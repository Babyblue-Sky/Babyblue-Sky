importScripts("config.js");

chrome.commands.onCommand.addListener((command) => {
  if (command === "save-phrase") {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (tabs[0]) chrome.tabs.sendMessage(tabs[0].id, { action: "save-phrase" });
    });
  }
});

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.action !== "capture") return false;
  saveWord(msg.text, msg.type)
    .then((result) => sendResponse(result))
    .catch((err) => sendResponse({ error: String((err && err.message) || err) }));
  return true; // keep the message channel open for the async response above
});

// ---------- DICTIONARY LOOKUP (Merriam-Webster only — the Claude fallback for
// idioms/unresolved words runs server-side in the weekly/monthly GitHub
// Action, so that API key never has to live in this extension) ----------

async function fetchMW(word, dict, key) {
  const url = `https://dictionaryapi.com/api/v3/references/${dict}/json/${encodeURIComponent(word)}?key=${encodeURIComponent(key)}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Merriam-Webster lookup failed: ${res.status}`);
  return res.json();
}

function isUsableMWEntry(json) {
  return Array.isArray(json) && json.length > 0 && typeof json[0] === "object" && json[0].meta;
}

function extractAudioUrl(entry) {
  try {
    const audio = entry.hwi.prs[0].sound.audio;
    const subdir = audio.indexOf("bix") === 0 ? "bix"
      : audio.indexOf("gg") === 0 ? "gg"
      : /^[0-9]/.test(audio) ? "number"
      : audio.charAt(0);
    return `https://media.merriam-webster.com/audio/prons/en/us/mp3/${subdir}/${audio}.mp3`;
  } catch (e) {
    return "";
  }
}

async function lookupMerriamWebster(word) {
  let json = await fetchMW(word, "learners", MW_LEARNERS_KEY);
  let usedLearners = isUsableMWEntry(json);

  if (!usedLearners) {
    json = await fetchMW(word, "collegiate", MW_COLLEGIATE_KEY);
  }
  if (!isUsableMWEntry(json)) return null;

  const entry = json[0];
  const definition = (entry.shortdef && entry.shortdef[0]) || "";

  let example = "";
  try {
    const vis = entry.def[0].sseq[0][0][1].dt.find((d) => d[0] === "vis");
    if (vis) example = vis[1][0].t.replace(/\{it\}|\{\/it\}/g, "");
  } catch (e) { /* no example available */ }

  let audioUrl = extractAudioUrl(entry);
  if (!audioUrl && usedLearners) {
    const collegiateJson = await fetchMW(word, "collegiate", MW_COLLEGIATE_KEY);
    if (isUsableMWEntry(collegiateJson)) audioUrl = extractAudioUrl(collegiateJson[0]);
  }

  return { definition, example, audioUrl };
}

// ---------- SAVE TO GITHUB (this repo IS the database) ----------

async function githubGetFile() {
  const url = `https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/contents/${GITHUB_DATA_PATH}?ref=${GITHUB_BRANCH}`;
  const res = await fetch(url, {
    headers: { Authorization: `Bearer ${GITHUB_TOKEN}`, Accept: "application/vnd.github+json" }
  });
  if (!res.ok) throw new Error(`GitHub read failed (${res.status}): ${await res.text()}`);
  const data = await res.json();
  const words = JSON.parse(decodeURIComponent(escape(atob(data.content))));
  return { words, sha: data.sha };
}

async function githubPutFile(words, sha, message) {
  const url = `https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/contents/${GITHUB_DATA_PATH}`;
  const body = {
    message,
    content: btoa(unescape(encodeURIComponent(JSON.stringify(words, null, 2) + "\n"))),
    sha,
    branch: GITHUB_BRANCH
  };
  const res = await fetch(url, {
    method: "PUT",
    headers: { Authorization: `Bearer ${GITHUB_TOKEN}`, Accept: "application/vnd.github+json", "content-type": "application/json" },
    body: JSON.stringify(body)
  });
  if (!res.ok) throw new Error(`GitHub write failed (${res.status}): ${await res.text()}`);
}

// Saving is a read-modify-write against a single shared file, so if two
// captures race, the second PUT's `sha` goes stale and GitHub rejects it
// (409). Re-reading and retrying a couple of times covers that without the
// user noticing.
async function saveWord(text, type) {
  let lastErr;
  for (let attempt = 0; attempt < 3; attempt++) {
    try {
      return await trySaveWord(text, type);
    } catch (err) {
      lastErr = err;
      if (!String(err.message).includes("409")) throw err;
    }
  }
  throw lastErr;
}

async function trySaveWord(text, type) {
  const { words, sha } = await githubGetFile();
  const now = new Date().toISOString();
  const existing = words.find((w) => w.word.toLowerCase() === text.toLowerCase());

  if (existing) {
    existing.dateSaved = now;
    await githubPutFile(words, sha, `Refresh: ${text}`);
    return { status: "duplicate", word: existing.word, definition: existing.definition, example: existing.example, audioUrl: existing.audioUrl };
  }

  let lookup = null;
  if (type !== "idiom") {
    try {
      lookup = await lookupMerriamWebster(text);
    } catch (e) {
      console.warn("MW lookup failed, saving without a definition:", e);
    }
  }

  const entry = {
    word: text,
    type,
    definition: lookup ? lookup.definition : "",
    example: lookup ? lookup.example : "",
    audioUrl: lookup ? lookup.audioUrl || "" : "",
    dateSaved: now,
    firstSaved: now,
    reviewedIn: []
  };
  words.push(entry);
  await githubPutFile(words, sha, `Add: ${text}`);

  return {
    status: "saved",
    word: entry.word,
    definition: entry.definition || "Saved — definition will be filled in before your next review.",
    example: entry.example,
    audioUrl: entry.audioUrl
  };
}
