document.addEventListener("DOMContentLoaded", async () => {
  const statusEl = document.getElementById("app-status");
  const container = document.getElementById("streams-container");

  // 1. Check OmniDL Pro Desktop App status via local bridge
  try {
    const res = await fetch("http://127.0.0.1:48911/status");
    if (res.ok) {
      statusEl.textContent = "🟢 App Online";
      statusEl.className = "status-pill online";
    } else {
      throw new Error();
    }
  } catch (e) {
    statusEl.textContent = "🔴 App Offline";
    statusEl.className = "status-pill offline";
  }

  // 2. Query active tab
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab) return;

  // 3. Request captured streams from background script
  chrome.runtime.sendMessage({ action: "get_streams", tabId: tab.id }, (response) => {
    const streams = (response && response.streams) || [];
    renderStreams(streams);
  });

  function renderStreams(streams) {
    if (streams.length === 0) {
      container.innerHTML = `
        <div class="empty-state">
          No video streams detected yet.<br><br>
          Play the video on <b>${tab.title || "this page"}</b> to capture it!
        </div>
      `;
      return;
    }

    container.innerHTML = "";
    streams.forEach((stream) => {
      const card = document.createElement("div");
      card.className = "stream-card";
      card.innerHTML = `
        <div class="stream-title">${escapeHtml(stream.title)}</div>
        <span class="stream-badge">${escapeHtml(stream.formatType)}</span>
        <div class="stream-url" title="${escapeHtml(stream.url)}">${escapeHtml(stream.url)}</div>
        <div class="btn-row">
          <button class="btn-dl" data-id="${stream.id}">⚡ Download with OmniDL</button>
          <button class="btn-copy" data-url="${escapeHtml(stream.url)}">📋 Copy Link</button>
        </div>
      `;

      // Download button
      card.querySelector(".btn-dl").addEventListener("click", () => {
        chrome.runtime.sendMessage({ action: "send_to_app", stream }, (res) => {
          if (res && res.success) {
            const btn = card.querySelector(".btn-dl");
            btn.textContent = "✅ Sent to OmniDL!";
            setTimeout(() => {
              btn.textContent = "⚡ Download with OmniDL";
            }, 2000);
          } else {
            alert("Could not reach OmniDL Pro. Please make sure the desktop app is open!");
          }
        });
      });

      // Copy button
      card.querySelector(".btn-copy").addEventListener("click", (e) => {
        navigator.clipboard.writeText(stream.url);
        e.target.textContent = "Copied!";
        setTimeout(() => {
          e.target.textContent = "📋 Copy Link";
        }, 1500);
      });

      container.appendChild(card);
    });
  }

  function escapeHtml(str) {
    if (!str) return "";
    return str.replace(/[&<>"']/g, (m) => ({
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#39;"
    }[m]));
  }
});
