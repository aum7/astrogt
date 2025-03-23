# ruff: noqa: E402
# import gi

# gi.require_version("Gtk", "4.0")
# from gi.repository import Gtk  # type: ignore


class SignalManager:
    def __init__(self):
        self.signals = {}

    def connect(self, widget, signal, handler):
        if widget not in self.signals:
            self.signals[widget] = {}
        self.signals[widget][signal] = handler
        widget.connect(signal, handler)

    def disconnect(self, widget, signal):
        if widget in self.signals and signal in self.signals[widget]:
            widget.disconnect_by_func(self.signals[widget][signal])
            del self.signals[widget][signal]

    def emit(self, widget, signal, *args):
        if widget in self.signals and signal in self.signals[widget]:
            self.signals[widget][signal](*args)


# signal_manager = SignalManager()
