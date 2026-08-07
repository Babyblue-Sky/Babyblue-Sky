// One-time setup — fill these in, then reload the extension
// (chrome://extensions -> the reload icon on this extension's card).
//
// This file is only loaded by background.js (the service worker), never by
// content.js — so these values never get injected into the pages you browse.

// Merriam-Webster dictionary keys (same ones from the old setup — Learner's +
// Collegiate). Free at dictionaryapi.com/register/index.
const MW_LEARNERS_KEY = "PASTE_YOUR_MW_LEARNERS_KEY";
const MW_COLLEGIATE_KEY = "PASTE_YOUR_MW_COLLEGIATE_KEY";

// A GitHub fine-grained personal access token, scoped to ONLY this repo with
// "Contents: Read and write" permission. Create one at
// github.com/settings/tokens?type=beta
const GITHUB_TOKEN = "PASTE_A_FINE_GRAINED_GITHUB_TOKEN";
const GITHUB_OWNER = "Babyblue-Sky";
const GITHUB_REPO = "Babyblue-Sky";
const GITHUB_BRANCH = "main";
const GITHUB_DATA_PATH = "vocab-review-agent/data/words.json";
