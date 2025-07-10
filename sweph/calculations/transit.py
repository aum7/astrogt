# sweph/calculations/transit.py
# ruff: noqa: E402, E701
# import swisseph as swe
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore


def calculate_transit(event: str):
    # gather transit data
    app = Gtk.Application.get_default()
    notify = app.notify_manager
    msg = f"event {event}\n"
    # event 1 & 2 data is mandatory : natal / event & progression chart
    # check against lumies since e1_sweph can have 0 objects (user-selectable)
    if not app.e1_sweph.get("jd_ut") or not app.e2_sweph.get("jd_ut"):
        notify.error(
            "missing event 1 or 2 data needed for transit : exiting ...",
            source="transit",
            route=[""],
        )
        return
    # gather data
    e2_sweph = getattr(app, "e2_sweph", None)
    if e2_sweph:
        transit_pos = getattr(app, "e2_positions", {})
        transit_houses = getattr(app, "e2_houses", {})
        transit_data: list[dict] = []
        # msg += f"transitpos :\n\t{transit_pos}\ntransithouses :\n\t{transit_houses}\n"
        # pack for rings
        for v in transit_pos.values():
            if isinstance(v, dict) and "name" in v and "lon" in v:
                transit_data.append({"name": v["name"], "lon": v["lon"]})
        # cusps
        transit_data.append(transit_houses[0])
        # pack ascendant & midheaven
        if transit_houses and len(transit_houses) > 1:
            v = transit_houses[1]
            if len(v) > 0:
                transit_data.append({"name": "asc", "lon": v[0]})
            if len(v) > 1:
                transit_data.append({"name": "mc", "lon": v[1]})
    msg += f"transitdata :\n\t{transit_data}"
    app.transit_data = transit_data
    # emit signal
    app.signal_manager._emit("transit_changed", event)
    notify.debug(
        msg,
        source="transit",
        route=[""],
    )


def e2_cleared(event):
    # todo clear all event 2 data
    if event == "e2":
        return "e2 was cleared : todo\n"


def connect_signals_transit(signal_manager):
    # update app when data used changes
    signal_manager._connect("event_changed", calculate_transit)
    signal_manager._connect("settings_changed", calculate_transit)
    signal_manager._connect("e2_cleared", e2_cleared)
