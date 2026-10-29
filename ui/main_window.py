import os
import uuid
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QFrame, QFileDialog, QLineEdit,
    QMessageBox, QSystemTrayIcon, QMenu, QButtonGroup
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon, QAction

from core.config import get_config, set_config, load_history, save_history, get_category_for_file
from core.downloader import DownloadWorker
from core.clipboard_sniffer import ClipboardSniffer
from core.bridge_server import BridgeServer
from core.scheduler import DownloadScheduler
from ui.dialogs import AddDownloadDialog
from ui.task_widget import TaskWidget
from ui.settings_dialog import SettingsDialog
from ui.styles import MODERN_DARK_THEME


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("⚡ OmniDL Pro - Universal Turbo Video Downloader")
        self.resize(1020, 680)
        self.setMinimumSize(800, 520)

        # In-memory tasks
        self.tasks = {}       # task_id -> task_data dict
        self.widgets = {}     # task_id -> TaskWidget instance
        self.workers = {}     # task_id -> DownloadWorker instance
        self.current_filter = "all"

        self._init_ui()
        self._load_saved_history()
        self._init_clipboard_sniffer()
        self._init_bridge_server()
        self._init_scheduler()

        # Stats refresh timer
        self._stats_timer = QTimer(self)
        self._stats_timer.setInterval(2000)
        self._stats_timer.timeout.connect(self._update_stats)
        self._stats_timer.start()

    def _init_ui(self):
        self.setStyleSheet(MODERN_DARK_THEME)

        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Left Sidebar
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)
        side_layout = QVBoxLayout(sidebar)
        side_layout.setContentsMargins(0, 0, 0, 16)
        side_layout.setSpacing(4)

        # Brand Logo
        logo_lbl = QLabel("⚡ OmniDL Pro")
        logo_lbl.setObjectName("logoLabel")
        sub_logo = QLabel("Universal Video Grabber")
        sub_logo.setObjectName("logoSubLabel")
        side_layout.addWidget(logo_lbl)
        side_layout.addWidget(sub_logo)

        # Nav Buttons
        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)

        self.btn_nav_all = self._create_nav_btn("📥 All Downloads", "all", side_layout)
        self.btn_nav_active = self._create_nav_btn("⚡ Downloading", "active", side_layout)
        self.btn_nav_completed = self._create_nav_btn("✅ Completed", "completed", side_layout)
        self.btn_nav_queued = self._create_nav_btn("⏸️ Paused / Queued", "queued", side_layout)
        self.btn_nav_all.setChecked(True)

        side_layout.addStretch()

        # Stats panel
        stats_frame = QFrame()
        stats_frame.setStyleSheet("background-color: #21262d; border-radius: 8px; margin: 10px; padding: 10px;")
        stats_layout = QVBoxLayout(stats_frame)
        stats_layout.setSpacing(4)

        stats_title = QLabel("📊 Session Stats")
        stats_title.setStyleSheet("font-weight: 700; color: #58a6ff; font-size: 12px;")
        stats_layout.addWidget(stats_title)

        self.stats_active_lbl = QLabel("Active: 0")
        self.stats_active_lbl.setStyleSheet("color: #58a6ff; font-size: 11px;")
        stats_layout.addWidget(self.stats_active_lbl)

        self.stats_completed_lbl = QLabel("Completed: 0")
        self.stats_completed_lbl.setStyleSheet("color: #3fb950; font-size: 11px;")
        stats_layout.addWidget(self.stats_completed_lbl)

        self.stats_total_lbl = QLabel("Total: 0")
        self.stats_total_lbl.setStyleSheet("color: #8b949e; font-size: 11px;")
        stats_layout.addWidget(self.stats_total_lbl)

        side_layout.addWidget(stats_frame)

        # Sniffer Toggle in Sidebar
        sniff_frame = QFrame()
        sniff_frame.setStyleSheet("background-color: #21262d; border-radius: 8px; margin: 10px; padding: 10px;")
        sniff_layout = QVBoxLayout(sniff_frame)
        sniff_layout.setSpacing(6)

        sniff_title = QLabel("📋 Clipboard Sniffer")
        sniff_title.setStyleSheet("font-weight: 700; color: #58a6ff; font-size: 12px;")
        self.sniff_sub = QLabel("Auto-detect video links on Copy")
        self.sniff_sub.setStyleSheet("color: #8b949e; font-size: 10px;")
        self.sniff_sub.setWordWrap(True)

        self.btn_toggle_sniff = QPushButton("🟢 Sniffer Active")
        self.btn_toggle_sniff.setProperty("class", "btn-secondary")
        self.btn_toggle_sniff.clicked.connect(self._toggle_sniffer)

        sniff_layout.addWidget(sniff_title)
        sniff_layout.addWidget(self.sniff_sub)
        sniff_layout.addWidget(self.btn_toggle_sniff)
        side_layout.addWidget(sniff_frame)

        root_layout.addWidget(sidebar)

        # Right Content Area
        content_container = QWidget()
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Top Bar
        top_bar = QFrame()
        top_bar.setObjectName("topBar")
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(16, 12, 16, 12)
        top_layout.setSpacing(12)

        # Quick Add Button
        self.btn_add = QPushButton("➕ Add Video URL")
        self.btn_add.setProperty("class", "btn-primary")
        self.btn_add.clicked.connect(lambda: self._open_add_dialog())
        top_layout.addWidget(self.btn_add)

        # Open Downloads Folder
        btn_folder = QPushButton("📂 Downloads")
        btn_folder.setProperty("class", "btn-secondary")
        btn_folder.clicked.connect(self._open_downloads_folder)
        top_layout.addWidget(btn_folder)

        # Settings button (merged from Persepolis/FireDM)
        btn_settings = QPushButton("⚙️ Settings")
        btn_settings.setProperty("class", "btn-secondary")
        btn_settings.clicked.connect(self._open_settings)
        top_layout.addWidget(btn_settings)

        top_layout.addStretch()

        # Quick URL paste input in top bar
        self.quick_input = QLineEdit()
        self.quick_input.setPlaceholderText("Paste URL here & press Enter...")
        self.quick_input.setFixedWidth(280)
        self.quick_input.returnPressed.connect(self._on_quick_paste_enter)
        top_layout.addWidget(self.quick_input)

        btn_go = QPushButton("⚡ Grab")
        btn_go.setProperty("class", "btn-blue")
        btn_go.clicked.connect(self._on_quick_paste_enter)
        top_layout.addWidget(btn_go)

        content_layout.addWidget(top_bar)

        # Downloads List Scroll Area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_widget = QWidget()
        self.list_layout = QVBoxLayout(self.scroll_widget)
        self.list_layout.setContentsMargins(20, 16, 20, 16)
        self.list_layout.setSpacing(10)
        self.list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Empty State Label
        self.empty_label = QLabel(
            "📥 No downloads here yet.\n\n"
            "Copy any video link (YouTube, Facebook Reels, TikTok, Instagram, Twitter/X)\n"
            "or click '+ Add Video URL' to start downloading!\n\n"
            "🔗 Powered by yt-dlp • aria2c • FFmpeg\n"
            "Merged from: FireDM | Persepolis | PyIDM"
        )
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setStyleSheet("color: #8b949e; font-size: 14px; margin-top: 80px; line-height: 1.6;")
        self.list_layout.addWidget(self.empty_label)

        self.scroll_area.setWidget(self.scroll_widget)
        content_layout.addWidget(self.scroll_area)

        # Bottom Status Bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready. Supported: 1800+ sites via yt-dlp | aria2c acceleration | Proxy & scheduler")

        root_layout.addWidget(content_container)

    def _create_nav_btn(self, text, filter_id, layout):
        btn = QPushButton(text)
        btn.setProperty("class", "nav-btn")
        btn.setCheckable(True)
        btn.clicked.connect(lambda: self._set_filter(filter_id))
        self.nav_group.addButton(btn)
        layout.addWidget(btn)
        return btn

    def _init_clipboard_sniffer(self):
        self.sniffer = ClipboardSniffer(self)
        self.sniffer.video_url_detected.connect(self._on_sniffer_detected)
        self.sniffer.start()

    def _toggle_sniffer(self):
        cur = get_config("clipboard_sniffing", True)
        new_val = not cur
        set_config("clipboard_sniffing", new_val)
        self.sniffer.set_enabled(new_val)
        if new_val:
            self.btn_toggle_sniff.setText("🟢 Sniffer Active")
        else:
            self.btn_toggle_sniff.setText("⚪ Sniffer Paused")

    def _init_bridge_server(self):
        self.bridge = BridgeServer(parent=self)
        self.bridge.stream_captured.connect(self._on_stream_captured)
        self.bridge.start()

    def _init_scheduler(self):
        self.scheduler = DownloadScheduler(parent=self)
        self.scheduler.trigger_download.connect(self._start_task_worker)
        self.scheduler.start()

    def _on_stream_captured(self, payload):
        url = payload.get("url", "").strip()
        title = payload.get("title", "").strip()
        headers = payload.get("headers", {})
        if url:
            self.showNormal()
            self.activateWindow()
            self._open_add_dialog(initial_url=url, initial_title=title, initial_headers=headers)

    def _on_sniffer_detected(self, url):
        self._open_add_dialog(initial_url=url)

    def _on_quick_paste_enter(self):
        url = self.quick_input.text().strip()
        if url:
            self.quick_input.clear()
            self._open_add_dialog(initial_url=url)

    def _open_add_dialog(self, initial_url="", initial_title="", initial_headers=None):
        dlg = AddDownloadDialog(
            self,
            initial_url=initial_url,
            initial_title=initial_title,
            initial_headers=initial_headers
        )
        dlg.download_requested.connect(self._create_task)
        dlg.exec()

    def _open_settings(self):
        dlg = SettingsDialog(self)
        dlg.exec()

    def _create_task(self, req):
        task_id = str(uuid.uuid4())[:8]
        url = req["url"]

        # Auto-categorize (FireDM feature)
        category, cat_icon = "", ""
        if get_config("category_auto_assign", True):
            title_or_url = req.get("title") or url
            category, cat_icon = get_category_for_file(title_or_url)

        task_data = {
            "id": task_id,
            "url": url,
            "title": req.get("title") or "Resolving Title...",
            "quality": req.get("quality", "best"),
            "destination": req.get("destination", get_config("download_dir")),
            "headers": req.get("headers", {}),
            "status": "Starting" if req.get("auto_start", True) else "Queued",
            "output_path": "",
            "category": category,
            "category_icon": cat_icon,
        }
        self.tasks[task_id] = task_data
        self._add_task_widget(task_data)

        if req.get("auto_start", True):
            # Check concurrency limit (Persepolis-style queue management)
            active_count = sum(1 for w in self.workers.values() if w.isRunning())
            max_concurrent = get_config("max_concurrent_downloads", 3)
            if active_count < max_concurrent:
                self._start_task_worker(task_id)
            else:
                task_data["status"] = "Queued"
                if task_id in self.widgets:
                    self.widgets[task_id].update_status("Queued (waiting)")

        self._save_state()

    def _add_task_widget(self, task_data):
        self.empty_label.setVisible(False)
        w = TaskWidget(task_data)
        w.pause_requested.connect(self._pause_task)
        w.resume_requested.connect(self._start_task_worker)
        w.cancel_requested.connect(self._cancel_task)
        w.delete_requested.connect(self._delete_task)

        self.widgets[task_data["id"]] = w
        self.list_layout.insertWidget(0, w)
        self._apply_filter()

    def _start_task_worker(self, task_id):
        if task_id not in self.tasks:
            return
        task = self.tasks[task_id]
        task["status"] = "Downloading"

        if task_id in self.widgets:
            self.widgets[task_id].update_status("Downloading")

        worker = DownloadWorker(
            task_id=task_id,
            url=task["url"],
            quality=task.get("quality", "best"),
            destination=task.get("destination"),
            title=task.get("title"),
            headers=task.get("headers", {})
        )
        worker.progress_updated.connect(self._on_worker_progress)
        worker.status_changed.connect(self._on_worker_status)
        worker.download_finished.connect(self._on_worker_finished)
        worker.download_failed.connect(self._on_worker_failed)

        self.workers[task_id] = worker
        worker.start()

    def _on_worker_progress(self, task_id, percent, speed_str, eta_str, down_str, tot_str):
        if task_id in self.widgets:
            self.widgets[task_id].update_progress(percent, speed_str, eta_str, down_str, tot_str)

    def _on_worker_status(self, task_id, status):
        if task_id in self.tasks:
            self.tasks[task_id]["status"] = status
        if task_id in self.widgets:
            self.widgets[task_id].update_status(status)

    def _on_worker_finished(self, task_id, output_path):
        if task_id in self.tasks:
            self.tasks[task_id]["status"] = "Completed"
            self.tasks[task_id]["output_path"] = output_path
            filename = os.path.basename(output_path)
            self.tasks[task_id]["title"] = filename

            # Update category from actual filename
            if get_config("category_auto_assign", True):
                cat, cat_icon = get_category_for_file(filename)
                self.tasks[task_id]["category"] = cat
                self.tasks[task_id]["category_icon"] = cat_icon

            if task_id in self.widgets:
                self.widgets[task_id].set_title(filename)
                self.widgets[task_id].set_finished(output_path)

        if task_id in self.workers:
            del self.workers[task_id]

        self._save_state()
        self._apply_filter()
        self._start_queued_tasks()  # Start next queued task (Persepolis feature)
        self.status_bar.showMessage(f"✅ Download completed: {os.path.basename(output_path)}", 5000)

    def _on_worker_failed(self, task_id, err):
        if task_id in self.tasks:
            self.tasks[task_id]["status"] = "Failed"
        if task_id in self.widgets:
            self.widgets[task_id].update_status("Failed")
        if task_id in self.workers:
            del self.workers[task_id]
        self._save_state()
        self._start_queued_tasks()
        self.status_bar.showMessage(f"❌ Error downloading {task_id}: {err}", 6000)

    def _start_queued_tasks(self):
        """Auto-start queued tasks when a slot frees up (Persepolis-style queue management)."""
        active_count = sum(1 for w in self.workers.values() if w.isRunning())
        max_concurrent = get_config("max_concurrent_downloads", 3)

        for task_id, task in self.tasks.items():
            if active_count >= max_concurrent:
                break
            if task.get("status", "").lower() in ("queued", "queued (waiting)"):
                self._start_task_worker(task_id)
                active_count += 1

    def _pause_task(self, task_id):
        if task_id in self.workers:
            self.workers[task_id].cancel()
            del self.workers[task_id]
        if task_id in self.tasks:
            self.tasks[task_id]["status"] = "Paused"
        if task_id in self.widgets:
            self.widgets[task_id].update_status("Paused")
        self._save_state()

    def _cancel_task(self, task_id):
        self._pause_task(task_id)
        self._delete_task(task_id)

    def _delete_task(self, task_id):
        if task_id in self.workers:
            self.workers[task_id].cancel()
            del self.workers[task_id]
        if task_id in self.widgets:
            w = self.widgets.pop(task_id)
            self.list_layout.removeWidget(w)
            w.deleteLater()
        if task_id in self.tasks:
            del self.tasks[task_id]
        self._save_state()
        if len(self.tasks) == 0:
            self.empty_label.setVisible(True)

    def _set_filter(self, filter_id):
        self.current_filter = filter_id
        self._apply_filter()

    def _apply_filter(self):
        visible_count = 0
        for task_id, w in self.widgets.items():
            status = self.tasks[task_id].get("status", "").lower()
            if self.current_filter == "all":
                show = True
            elif self.current_filter == "active":
                show = "downloading" in status or "connecting" in status or "merging" in status or "retrying" in status
            elif self.current_filter == "completed":
                show = "completed" in status
            elif self.current_filter == "queued":
                show = "paused" in status or "queued" in status or "failed" in status
            else:
                show = True

            w.setVisible(show)
            if show:
                visible_count += 1

        self.empty_label.setVisible(visible_count == 0)

    def _update_stats(self):
        """Update sidebar stats panel."""
        active = sum(1 for t in self.tasks.values() if "downloading" in t.get("status", "").lower() or "connecting" in t.get("status", "").lower())
        completed = sum(1 for t in self.tasks.values() if "completed" in t.get("status", "").lower())
        total = len(self.tasks)

        self.stats_active_lbl.setText(f"Active: {active}")
        self.stats_completed_lbl.setText(f"Completed: {completed}")
        self.stats_total_lbl.setText(f"Total: {total}")

    def _open_downloads_folder(self):
        d = get_config("download_dir")
        os.makedirs(d, exist_ok=True)
        os.startfile(d)

    def _load_saved_history(self):
        history = load_history()
        for item in history:
            task_id = item["id"]
            self.tasks[task_id] = item
            w = TaskWidget(item)
            w.pause_requested.connect(self._pause_task)
            w.resume_requested.connect(self._start_task_worker)
            w.cancel_requested.connect(self._cancel_task)
            w.delete_requested.connect(self._delete_task)
            if item.get("status") == "Completed":
                w.set_finished(item.get("output_path", ""))
            self.widgets[task_id] = w
            self.list_layout.addWidget(w)

        if len(self.tasks) > 0:
            self.empty_label.setVisible(False)

    def _save_state(self):
        save_history(list(self.tasks.values()))
