import os
import sys
import time
import statistics
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

os.environ["QT_QPA_PLATFORM"] = "offscreen"

from core.clipboard_sniffer import is_video_url
from core.config import get_config

TEST_URLS = [
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "https://youtu.be/dQw4w9WgXcQ",
    "https://www.youtube.com/shorts/abc123XYZ",
    "https://www.facebook.com/reel/1234567890",
    "https://www.facebook.com/watch/?v=987654321",
    "https://fb.watch/xyz123/",
    "https://www.instagram.com/reel/CxY12345678/",
    "https://www.tiktok.com/@user/video/7123456789012345678",
    "https://twitter.com/user/status/1234567890123456789",
    "https://x.com/user/status/1234567890123456789",
    "https://vimeo.com/123456789",
    "https://reddit.com/r/videos/comments/xyz123/cool_video/",
    "https://example.com/media/sample_video.mp4",
    "https://cdn.site.org/stream/index.m3u8",
    "https://files.test.com/audio/track.mp3",
    "https://www.google.com/search?q=python",
    "https://en.wikipedia.org/wiki/Computer",
    "https://github.com/torvalds/linux",
    "Some non-url text snippet",
    "http://example.com/index.html"
]

def bench_regex_throughput(iterations=10000):
    start = time.perf_counter()
    count = 0
    for _ in range(iterations):
        for u in TEST_URLS:
            is_video_url(u)
            count += 1
    duration = time.perf_counter() - start
    ops_per_sec = count / duration
    return ops_per_sec, duration

def bench_app_init():
    from PyQt6.QtWidgets import QApplication
    from ui.main_window import MainWindow

    times = []
    app = QApplication.instance() or QApplication(sys.argv)
    for _ in range(5):
        t0 = time.perf_counter()
        w = MainWindow()
        t1 = time.perf_counter()
        times.append((t1 - t0) * 1000) # ms
        w.close()
    return statistics.median(times)

def main():
    if sys.stdout.encoding.lower() != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
    print("=" * 60)
    print("[BENCHMARK] OmniDL Pro Benchmark Suite")
    print("=" * 60)

    # 1. Regex Sniffer Speed
    ops_sec, dur = bench_regex_throughput(5000)
    print(f"[*] Regex URL Evaluation: {ops_sec:,.0f} URLs/sec (Evaluated 100,000 URLs in {dur:.2f}s)")

    # 2. GUI Window Init Latency
    median_init_ms = bench_app_init()
    print(f"[*] GUI Window Init Latency: {median_init_ms:.1f} ms")

    print("=" * 60)
    return {
        "regex_ops_sec": ops_sec,
        "gui_init_ms": median_init_ms
    }

if __name__ == "__main__":
    main()
