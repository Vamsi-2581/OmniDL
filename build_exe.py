import subprocess
import sys
import os

def build():
    print("Building OmniDL Pro standalone Windows executable...")
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=OmniDL-Pro",
        "--noconsole",
        "--onefile",
        "--clean",
        "--icon=assets/icon.ico",
        "--collect-all=yt_dlp",
        "--hidden-import=PyQt6",
        "--hidden-import=requests",
        "--hidden-import=websockets",
        "main.py"
    ]
    subprocess.run(cmd, check=True)
    if os.path.exists("dist/OmniDL-Pro.exe"):
        import shutil
        shutil.copy2("dist/OmniDL-Pro.exe", "OmniDL-Pro.exe")
        print("\n[SUCCESS] Executable copied to: OmniDL-Pro.exe")


if __name__ == "__main__":
    build()
