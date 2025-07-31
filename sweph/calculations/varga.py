# sweph/calculations/varga.py
# navams
# draw natal navams into event ring
# draw transit navams into separate /varga ring
# ruff: noqa: E402, E701
# import swisseph as swe
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore
# from ui.helpers import _object_name_to_code as objcode
# from sweph.swetime import jd_to_custom_iso as jdtoiso


def calculate_varga(event: str, division: int = 9):
    # calculate planetary positions in varga chart
    app = Gtk.Application.get_default()
    notify = app.notify_manager
    msg = f"event {event}\n"
    varga_data = []
    varga_data.append({"event": event})
    # event 1 is mandatory
    if event == "e1":
        # check by event 1 sweph attribute
        if not app.e1_sweph.get("jd_ut"):
            notify.error(
                "missing event 1 data : exiting ...",
                source="varga",
                route=[""],
            )
            return
        # e1 positions
        e1_pos = getattr(app, "e1_positions", None)
        if e1_pos:
            for _, data in e1_pos.items():
                if isinstance(data, dict) and "lon" in data:
                    name = data.get("name", "")
                    lon = data.get("lon", 0.0)
                    sign = int(lon // 30)
                    seg = int((lon % 30) // (30 / division))
                    varga_sign = (sign * division + seg) % 12
                    varga = (varga_sign * 30) + ((lon % (30 / division)) * division)
                    varga_data.append({"name": name, "lon": varga})
                    # varga_data.append({"name": name, "lon": varga, "var": varga})
            app.varga_e1 = varga_data
        # msg += f"e1pos : {e1_pos}\n"
    if event == "e2":
        # check by event 2 sweph attribute
        if not app.e2_sweph.get("jd_ut"):
            notify.error(
                "missing event 2 data : exiting ...",
                source="varga",
                route=[""],
            )
            return
        # e2 positions
        e2_pos = getattr(app, "e2_positions", None)
        if e2_pos:
            for _, data in e2_pos.items():
                if isinstance(data, dict) and "lon" in data:
                    name = data.get("name", "")
                    lon = data.get("lon", 0.0)
                    sign = int(lon // 30)
                    seg = int((lon % 30) // (30 / division))
                    varga_sign = (sign * division + seg) % 12
                    varga = (varga_sign * 30) + ((lon % (30 / division)) * division)
                    varga_data.append({"name": name, "lon": varga, "var": varga})
            app.varga_e2 = varga_data
        # msg += f"e2pos : {e2_pos}\n"
    msg += f"vargadata : {varga_data}"
    # emit signal
    app.signal_manager._emit("varga_changed", event)
    notify.debug(
        msg,
        source="varga",
        route=[""],
    )
    return varga_data


def connect_signals_varga(signal_manager):
    # update varga chart
    signal_manager._connect("event_changed", calculate_varga)
    signal_manager._connect("settings_changed", calculate_varga)
