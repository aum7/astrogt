# ruff: noqa: E402
import gi

# gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw  # type: ignore


class NotifyManager:
    def __init__(self):
        self.toast_overlay = None

    # def setup_overlay(self, window):
    #     # content would be main_window
    #     content = window.get_child()
    #     self.toast_overlay = Adw.ToastOverlay()
    #     # self.toast_overlay.set_transient_for(window)
    #     self.toast_overlay.set_child(content)
    #     window.set_child(self.toast_overlay)

    def notify(self, message, timeout=3):
        if self.toast_overlay:
            toast = Adw.Toast.new(message)
            toast.set_timeout(timeout)
            # toast.set_transient_for(self.toast_overlay)
            self.toast_overlay.add_toast(toast)
            return True
        return False
