# ruff: noqa: E402
# ruff: noqa: E701
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore
from sweph.setupsettings import SetupSettings


class SwePositions:
    """get positions of planets"""

    def __init__(self, app=None):
        self._app = app or Gtk.Application.get_default()
        self._notify = self._app.notify_manager
        self._signal = self._app.signal_manager
        # connect to data-changed signal
        self._signal._connect("event-one-changed", self.on_event_one_changed)
        self._signal._connect("event-two-changed", self.on_event_two_changed)
        self.swe_core = self._app.swe_core
        self.e1data = self.swe_core.event_one_swe_ready()
        self.e2data = self.swe_core.event_two_swe_ready()
        # todo this is in user/settings/setupsettings.py
        self.flags = SetupSettings()._get_swe_flags()
        # print(f"flags : {self.flags}")

    def on_event_one_changed(self, data, *args):
        self.e1data = data
        self._notify.info(
            f"event 1 changed\n\t{self.e1data}",
            source="swepositions",
            route=["terminal"],
        )

    def on_event_two_changed(self, data, *args):
        self.e2data = data
        self._notify.info(
            f"event 2 changed\n\t{self.e2data}",
            source="swepositions",
            route=["terminal"],
        )
