# sweph/calculations/progressions.py
# ruff: noqa: E402, E701
import swisseph as swe
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore


def calculate_primary(event: str):
    # grab application data & calculate vimsottari for event 1
    app = Gtk.Application.get_default()
    notify = app.notify_manager
    msg = f"event {event}\n"
    msg += "olo\n"
    # event 1 data is mandatory and main source
    # check against lumies since e1_sweph can have 0 objects (user-selectable)
    if not app.e1_lumies.get("jd_ut"):
        notify.error(
            "missing event 1 data needed for progressions : exiting ...",
            source="progressions",
            route=["terminal", "user"],
        )
        return
    # event 2 data is also mandatory for progressions todo alternaive check : app.e2_active
    if not app.e2_lumies.get("jd_ut"):
        notify.error(
            "missing event 2 data needed for progressions : exiting ...",
            source="progressions",
            route=["terminal", "user"],
        )
        return
    # e2_jd = app.e2_lumies.get("jd_ut") if hasattr(app, "e2_lumies") else None
    # e2 calculations
    if event == "e2":
        msg += "e2 detected\n"
        msg += f"{e2_cleared(event)}"
    # app.signal_manager._emit("progressions_changed", event)
    notify.debug(
        msg,
        source="progressions",
        route=["terminal"],
    )


def connect_signals_progressions(signal_manager):
    # update progressions when data used changes
    signal_manager._connect("positions_changed", calculate_primary)
    signal_manager._connect("houses_changed", calculate_primary)
    signal_manager._connect("e2_cleared", e2_cleared)


def e2_cleared(event):
    # todo clear all event 2 data
    if event == "e2":
        return "e2 was cleared\n"
