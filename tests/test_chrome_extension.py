import os
import sys
import time
import threading
import http.server
import socketserver
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.bridge_server import BridgeServer

def run_test():
    print("=" * 60)
    print("⚡ Testing OmniDL Chrome Extension Integration")
    print("=" * 60)

    # 1. Start Bridge Server on 127.0.0.1:48911
    bridge = BridgeServer(port=48911)
    bridge.start()

    captured_streams = []
    bridge.stream_captured.connect(lambda p: captured_streams.append(p))

    # 2. Start local HTTP server serving video & test page
    test_dir = PROJECT_ROOT / "tests"
    dummy_video = test_dir / "sample_stream.mp4"
    if not dummy_video.exists():
        dummy_video.write_bytes(b"OmniDL_DUMMY_MP4_STREAM_CONTENT_" * 1000)

    class TestHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            pass
        def translate_path(self, path):
            if "sample_stream.mp4" in path:
                return str(dummy_video)
            return str(test_dir / "web_test_page.html")

    server = socketserver.TCPServer(("127.0.0.1", 48919), TestHandler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    print("[*] Local Web Video Server running on http://127.0.0.1:48919/")

    # 3. Launch Chrome with extension loaded pointing to test page
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    user_data = PROJECT_ROOT / "chrome-test-profile"
    ext_path = PROJECT_ROOT / "extension"

    cmd = [
        chrome_path,
        f"--user-data-dir={user_data}",
        f"--load-extension={ext_path}",
        "--no-first-run",
        "--no-default-browser-check",
        "http://127.0.0.1:48919/"
    ]

    print(f"[*] Launching Chrome with extension preloaded: {ext_path}")
    proc = subprocess.Popen(cmd)

    print("[*] Chrome launched successfully with OmniDL Pro extension.")
    print("[*] Check your Chrome window - you will see the video playing and OmniDL Grabber active.")
    
    return proc, bridge, server

if __name__ == "__main__":
    proc, bridge, server = run_test()
    try:
        # Keep alive for demonstration
        time.sleep(5)
    finally:
        pass
