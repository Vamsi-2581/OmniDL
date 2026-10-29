"""Download scheduler — merged from Persepolis Download Manager.

Supports:
- Scheduled start times (queue a download to begin at a specific time)
- Speed-limited periods (e.g. slow speed during work hours, full speed at night)
- Post-completion actions (shutdown, sleep, notify)
"""
import time
from datetime import datetime, timedelta
from PyQt6.QtCore import QObject, pyqtSignal, QTimer


class DownloadScheduler(QObject):
    """Manages timed download starts and speed schedule profiles."""
    trigger_download = pyqtSignal(str)  # task_id to start
    trigger_speed_change = pyqtSignal(int)  # new speed limit in bytes/s (0 = unlimited)
    trigger_action = pyqtSignal(str)  # 'shutdown', 'sleep', 'notify'

    def __init__(self, parent=None):
        super().__init__(parent)
        self._scheduled_tasks = {}  # task_id -> datetime
        self._speed_profiles = []  # list of {start_hour, end_hour, speed_limit}
        self._timer = QTimer(self)
        self._timer.setInterval(10_000)  # Check every 10 seconds
        self._timer.timeout.connect(self._tick)

    def start(self):
        self._timer.start()

    def stop(self):
        self._timer.stop()

    def schedule_download(self, task_id, start_time: datetime):
        """Schedule a download to start at a specific time."""
        self._scheduled_tasks[task_id] = start_time

    def cancel_schedule(self, task_id):
        self._scheduled_tasks.pop(task_id, None)

    def add_speed_profile(self, start_hour: int, end_hour: int, speed_limit: int):
        """Add a speed limit profile for a time window (Persepolis feature).

        Args:
            start_hour: Hour of day (0-23) when this profile activates
            end_hour: Hour of day (0-23) when this profile deactivates
            speed_limit: Speed limit in bytes/sec (0 = unlimited)
        """
        self._speed_profiles.append({
            "start_hour": start_hour,
            "end_hour": end_hour,
            "speed_limit": speed_limit
        })

    def _tick(self):
        now = datetime.now()

        # Check scheduled downloads
        triggered = []
        for task_id, start_time in list(self._scheduled_tasks.items()):
            if now >= start_time:
                self.trigger_download.emit(task_id)
                triggered.append(task_id)

        for tid in triggered:
            del self._scheduled_tasks[tid]

        # Check speed profiles
        current_hour = now.hour
        for profile in self._speed_profiles:
            sh = profile["start_hour"]
            eh = profile["end_hour"]
            if sh <= eh:
                in_range = sh <= current_hour < eh
            else:
                # Wraps past midnight (e.g. 22:00 - 06:00)
                in_range = current_hour >= sh or current_hour < eh

            if in_range:
                self.trigger_speed_change.emit(profile["speed_limit"])
                break

    def get_scheduled_count(self):
        return len(self._scheduled_tasks)

    def get_next_scheduled(self):
        if not self._scheduled_tasks:
            return None
        return min(self._scheduled_tasks.values())
