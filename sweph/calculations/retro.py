# sweph/calculations/retro.py
# ruff: noqa: E402, E701
import swisseph as swe
import numpy as np
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore
from collections import defaultdict  # will add attr if missing
from typing import List, Optional
from ui.helpers import _object_name_to_code as objcode


average_speed = {
    # average speeds in deg/day (wikipedia)
    # "su": 0.9856, # never retro
    # "mo": 13.1764, # never retro
    "me": 1.607,
    "ve": 1.174,
    "ma": 0.524,
    "ju": 0.083,
    "sa": 0.033,
    "ur": 0.012,
    "ne": 0.006,
    "pl": 0.004,
}

# def is_stationary(planet, speed):
#     # if below x percent > declare stationary
#     threshold_pct = 0.02  # 2 %
#     avg = average_speed[planet]
#     return abs(speed) < abs(avg) * threshold_pct


def calculate_retro(event: Optional[str] = None):
    """calculate retro station & direction for one or both events"""
    # 2 options : get jd_ut for e1 / e2 / p3 & calculate speeds ... or grab
    # existing positions with lon speed - & calculate
    app = Gtk.Application.get_default()
    notify = app.notify_manager
    msg = f"event {event}\n"
    events: List[str] = [event] if event else ["e1", "e2"]
    if "e2" in events and not app.e2_sweph.get("jd_ut"):
        # skip e2 if no datetime / julian day utc set = user not interested in e2
        events.remove("e2")
        msg += "e2 removed\n"
    for event in events:
        # sweph = app.e1_sweph if event == "e1" else app.e2_sweph
        # print(f"retro : sweph :\n\t{sweph}")
        jd_ut = 0.0
        pos = ()
        if event == "e1":
            pos = getattr(app, "e1_positions")
            jd_ut = pos.get("jd_ut") if isinstance(pos, dict) else None
        elif event == "e2":
            pos = getattr(app, "e2_positions")
            jd_ut = pos.get("jd_ut") if isinstance(pos, dict) else None
        elif event == "p3":
            pos = getattr(app, "p3_pos")
            jd_ut = next(
                (o["jd_ut"] for o in pos if isinstance(o, dict) and "jd_ut" in o)
            )
        # msg += f"retro [{event}] :\n\tjdut : {jd_ut}\n\tpos : {pos}\n"
        objs = app.selected_objects_e1 if event == "e1" else app.selected_objects_e2
        use_mean_node = app.chart_settings["mean node"]
        # times = np.arange(start_jd, end_jd, step)
        # lon, speed = pos.get("lon"), pos.get("lon speed")
        threshold_pct = 0.02  # 2 %
        retro_events = {}
        for obj in objs:
            code, name = objcode(obj, use_mean_node)
            if code is None:
                continue
            # prev_speed = {}
            # prev_direction = {}
            avg = average_speed.get(name)
            speed = None
            # e1 / e2 search in pos (dict) for matching name
            if event in ["e1", "e2"] and isinstance(pos, dict):
                for _, v in pos.items():
                    if isinstance(v, dict) and v.get("name") == name:
                        speed = v.get("lon speed")
                        break
            # p3 search in pos (list) for dict name==name
            elif event == "p3" and isinstance(pos, list):
                for v in pos:
                    if (
                        isinstance(v, dict)
                        and v.get("name") == name
                        and "lon speed" in v
                    ):
                        speed = v.get("lon speed")
                        break
            if avg and speed:
                threshold = abs(avg) * threshold_pct
                is_station = abs(speed) < threshold
                # 1 = direct : -1 = retro : 0 = stationary
                direction = 1 if speed > 0 else (-1 if speed < 0 else 0)
                prev_direction = retro_events.get(name, {}).get("prev_direction", None)
                if prev_direction is not None:
                    # check for stationary retrograde (SR) or stationary direct (SD)
                    if prev_direction > 0 and direction < 0 and is_station:
                        retro_events.setdefault(name, {"events": []})["events"].append((
                            jd_ut,
                            "SR",
                            speed,
                        ))
                    elif prev_direction < 0 and direction > 0 and is_station:
                        retro_events.setdefault(name, {"events": []})["events"].append((
                            jd_ut,
                            "SD",
                            speed,
                        ))
                # update previous direction
                retro_events.setdefault(name, {})["prev_direction"] = direction
        msg += f"positions : retro : {retro_events}\n"
    notify.debug(
        msg,
        source="retro",
        route=["terminal"],
    )
