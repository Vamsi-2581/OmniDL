import sys
import os

# Prevent crash in PyInstaller --noconsole when print() is called
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w", encoding="utf-8")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w", encoding="utf-8")

def excepthook(exc_type, exc_value, exc_tb):
    import traceback
    try:
        with open(os.path.join(os.path.expanduser("~"), ".omni_downloader", "crash.log"), "w", encoding="utf-8") as f:
            traceback.print_exception(exc_type, exc_value, exc_tb, file=f)
    except Exception:
        pass
sys.excepthook = excepthook

from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import Qt

from ui.main_window import MainWindow
from core.config import ensure_dirs, get_config

def main():
    ensure_dirs()
    app = QApplication(sys.argv)
    app.setApplicationName("OmniDL Pro")
    app.setOrganizationName("OmniSuite")

    # Set application style
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()
    window.raise_()
    window.activateWindow()

    # System Tray integration
    tray = QSystemTrayIcon(window)
    # We can use a standard system icon or fallback
    standard_icon = window.style().standardIcon(window.style().StandardPixmap.SP_ArrowDown)
    tray.setIcon(standard_icon)
    tray.setToolTip("⚡ OmniDL Pro - Universal Video Downloader")

    tray_menu = QMenu()
    act_show = QAction("Show OmniDL", window)
    act_show.triggered.connect(window.showNormal)
    tray_menu.addAction(act_show)

    act_add = QAction("➕ Add New Download", window)
    act_add.triggered.connect(lambda: window._open_add_dialog())
    tray_menu.addAction(act_add)

    act_folder = QAction("📁 Open Downloads Folder", window)
    act_folder.triggered.connect(window._open_downloads_folder)
    tray_menu.addAction(act_folder)

    tray_menu.addSeparator()

    act_exit = QAction("Exit", window)
    act_exit.triggered.connect(app.quit)
    tray_menu.addAction(act_exit)

    tray.setContextMenu(tray_menu)
    tray.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
