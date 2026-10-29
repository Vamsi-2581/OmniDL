import os
import json
from pathlib import Path

DEFAULT_DOWNLOAD_DIR = str(Path.home() / "Downloads" / "OmniDownloads")
CONFIG_DIR = Path.home() / ".omni_downloader"
CONFIG_FILE = CONFIG_DIR / "config.json"
HISTORY_FILE = CONFIG_DIR / "history.json"
SCHEDULE_FILE = CONFIG_DIR / "schedules.json"
CATEGORIES_FILE = CONFIG_DIR / "categories.json"

DEFAULT_CONFIG = {
    "download_dir": DEFAULT_DOWNLOAD_DIR,
    "max_concurrent_downloads": 3,
    "concurrent_fragments": 16,  # Multi-threaded segment acceleration (IDM style)
    "clipboard_sniffing": True,
    "default_quality": "best",  # 'best', '1080p', '720p', '480p', 'mp3'
    "auto_start_sniffed": False,
    "notifications_enabled": True,
    "theme": "dark",
    # --- Merged from FireDM / Persepolis ---
    "use_aria2c": False,  # Use aria2c as external downloader when available
    "aria2c_connections": 16,  # Max connections per server (-x flag)
    "aria2c_split": 16,  # Split segments (-s flag)
    "speed_limit": 0,  # 0 = unlimited, otherwise bytes/sec
    "proxy_enabled": False,
    "proxy_type": "http",  # http, https, socks5
    "proxy_host": "",
    "proxy_port": "",
    "proxy_user": "",
    "proxy_pass": "",
    "auto_resume": True,  # Resume broken downloads automatically
    "auto_retry_count": 3,
    "auto_retry_delay": 5,  # seconds
    "download_on_complete_action": "none",  # 'none', 'shutdown', 'sleep', 'notify'
    "sound_on_complete": True,
    "browser_intercept_enabled": True,
    "intercept_file_types": ".mp4,.mkv,.avi,.mov,.webm,.flv,.mp3,.wav,.flac,.aac,.ogg,.zip,.rar,.7z,.exe,.iso,.pdf,.torrent",
    "playlist_support": True,
    "max_playlist_items": 50,
    "category_auto_assign": True,
}

DEFAULT_CATEGORIES = {
    "Video": {
        "extensions": [".mp4", ".mkv", ".avi", ".mov", ".webm", ".flv", ".wmv", ".m4v", ".3gp"],
        "icon": "🎬",
        "folder": "Videos"
    },
    "Audio": {
        "extensions": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a", ".opus"],
        "icon": "🎵",
        "folder": "Audio"
    },
    "Documents": {
        "extensions": [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt", ".csv"],
        "icon": "📄",
        "folder": "Documents"
    },
    "Archives": {
        "extensions": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz"],
        "icon": "📦",
        "folder": "Archives"
    },
    "Programs": {
        "extensions": [".exe", ".msi", ".dmg", ".deb", ".rpm", ".apk", ".appimage"],
        "icon": "💿",
        "folder": "Programs"
    },
    "Images": {
        "extensions": [".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".bmp", ".ico"],
        "icon": "🖼️",
        "folder": "Images"
    },
    "Other": {
        "extensions": [],
        "icon": "📁",
        "folder": "Other"
    }
}


def ensure_dirs(download_dir=None):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    d = download_dir or DEFAULT_DOWNLOAD_DIR
    try:
        Path(d).mkdir(parents=True, exist_ok=True)
    except Exception:
        pass


def load_config():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not CONFIG_FILE.exists():
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            cfg = json.load(f)
            # Fill missing keys from default
            for k, v in DEFAULT_CONFIG.items():
                if k not in cfg:
                    cfg[k] = v
            return cfg
    except Exception:
        return DEFAULT_CONFIG.copy()


def save_config(cfg):
    ensure_dirs()
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=4)
    except Exception as e:
        print(f"[Config Error] Failed to save config: {e}")


_CURRENT_CONFIG = None


def get_config(key=None, default=None):
    global _CURRENT_CONFIG
    if _CURRENT_CONFIG is None:
        _CURRENT_CONFIG = load_config()
    if key is None:
        return _CURRENT_CONFIG
    return _CURRENT_CONFIG.get(key, default)


def set_config(key, value):
    global _CURRENT_CONFIG
    if _CURRENT_CONFIG is None:
        _CURRENT_CONFIG = load_config()
    _CURRENT_CONFIG[key] = value
    save_config(_CURRENT_CONFIG)


def load_history():
    ensure_dirs()
    if not HISTORY_FILE.exists():
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_history(history_list):
    ensure_dirs()
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history_list, f, indent=2)
    except Exception as e:
        print(f"[History Error] Failed to save history: {e}")


def load_categories():
    ensure_dirs()
    if not CATEGORIES_FILE.exists():
        save_categories(DEFAULT_CATEGORIES)
        return DEFAULT_CATEGORIES.copy()
    try:
        with open(CATEGORIES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return DEFAULT_CATEGORIES.copy()


def save_categories(cats):
    ensure_dirs()
    try:
        with open(CATEGORIES_FILE, "w", encoding="utf-8") as f:
            json.dump(cats, f, indent=2)
    except Exception:
        pass


def get_category_for_file(filename):
    """Auto-detect category from file extension (FireDM-style)."""
    cats = load_categories()
    ext = os.path.splitext(filename.lower())[1]
    for cat_name, cat_data in cats.items():
        if ext in cat_data.get("extensions", []):
            return cat_name, cat_data.get("icon", "📁")
    return "Other", "📁"


def load_schedules():
    ensure_dirs()
    if not SCHEDULE_FILE.exists():
        return []
    try:
        with open(SCHEDULE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_schedules(schedules):
    ensure_dirs()
    try:
        with open(SCHEDULE_FILE, "w", encoding="utf-8") as f:
            json.dump(schedules, f, indent=2)
    except Exception:
        pass


def get_proxy_url():
    """Build proxy URL from config (Persepolis-style)."""
    cfg = get_config()
    if not cfg.get("proxy_enabled"):
        return None
    ptype = cfg.get("proxy_type", "http")
    host = cfg.get("proxy_host", "").strip()
    port = cfg.get("proxy_port", "").strip()
    user = cfg.get("proxy_user", "").strip()
    pwd = cfg.get("proxy_pass", "").strip()
    if not host:
        return None
    auth = f"{user}:{pwd}@" if user else ""
    return f"{ptype}://{auth}{host}:{port}" if port else f"{ptype}://{auth}{host}"


def check_aria2c_available():
    """Check if aria2c binary is in PATH."""
    import shutil
    return shutil.which("aria2c") is not None
