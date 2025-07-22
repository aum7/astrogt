# sweph/calculations/lots.py
# ruff: noqa: E402, E701
import re
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore
from typing import List

# from ui.helpers import _object_name_to_code as objcode
# from sweph.swetime import jd_to_custom_iso as jdtoiso
from user.settings import LOTS


def calculate_lots(event: str):
    """calculate arabic parts aka hermetic lots for event (< mandatory)"""
    # grab existing positions with lon speed & calculate positions of lots
    app = Gtk.Application.get_default()
    notify = app.notify_manager
    msg = f"event {event}\n"
    lots_data = []
    events: List[str] = [event] if event else ["e1", "e2"]
    if "e2" in events and not app.e2_sweph.get("jd_ut"):
        # skip e2 if no datetime / julian day utc set = user not interested in e2
        events.remove("e2")
        msg += "e2 removed\n"
    for event_name in events:
        pos, houses, lots = None, None, None
        # grab positons & selected objects based on event
        if event_name in ("e1", "e2"):
            pos = getattr(app, f"{event_name}_positions")
            houses = getattr(app, f"{event_name}_houses")
            lots = getattr(app, f"selected_lots_{event_name}")
        elif event_name == "p3":
            # pos includes asc & mc + e2 selected objects
            pos = getattr(app, "p3_pos")
            lots = getattr(app, "selected_lots_e2")
        # msg += (
        #     f"event {event_name}\nlots {LOTS}\npos : {pos}"
        #     f"\nhouses : {houses}\nlots : {lots}"
        # )
        if not pos or not lots or not houses:
            notify.warning(
                f"data for {event_name} missing : exiting ...",
                source="lots",
                route=["terminal"],
            )
            return
        lots_data.append({"event": event_name})
        # lots_order = ("fortuna", "spirit", "eros", "courage", "victory", "nemesis")
        for lot in lots:
            LOT = LOTS.get(lot, {})
            # use day formula
            formula = LOT.get("day")
            if not formula:
                continue
            # parse formula to get objects needed
            objs_needed = re.findall(r"\b[a-z]{2,}\b", formula)
            # msg += f"objsneeded : {objs_needed}\n"
            # gather data for lots calculation : ascendant
            data = {"asc": houses[1][0]}
            # example if house cusps are needed
            # data["3rd"] = houses[0][3]  # 3rd house cusp
            # data["10th"] = houses[0][10]  # 10th cusp (equal & whole-sign houses)
            # data["mc"] = houses[1][1]  # true midheaven (quadrant houses)
            # msg += f"data example : {data}\n"
            # planetary longitudes
            for obj in objs_needed:
                for v in pos.values():
                    if isinstance(v, dict) and v.get("name") == obj:
                        data[v["name"]] = v["lon"]
                        # msg += f"obj : {obj} | lon : {v['lon']}\n"
            try:
                lot_lon = eval(formula, {}, data) % 360
            except Exception as e:
                notify.error(f"{lot} error :\n\t{e}")
            lots_data.append({
                "name": lot,
                "lon": lot_lon,
            })
        msg += f"lotsdata : {lots_data}\n"
    notify.debug(
        msg,
        source="lots",
        route=[""],
    )
    return lots_data
