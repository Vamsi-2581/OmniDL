// Content script to render IDM-style floating download bar
let latestStream = null;
let streamCount = 0;
let floatingBar = null;

chrome.runtime.onMessage.addListener((msg) => {
  if (msg.action === "stream_detected") {
    latestStream = msg.stream;
    streamCount = msg.count || 1;
    showFloatingBar();
  }
});

function showFloatingBar() {
  if (!floatingBar) {
    floatingBar = document.createElement("div");
    floatingBar.id = "omnidl-floating-panel";
    floatingBar.innerHTML = `
      <div class="omnidl-btn-main" id="omnidl-trigger">
        <span class="omnidl-icon">⚡</span>
        <span class="omnidl-text">Download Video (${streamCount})</span>
      </div>
      <button class="omnidl-close" id="omnidl-close" title="Dismiss">×</button>
    `;
    document.body.appendChild(floatingBar);

    document.getElementById("omnidl-trigger").addEventListener("click", () => {
      if (latestStream) {
        chrome.runtime.sendMessage({ action: "send_to_app", stream: latestStream }, (res) => {
          if (res && res.success) {
            flashNotice("Sent to OmniDL Pro! ⚡");
          } else {
            flashNotice("Open OmniDL Pro app to download!");
          }
        });
      }
    });

    document.getElementById("omnidl-close").addEventListener("click", (e) => {
      e.stopPropagation();
      floatingBar.style.display = "none";
    });
  } else {
    floatingBar.style.display = "flex";
    const txt = floatingBar.querySelector(".omnidl-text");
    if (txt) txt.textContent = `Download Video (${streamCount})`;
  }
}

function flashNotice(msg) {
  const txt = floatingBar.querySelector(".omnidl-text");
  if (txt) {
    const orig = txt.textContent;
    txt.textContent = msg;
    setTimeout(() => {
      txt.textContent = orig;
    }, 2500);
  }
}
