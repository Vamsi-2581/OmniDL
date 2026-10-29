// In-memory captured streams: tabId -> array of stream objects
const capturedStreams = {};

const MEDIA_URL_REGEX = /\.(m3u8|mpd|mp4|webm|flv|ts)(\?.*)?$/i;
const IGNORE_PATTERNS = [
  /google-analytics\.com/,
  /doubleclick\.net/,
  /\.ts\?.*frag=/i, // repetitive ts fragments
  /segment[0-9]+\.ts/i
];

chrome.webRequest.onBeforeSendHeaders.addListener(
  (details) => {
    const { url, tabId, requestHeaders, type } = details;

    if (tabId <= 0) return;

    // Filter media
    const isMedia = (type === "media") || MEDIA_URL_REGEX.test(url);
    if (!isMedia) return;

    // Check ignore patterns
    for (const pat of IGNORE_PATTERNS) {
      if (pat.test(url)) return;
    }

    // Extract headers: Referer, Origin, User-Agent
    const headers = {};
    if (requestHeaders) {
      for (const h of requestHeaders) {
        const name = h.name.toLowerCase();
        if (name === "referer") headers["Referer"] = h.value;
        if (name === "origin") headers["Origin"] = h.value;
        if (name === "user-agent") headers["User-Agent"] = h.value;
      }
    }

    if (!capturedStreams[tabId]) {
      capturedStreams[tabId] = [];
    }

    // Check duplicate URL
    const existing = capturedStreams[tabId].find((s) => s.url === url);
    if (existing) return;

    // Get tab info
    chrome.tabs.get(tabId, (tab) => {
      if (chrome.runtime.lastError || !tab) return;

      let formatType = "MP4 / Media";
      if (url.includes(".m3u8")) formatType = "HLS Stream (m3u8)";
      else if (url.includes(".mpd")) formatType = "DASH Stream (mpd)";

      const streamItem = {
        id: Math.random().toString(36).substring(2, 9),
        url: url,
        title: tab.title || "Video Stream",
        pageUrl: tab.url,
        formatType: formatType,
        headers: headers,
        timestamp: Date.now()
      };

      capturedStreams[tabId].push(streamItem);

      // Update badge
      const count = capturedStreams[tabId].length;
      chrome.action.setBadgeText({ text: count.toString(), tabId: tabId });
      chrome.action.setBadgeBackgroundColor({ color: "#238636", tabId: tabId });

      // Notify content script on page
      chrome.tabs.sendMessage(tabId, {
        action: "stream_detected",
        stream: streamItem,
        count: count
      }).catch(() => {});
    });
  },
  { urls: ["<all_urls>"] },
  ["requestHeaders", "extraHeaders"]
);

// Clean up when tab is closed
chrome.tabs.onRemoved.addListener((tabId) => {
  delete capturedStreams[tabId];
});

// Messages from popup or content script
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.action === "get_streams") {
    const tabId = msg.tabId;
    sendResponse({ streams: capturedStreams[tabId] || [] });
  } else if (msg.action === "send_to_app") {
    sendStreamToApp(msg.stream)
      .then((res) => sendResponse(res))
      .catch((err) => sendResponse({ success: false, error: err.message }));
    return true; // async response
  }
});

async function sendStreamToApp(stream) {
  try {
    const resp = await fetch("http://127.0.0.1:48911/download", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        url: stream.url,
        title: stream.title,
        pageUrl: stream.pageUrl,
        headers: stream.headers
      })
    });
    if (!resp.ok) {
      throw new Error(`OmniDL app returned HTTP ${resp.status}`);
    }
    return await resp.json();
  } catch (e) {
    throw new Error("Could not reach OmniDL Pro app. Make sure it is running.");
  }
}
