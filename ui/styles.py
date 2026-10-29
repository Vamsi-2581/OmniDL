MODERN_DARK_THEME = """
/* Global Window Styling */
QMainWindow, QDialog, QWidget {
    background-color: #0d1117;
    color: #e6edf3;
    font-family: 'Segoe UI', 'SF Pro Display', -apple-system, Roboto, sans-serif;
    font-size: 13px;
}

/* Sidebar styling */
#sidebar {
    background-color: #161b22;
    border-right: 1px solid #21262d;
    padding-top: 15px;
}

#logoLabel {
    font-size: 18px;
    font-weight: 700;
    color: #58a6ff;
    padding: 10px 16px;
    letter-spacing: 0.5px;
}

#logoSubLabel {
    font-size: 11px;
    font-weight: 500;
    color: #8b949e;
    padding-left: 16px;
    margin-bottom: 20px;
}

/* Navigation Buttons */
QPushButton.nav-btn {
    background-color: transparent;
    color: #8b949e;
    border: none;
    border-radius: 6px;
    padding: 10px 16px;
    text-align: left;
    font-size: 13px;
    font-weight: 600;
    margin: 2px 10px;
}

QPushButton.nav-btn:hover {
    background-color: #21262d;
    color: #c9d1d9;
}

QPushButton.nav-btn:checked {
    background-color: #1f6feb;
    color: #ffffff;
}

/* Header & Top Bar */
#topBar {
    background-color: #161b22;
    border-bottom: 1px solid #21262d;
    padding: 10px 20px;
}

/* Primary Action Buttons */
QPushButton.btn-primary {
    background-color: #238636;
    color: #ffffff;
    border: 1px solid rgba(240, 246, 252, 0.1);
    border-radius: 6px;
    padding: 8px 18px;
    font-weight: 600;
    font-size: 13px;
}

QPushButton.btn-primary:hover {
    background-color: #2ea043;
}

QPushButton.btn-primary:pressed {
    background-color: #238636;
}

/* Blue Accent Buttons */
QPushButton.btn-blue {
    background-color: #1f6feb;
    color: #ffffff;
    border: 1px solid rgba(240, 246, 252, 0.1);
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 600;
    font-size: 13px;
}

QPushButton.btn-blue:hover {
    background-color: #388bfd;
}

/* Secondary Buttons */
QPushButton.btn-secondary {
    background-color: #21262d;
    color: #c9d1d9;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 8px 14px;
    font-weight: 500;
}

QPushButton.btn-secondary:hover {
    background-color: #30363d;
    border-color: #8b949e;
}

/* Danger Buttons */
QPushButton.btn-danger {
    background-color: rgba(248, 81, 73, 0.15);
    color: #f85149;
    border: 1px solid rgba(248, 81, 73, 0.4);
    border-radius: 6px;
    padding: 6px 12px;
    font-weight: 600;
}

QPushButton.btn-danger:hover {
    background-color: #da3633;
    color: #ffffff;
}

/* Input Fields */
QLineEdit {
    background-color: #0d1117;
    color: #c9d1d9;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 13px;
    selection-background-color: #1f6feb;
}

QLineEdit:focus {
    border-color: #58a6ff;
    outline: none;
}

/* Combo Box */
QComboBox {
    background-color: #21262d;
    color: #c9d1d9;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 7px 12px;
    font-size: 13px;
}

QComboBox:hover {
    border-color: #58a6ff;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox QAbstractItemView {
    background-color: #161b22;
    color: #c9d1d9;
    selection-background-color: #1f6feb;
    selection-color: #ffffff;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 4px;
}

/* Progress Bar */
QProgressBar {
    background-color: #21262d;
    border: none;
    border-radius: 4px;
    height: 8px;
    text-align: center;
    color: transparent;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #1f6feb, stop:1 #58a6ff);
    border-radius: 4px;
}

/* Scroll Area */
QScrollArea {
    border: none;
    background-color: transparent;
}

QScrollBar:vertical {
    background: #0d1117;
    width: 10px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background: #30363d;
    min-height: 20px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background: #8b949e;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* Card / Task Item Container */
#taskCard {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 10px;
    padding: 14px;
    margin-bottom: 10px;
}

#taskCard:hover {
    border-color: #58a6ff;
}

/* Status Badges */
QLabel.badge-downloading {
    background-color: rgba(56, 139, 253, 0.15);
    color: #58a6ff;
    border: 1px solid rgba(56, 139, 253, 0.4);
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 11px;
    font-weight: 600;
}

QLabel.badge-completed {
    background-color: rgba(46, 160, 67, 0.15);
    color: #3fb950;
    border: 1px solid rgba(46, 160, 67, 0.4);
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 11px;
    font-weight: 600;
}

QLabel.badge-failed {
    background-color: rgba(248, 81, 73, 0.15);
    color: #f85149;
    border: 1px solid rgba(248, 81, 73, 0.4);
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 11px;
    font-weight: 600;
}

QLabel.badge-paused {
    background-color: rgba(210, 153, 34, 0.15);
    color: #d29922;
    border: 1px solid rgba(210, 153, 34, 0.4);
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 11px;
    font-weight: 600;
}

/* Checkbox */
QCheckBox {
    color: #c9d1d9;
    font-size: 13px;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 1px solid #30363d;
    border-radius: 4px;
    background-color: #0d1117;
}

QCheckBox::indicator:checked {
    background-color: #1f6feb;
    border-color: #58a6ff;
    image: url(""); /* Can render checkmark */
}

/* Status Bar */
QStatusBar {
    background-color: #161b22;
    color: #8b949e;
    border-top: 1px solid #21262d;
    padding: 4px 10px;
    font-size: 12px;
}
"""
