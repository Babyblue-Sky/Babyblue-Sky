// Double-click a single word -> save as "word"
document.addEventListener("dblclick", (e) => {
  const selection = window.getSelection().toString().trim();
  if (!/^[A-Za-z][A-Za-z'-]*$/.test(selection)) return; // must look like an actual word, not a stray symbol/number
  captureAndShow(selection, "word", e.pageX, e.pageY);
});

// Ctrl+Shift+S / Cmd+Shift+S (relayed from background.js) -> save selection as "idiom"
chrome.runtime.onMessage.addListener((msg) => {
  if (msg.action === "save-phrase") {
    const selection = window.getSelection().toString().trim();
    if (!selection) return;
    const range = window.getSelection().getRangeAt(0).getBoundingClientRect();
    captureAndShow(selection, "idiom", range.left + window.scrollX, range.bottom + window.scrollY);
  }
});

function captureAndShow(text, type, x, y) {
  showBubble(text, type, x, y, "Saving...", null);

  chrome.runtime.sendMessage({ action: "capture", text, type }, (response) => {
    if (chrome.runtime.lastError) {
      showBubble(text, type, x, y, "Connection error — try again.", null);
      return;
    }
    if (response.error) {
      showBubble(text, type, x, y, "Couldn't save: " + response.error, null);
      return;
    }
    showBubble(text, type, x, y, response.definition, response.example, response.audioUrl, response.status);
  });
}

function showBubble(word, type, x, y, message, example, audioUrl, status) {
  const existing = document.getElementById("vocab-bubble");
  if (existing) existing.remove();

  const bubble = document.createElement("div");
  bubble.id = "vocab-bubble";
  bubble.innerHTML = `
    <span id="vocab-close">✕</span>
    <div class="vocab-type">${type}</div>
    <div class="vocab-word">${word}${audioUrl ? ' <button id="vocab-audio">🔊</button>' : ""}</div>
    <div class="vocab-msg">${message}</div>
    ${example ? `<div class="vocab-example">${example}</div>` : ""}
    ${status ? `<div class="vocab-status">${status === "duplicate" ? "Already in your Word Bank — refreshed date" : "Saved to Word Bank ✓"}</div>` : ""}
  `;
  bubble.style.left = `${x}px`;
  bubble.style.top = `${y + 16}px`;
  document.body.appendChild(bubble);

  document.getElementById("vocab-close").onclick = () => bubble.remove();
  if (audioUrl) {
    document.getElementById("vocab-audio").onclick = () => new Audio(audioUrl).play();
  }
}
