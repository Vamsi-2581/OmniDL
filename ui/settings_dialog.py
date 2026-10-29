"""Settings dialog — merged from FireDM/Persepolis settings panels.

Provides:
- General: download dir, concurrent downloads, themes
- Network: proxy, speed limit, aria2c toggle
- Browser: intercept file types, extension port
- Categories: auto-assign file categories
- Scheduler: speed profiles, post-completion actions
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QCheckBox, QSpinBox, QTabWidget,
    QWidget, QFormLayout, QFileDialog, QGroupBox, QTextEdit,
    QSlider, QFrame
)
from PyQt6.QtCore import Qt

from core.config import (
    get_config, set_config, check_aria2c_available,
    DEFAULT_DOWNLOAD_DIR
)


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("⚙️ OmniDL Pro Settings")
        self.setMinimumSize(620, 520)
        self.setModal(True)
        self._init_ui()
        self._load_current()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        hdr = QLabel("⚙️ Settings")
        hdr.setStyleSheet("font-size: 18px; font-weight: 700; color: #58a6ff;")
        layout.addWidget(hdr)

        # Tab Widget
        self.tabs = QTabWidget()
        self.tabs.addTab(self._create_general_tab(), "📂 General")
        self.tabs.addTab(self._create_network_tab(), "🌐 Network")
        self.tabs.addTab(self._create_engine_tab(), "⚡ Engine")
        self.tabs.addTab(self._create_browser_tab(), "🔗 Browser")
        self.tabs.addTab(self._create_advanced_tab(), "🔧 Advanced")
        layout.addWidget(self.tabs)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_cancel = QPushButton("Cancel")
        btn_cancel.setProperty("class", "btn-secondary")
        btn_cancel.clicked.connect(self.reject)
        btn_row.addWidget(btn_cancel)

        btn_save = QPushButton("💾 Save Settings")
        btn_save.setProperty("class", "btn-primary")
        btn_save.clicked.connect(self._save_settings)
        btn_row.addWidget(btn_save)
        layout.addLayout(btn_row)

    def _create_general_tab(self):
        w = QWidget()
        form = QFormLayout(w)
        form.setSpacing(14)

        # Download directory
        dir_row = QHBoxLayout()
        self.dir_input = QLineEdit()
        btn_browse = QPushButton("📁")
        btn_browse.setProperty("class", "btn-secondary")
        btn_browse.clicked.connect(self._browse_dir)
        dir_row.addWidget(self.dir_input)
        dir_row.addWidget(btn_browse)
        form.addRow("Download folder:", dir_row)

        # Concurrent downloads
        self.spin_concurrent = QSpinBox()
        self.spin_concurrent.setRange(1, 10)
        form.addRow("Max concurrent downloads:", self.spin_concurrent)

        # Default quality
        self.combo_quality = QComboBox()
        self.combo_quality.addItem("🎬 Best Quality", "best")
        self.combo_quality.addItem("🔥 1080p", "1080p")
        self.combo_quality.addItem("⚡ 720p", "720p")
        self.combo_quality.addItem("📺 480p", "480p")
        self.combo_quality.addItem("🎵 Audio MP3", "mp3")
        form.addRow("Default quality:", self.combo_quality)

        # Clipboard sniffer
        self.chk_clipboard = QCheckBox("Enable clipboard video link detection")
        form.addRow("", self.chk_clipboard)

        # Sound on complete
        self.chk_sound = QCheckBox("Play sound when download completes")
        form.addRow("", self.chk_sound)

        # Auto start sniffed
        self.chk_auto_start = QCheckBox("Auto-start sniffed downloads (no dialog)")
        form.addRow("", self.chk_auto_start)

        # Playlist support
        self.chk_playlist = QCheckBox("Enable playlist/batch downloads")
        form.addRow("", self.chk_playlist)

        self.spin_playlist_max = QSpinBox()
        self.spin_playlist_max.setRange(1, 500)
        form.addRow("Max playlist items:", self.spin_playlist_max)

        return w

    def _create_network_tab(self):
        w = QWidget()
        form = QFormLayout(w)
        form.setSpacing(14)

        # Proxy (Persepolis-style)
        proxy_group = QGroupBox("🔒 Proxy Settings")
        proxy_layout = QFormLayout(proxy_group)

        self.chk_proxy = QCheckBox("Enable proxy")
        proxy_layout.addRow("", self.chk_proxy)

        self.combo_proxy_type = QComboBox()
        self.combo_proxy_type.addItem("HTTP", "http")
        self.combo_proxy_type.addItem("HTTPS", "https")
        self.combo_proxy_type.addItem("SOCKS5", "socks5")
        proxy_layout.addRow("Proxy type:", self.combo_proxy_type)

        self.proxy_host = QLineEdit()
        self.proxy_host.setPlaceholderText("e.g. 127.0.0.1")
        proxy_layout.addRow("Host:", self.proxy_host)

        self.proxy_port = QLineEdit()
        self.proxy_port.setPlaceholderText("e.g. 8080")
        proxy_layout.addRow("Port:", self.proxy_port)

        self.proxy_user = QLineEdit()
        self.proxy_user.setPlaceholderText("(optional)")
        proxy_layout.addRow("Username:", self.proxy_user)

        self.proxy_pass = QLineEdit()
        self.proxy_pass.setPlaceholderText("(optional)")
        self.proxy_pass.setEchoMode(QLineEdit.EchoMode.Password)
        proxy_layout.addRow("Password:", self.proxy_pass)

        form.addRow(proxy_group)

        # Speed limit (FireDM-style)
        speed_group = QGroupBox("⏱️ Speed Throttling")
        speed_layout = QFormLayout(speed_group)

        self.spin_speed = QSpinBox()
        self.spin_speed.setRange(0, 999999)
        self.spin_speed.setSuffix(" KB/s")
        self.spin_speed.setSpecialValueText("Unlimited")
        speed_layout.addRow("Download speed limit:", self.spin_speed)

        form.addRow(speed_group)

        return w

    def _create_engine_tab(self):
        w = QWidget()
        form = QFormLayout(w)
        form.setSpacing(14)

        # Concurrent fragments (IDM/PyIDM style)
        self.spin_fragments = QSpinBox()
        self.spin_fragments.setRange(1, 64)
        form.addRow("Concurrent fragments:", self.spin_fragments)

        # Aria2c integration (Persepolis feature)
        aria2_group = QGroupBox("🚀 Aria2c Accelerator")
        aria2_layout = QFormLayout(aria2_group)

        self.chk_aria2 = QCheckBox("Use aria2c as external downloader")
        aria2_available = check_aria2c_available()
        if not aria2_available:
            self.chk_aria2.setToolTip("aria2c not found in PATH. Install aria2 first.")
            self.chk_aria2.setEnabled(False)

        aria2_status = QLabel("✅ aria2c found" if aria2_available else "⚠️ aria2c not installed")
        aria2_status.setStyleSheet(f"color: {'#3fb950' if aria2_available else '#d29922'}; font-size: 11px;")
        aria2_layout.addRow("", self.chk_aria2)
        aria2_layout.addRow("Status:", aria2_status)

        self.spin_aria2_conns = QSpinBox()
        self.spin_aria2_conns.setRange(1, 64)
        aria2_layout.addRow("Connections per server:", self.spin_aria2_conns)

        self.spin_aria2_split = QSpinBox()
        self.spin_aria2_split.setRange(1, 64)
        aria2_layout.addRow("File split count:", self.spin_aria2_split)

        form.addRow(aria2_group)

        # Auto-retry (FireDM feature)
        retry_group = QGroupBox("🔄 Auto-Retry")
        retry_layout = QFormLayout(retry_group)

        self.chk_auto_resume = QCheckBox("Auto-resume broken downloads")
        retry_layout.addRow("", self.chk_auto_resume)

        self.spin_retry_count = QSpinBox()
        self.spin_retry_count.setRange(0, 20)
        retry_layout.addRow("Retry attempts:", self.spin_retry_count)

        self.spin_retry_delay = QSpinBox()
        self.spin_retry_delay.setRange(1, 120)
        self.spin_retry_delay.setSuffix(" sec")
        retry_layout.addRow("Retry delay:", self.spin_retry_delay)

        form.addRow(retry_group)

        return w

    def _create_browser_tab(self):
        w = QWidget()
        form = QFormLayout(w)
        form.setSpacing(14)

        # Browser intercept
        self.chk_browser_intercept = QCheckBox("Enable browser download interception")
        form.addRow("", self.chk_browser_intercept)

        # Intercepted file types
        self.intercept_types = QTextEdit()
        self.intercept_types.setFixedHeight(80)
        self.intercept_types.setPlaceholderText(".mp4,.mkv,.mp3,.zip,.exe,.pdf ...")
        form.addRow("Intercept file types\n(comma-separated):", self.intercept_types)

        # Bridge port info
        info_lbl = QLabel(
            "The OmniDL bridge server runs on 127.0.0.1:48911.\n"
            "Chrome/Edge extension communicates via this loopback port.\n"
            "Context menu 'Download via OmniDL' sends the link here."
        )
        info_lbl.setStyleSheet("color: #8b949e; font-size: 11px;")
        info_lbl.setWordWrap(True)
        form.addRow(info_lbl)

        return w

    def _create_advanced_tab(self):
        w = QWidget()
        form = QFormLayout(w)
        form.setSpacing(14)

        # On-complete action (Persepolis feature)
        self.combo_complete_action = QComboBox()
        self.combo_complete_action.addItem("Do nothing", "none")
        self.combo_complete_action.addItem("Show notification", "notify")
        self.combo_complete_action.addItem("Shutdown computer", "shutdown")
        self.combo_complete_action.addItem("Sleep/Hibernate", "sleep")
        form.addRow("After all downloads:", self.combo_complete_action)

        # Category auto-assign
        self.chk_category = QCheckBox("Auto-categorize downloads by file type")
        form.addRow("", self.chk_category)

        return w

    def _browse_dir(self):
        chosen = QFileDialog.getExistingDirectory(self, "Select Download Directory", self.dir_input.text())
        if chosen:
            self.dir_input.setText(chosen)

    def _load_current(self):
        """Load current config into UI controls."""
        self.dir_input.setText(get_config("download_dir", DEFAULT_DOWNLOAD_DIR))
        self.spin_concurrent.setValue(get_config("max_concurrent_downloads", 3))
        self.chk_clipboard.setChecked(get_config("clipboard_sniffing", True))
        self.chk_sound.setChecked(get_config("sound_on_complete", True))
        self.chk_auto_start.setChecked(get_config("auto_start_sniffed", False))
        self.chk_playlist.setChecked(get_config("playlist_support", True))
        self.spin_playlist_max.setValue(get_config("max_playlist_items", 50))

        # Default quality
        q = get_config("default_quality", "best")
        idx = self.combo_quality.findData(q)
        if idx >= 0:
            self.combo_quality.setCurrentIndex(idx)

        # Network
        self.chk_proxy.setChecked(get_config("proxy_enabled", False))
        pt = get_config("proxy_type", "http")
        idx = self.combo_proxy_type.findData(pt)
        if idx >= 0:
            self.combo_proxy_type.setCurrentIndex(idx)
        self.proxy_host.setText(get_config("proxy_host", ""))
        self.proxy_port.setText(get_config("proxy_port", ""))
        self.proxy_user.setText(get_config("proxy_user", ""))
        self.proxy_pass.setText(get_config("proxy_pass", ""))

        speed_kb = get_config("speed_limit", 0)
        self.spin_speed.setValue(speed_kb // 1024 if speed_kb else 0)

        # Engine
        self.spin_fragments.setValue(get_config("concurrent_fragments", 16))
        self.chk_aria2.setChecked(get_config("use_aria2c", False))
        self.spin_aria2_conns.setValue(get_config("aria2c_connections", 16))
        self.spin_aria2_split.setValue(get_config("aria2c_split", 16))
        self.chk_auto_resume.setChecked(get_config("auto_resume", True))
        self.spin_retry_count.setValue(get_config("auto_retry_count", 3))
        self.spin_retry_delay.setValue(get_config("auto_retry_delay", 5))

        # Browser
        self.chk_browser_intercept.setChecked(get_config("browser_intercept_enabled", True))
        self.intercept_types.setPlainText(get_config("intercept_file_types", ""))

        # Advanced
        ca = get_config("download_on_complete_action", "none")
        idx = self.combo_complete_action.findData(ca)
        if idx >= 0:
            self.combo_complete_action.setCurrentIndex(idx)
        self.chk_category.setChecked(get_config("category_auto_assign", True))

    def _save_settings(self):
        """Save all settings back to config."""
        set_config("download_dir", self.dir_input.text().strip() or DEFAULT_DOWNLOAD_DIR)
        set_config("max_concurrent_downloads", self.spin_concurrent.value())
        set_config("default_quality", self.combo_quality.currentData() or "best")
        set_config("clipboard_sniffing", self.chk_clipboard.isChecked())
        set_config("sound_on_complete", self.chk_sound.isChecked())
        set_config("auto_start_sniffed", self.chk_auto_start.isChecked())
        set_config("playlist_support", self.chk_playlist.isChecked())
        set_config("max_playlist_items", self.spin_playlist_max.value())

        # Network
        set_config("proxy_enabled", self.chk_proxy.isChecked())
        set_config("proxy_type", self.combo_proxy_type.currentData() or "http")
        set_config("proxy_host", self.proxy_host.text().strip())
        set_config("proxy_port", self.proxy_port.text().strip())
        set_config("proxy_user", self.proxy_user.text().strip())
        set_config("proxy_pass", self.proxy_pass.text().strip())

        speed_kb = self.spin_speed.value()
        set_config("speed_limit", speed_kb * 1024 if speed_kb > 0 else 0)

        # Engine
        set_config("concurrent_fragments", self.spin_fragments.value())
        set_config("use_aria2c", self.chk_aria2.isChecked())
        set_config("aria2c_connections", self.spin_aria2_conns.value())
        set_config("aria2c_split", self.spin_aria2_split.value())
        set_config("auto_resume", self.chk_auto_resume.isChecked())
        set_config("auto_retry_count", self.spin_retry_count.value())
        set_config("auto_retry_delay", self.spin_retry_delay.value())

        # Browser
        set_config("browser_intercept_enabled", self.chk_browser_intercept.isChecked())
        set_config("intercept_file_types", self.intercept_types.toPlainText().strip())

        # Advanced
        set_config("download_on_complete_action", self.combo_complete_action.currentData() or "none")
        set_config("category_auto_assign", self.chk_category.isChecked())

        self.accept()
