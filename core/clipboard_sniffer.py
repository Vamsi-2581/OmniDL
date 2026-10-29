import re
import time
from PyQt6.QtCore import QObject, pyqtSignal, QThread
from PyQt6.QtWidgets import QApplication
from core.config import get_config

# Common media domains & extensions
MEDIA_PATTERNS = [
    r'https?://(?:www\.)?youtube\.com/(?:watch\?v=|shorts/|live/|playlist\?|clip/)[^\s]+',
    r'https?://youtu\.be/[^\s]+',
    r'https?://(?:www\.|m\.|web\.)?facebook\.com/(?:reel/|watch/?\?v=|videos/|share/v/|share/r/)[^\s]+',
    r'https?://fb\.watch/[^\s]+',
    r'https?://(?:www\.)?instagram\.com/(?:reel/|p/|tv/)[^\s]+',
    r'https?://(?:www\.|vm\.|vt\.)?tiktok\.com/[^\s]+',
    r'https?://(?:www\.)?(?:twitter\.com|x\.com)/[a-zA-Z0-9_]+/status/[0-9]+[^\s]*',
    r'https?://(?:www\.)?reddit\.com/r/[^\s]+/comments/[^\s]+',
    r'https?://(?:www\.)?vimeo\.com/[0-9]+[^\s]*',
    r'https?://(?:www\.)?dailymotion\.com/video/[^\s]+',
    r'https?://(?:www\.)?bilibili\.com/video/[^\s]+',
    r'https?://(?:www\.)?twitch\.tv/videos/[0-9]+[^\s]*',
    r'https?://(?:www\.)?pinterest\.com/pin/[^\s]+',
    r'https?://[^\s]+\.(?:mp4|mkv|webm|flv|mov|avi|ts|m3u8|mpd|mp3|m4a|aac)(?:\?[^\s]*)?$',
]

COMPILED_PATTERNS = [re.compile(p, re.IGNORECASE) for p in MEDIA_PATTERNS]

def is_video_url(text):
    if not text or len(text) > 2048 or not text.startswith("http"):
        return False
    text = text.strip()
    for pattern in COMPILED_PATTERNS:
        if pattern.search(text):
            return True
    return False

class ClipboardSniffer(QObject):
    """Monitors system clipboard using PyQt's QApplication clipboard changed signal."""
    video_url_detected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.last_clipboard_text = ""
        self.recent_seen = set()
        self.enabled = get_config("clipboard_sniffing", True)

    def start(self):
        clip = QApplication.clipboard()
        clip.dataChanged.connect(self._on_clipboard_changed)

    def set_enabled(self, val):
        self.enabled = bool(val)

    def _on_clipboard_changed(self):
        if not self.enabled:
            return

        try:
            clip = QApplication.clipboard()
            text = clip.text().strip()
            
            if not text or text == self.last_clipboard_text:
                return
            
            self.last_clipboard_text = text

            if text in self.recent_seen:
                return

            if is_video_url(text):
                self.recent_seen.add(text)
                if len(self.recent_seen) > 100:
                    self.recent_seen.pop()
                self.video_url_detected.emit(text)
        except Exception as e:
            print(f"[Clipboard Monitor Error] {e}")
