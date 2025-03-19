# ruff: noqa: E402
import gi

gi.require_version("Adw", "1")
from gi.repository import Adw  # type: ignore


class NotifyManager:
    def __init__(self):
        self.toast_overlay = None

    def notify(self, message, timeout=3):
        if self.toast_overlay:
            toast = Adw.Toast.new(message)
            toast.set_timeout(timeout)
            self.toast_overlay.add_toast(toast)
            return True
        return False
