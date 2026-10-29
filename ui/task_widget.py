import os
import subprocess
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QProgressBar, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal

class TaskWidget(QFrame):
    pause_requested = pyqtSignal(str)   # task_id
    resume_requested = pyqtSignal(str)  # task_id
    cancel_requested = pyqtSignal(str)  # task_id
    delete_requested = pyqtSignal(str)  # task_id

    def __init__(self, task_data, parent=None):
        super().__init__(parent)
        self.setObjectName("taskCard")
        self.task_id = task_data["id"]
        self.url = task_data["url"]
        self.title = task_data.get("title") or "Loading title..."
        self.output_path = task_data.get("output_path", "")
        self.status = task_data.get("status", "Queued")
        self.quality = task_data.get("quality", "best")

        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(14, 12, 14, 12)
        main_layout.setSpacing(8)

        # Top Row: Title, Badge, Actions
        top_row = QHBoxLayout()
        top_row.setSpacing(10)

        # Title Label
        self.title_lbl = QLabel(self.title)
        self.title_lbl.setStyleSheet("font-weight: 600; font-size: 13px; color: #f0f6fc;")
        self.title_lbl.setWordWrap(False)
        self.title_lbl.setTextFormat(Qt.TextFormat.PlainText)
        top_row.addWidget(self.title_lbl, 1)

        # Status Badge
        self.badge = QLabel(self.status)
        top_row.addWidget(self.badge)

        # Action Buttons
        self.btn_action = QPushButton("⏸️")
        self.btn_action.setToolTip("Pause / Resume")
        self.btn_action.setProperty("class", "btn-secondary")
        self.btn_action.setFixedSize(32, 28)
        self.btn_action.clicked.connect(self._toggle_pause)
        top_row.addWidget(self.btn_action)

        self.btn_open = QPushButton("▶️ Play")
        self.btn_open.setToolTip("Play file")
        self.btn_open.setProperty("class", "btn-blue")
        self.btn_open.setFixedHeight(28)
        self.btn_open.clicked.connect(self._open_file)
        self.btn_open.setVisible(False)
        top_row.addWidget(self.btn_open)

        self.btn_folder = QPushButton("📁 Folder")
        self.btn_folder.setToolTip("Open folder")
        self.btn_folder.setProperty("class", "btn-secondary")
        self.btn_folder.setFixedHeight(28)
        self.btn_folder.clicked.connect(self._open_folder)
        self.btn_folder.setVisible(False)
        top_row.addWidget(self.btn_folder)

        self.btn_cancel = QPushButton("✖")
        self.btn_cancel.setToolTip("Cancel or remove")
        self.btn_cancel.setProperty("class", "btn-danger")
        self.btn_cancel.setFixedSize(30, 28)
        self.btn_cancel.clicked.connect(self._on_cancel)
        top_row.addWidget(self.btn_cancel)

        main_layout.addLayout(top_row)

        # Badge style toggles the buttons above, so it must run after they exist
        self._update_badge_style(self.status)

        # Middle Row: Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        main_layout.addWidget(self.progress_bar)

        # Bottom Row: Stats (Downloaded, Total, Speed, ETA)
        bottom_row = QHBoxLayout()
        self.size_lbl = QLabel("0 B / 0 B")
        self.size_lbl.setStyleSheet("color: #8b949e; font-size: 11px;")
        bottom_row.addWidget(self.size_lbl)

        bottom_row.addStretch()

        self.speed_lbl = QLabel("Speed: --")
        self.speed_lbl.setStyleSheet("color: #58a6ff; font-weight: 600; font-size: 11px;")
        bottom_row.addWidget(self.speed_lbl)

        self.eta_lbl = QLabel("ETA: --:--")
        self.eta_lbl.setStyleSheet("color: #8b949e; font-size: 11px; margin-left: 10px;")
        bottom_row.addWidget(self.eta_lbl)

        main_layout.addLayout(bottom_row)

    def _update_badge_style(self, status):
        status_lower = status.lower()
        if "completed" in status_lower or "done" in status_lower:
            self.badge.setProperty("class", "badge-completed")
            self.badge.setText("✅ Completed")
            self.btn_action.setVisible(False)
            self.btn_open.setVisible(True)
            self.btn_folder.setVisible(True)
        elif "downloading" in status_lower:
            self.badge.setProperty("class", "badge-downloading")
            self.badge.setText("⚡ Downloading")
            self.btn_action.setVisible(True)
            self.btn_action.setText("⏸️")
            self.btn_open.setVisible(False)
            self.btn_folder.setVisible(False)
        elif "paused" in status_lower:
            self.badge.setProperty("class", "badge-paused")
            self.badge.setText("⏸️ Paused")
            self.btn_action.setVisible(True)
            self.btn_action.setText("▶️")
        elif "failed" in status_lower or "cancelled" in status_lower:
            self.badge.setProperty("class", "badge-failed")
            self.badge.setText("❌ " + status)
            self.btn_action.setVisible(False)
        else:
            self.badge.setProperty("class", "badge-downloading")
            self.badge.setText(status)

        self.badge.style().unpolish(self.badge)
        self.badge.style().polish(self.badge)

    def update_progress(self, percent, speed_str, eta_str, downloaded_str, total_str):
        self.progress_bar.setValue(int(percent))
        self.speed_lbl.setText(f"Speed: {speed_str}")
        self.eta_lbl.setText(f"ETA: {eta_str}")
        self.size_lbl.setText(f"{downloaded_str} / {total_str}")

    def update_status(self, status):
        self.status = status
        self._update_badge_style(status)

    def set_title(self, title):
        self.title = title
        self.title_lbl.setText(title)

    def set_finished(self, output_path):
        self.output_path = output_path
        self.status = "Completed"
        self._update_badge_style("Completed")
        self.progress_bar.setValue(100)
        self.speed_lbl.setText("Complete")
        self.eta_lbl.setText("00:00")

    def _toggle_pause(self):
        if "downloading" in self.status.lower():
            self.pause_requested.emit(self.task_id)
        else:
            self.resume_requested.emit(self.task_id)

    def _on_cancel(self):
        if self.status == "Completed":
            self.delete_requested.emit(self.task_id)
        else:
            self.cancel_requested.emit(self.task_id)

    def _open_file(self):
        if self.output_path and os.path.exists(self.output_path):
            os.startfile(self.output_path)
        else:
            folder = os.path.dirname(self.output_path) if self.output_path else ""
            if folder and os.path.exists(folder):
                os.startfile(folder)

    def _open_folder(self):
        folder = os.path.dirname(self.output_path) if self.output_path else ""
        if folder and os.path.exists(folder):
            os.startfile(folder)
