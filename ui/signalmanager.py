# ruff: noqa: E402
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore


class SignalManager:
    def __init__(self, get_application=None):
        # store handlers
        self._get_application = get_application or Gtk.Application.get_default()
        self._handlers = {}

    def _emit(self, signal_name, *args):
        print(f"signalmanager : emitting signal {signal_name}")
        if signal_name not in self._handlers:
            return
        for handler in self._handlers[signal_name]:
            handler(*args)

    def _connect(self, signal_name, handler):
        print(f"signalmanager : connecting signal {signal_name}")
        if signal_name not in self._handlers:
            self._handlers[signal_name] = []
        self._handlers[signal_name].append(handler)

    def _disconnect(self, signal_name, handler):
        if signal_name in self._handlers and handler in self._handlers[signal_name]:
            self._handlers[signal_name].remove(handler)
