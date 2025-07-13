# sweph/calculations/retro.py
# ruff: noqa: E402, E701
# import swisseph as swe
# import numpy as np
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore

# from collections import defaultdict  # will add attr if missing
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
        # jd_ut = 0.0
        pos = ()
        if event == "e1":
            pos = getattr(app, "e1_positions")
            # jd_ut = pos.get("jd_ut") if isinstance(pos, dict) else None
        elif event == "e2":
            pos = getattr(app, "e2_positions")
            # jd_ut = pos.get("jd_ut") if isinstance(pos, dict) else None
        elif event == "p3":
            pos = getattr(app, "p3_pos")
            # jd_ut = next(
            #     (o["jd_ut"] for o in pos if isinstance(o, dict) and "jd_ut" in o)
            # )
        # msg += f"retro [{event}] :\n\tjdut : {jd_ut}\n\tpos : {pos}\n"
        objs = app.selected_objects_e1 if event == "e1" else app.selected_objects_e2
        use_mean_node = app.chart_settings["mean node"]
        # threshold_pct = 0.02  # 2 %
        retro_data = []
        prev_dir = ""
        dir = ""
        for obj in objs:
            # retro_state = ""
            code, name = objcode(obj, use_mean_node)
            if code is None:
                continue
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
                # threshold = abs(avg) * threshold_pct
                # is_station = abs(speed) < threshold
                dir = "D" if speed > 0 else ("R" if speed < 0 else "S")
                prev_dir_ = prev_dir
                print(f"{name} : dir : {dir} | prevdir {prev_dir_}")
                prev_dir = dir
                # retro_data.append({"name": name, "dir": dir})
                # prev_dir = retro_data[name].get("prevdir")
                # print(f"{name} = {dir} - prevdir : {prev_dir}\n")
                # retro_state = dir
                # print(f"\tRETRO : state : {retro_state} | prevdir : {prev_dir}")
                # if dir:
                # check for stationary retrograde (SR) or stationary direct (SD)
                # if dir == "R":
                #     retro_state = dir
                #     if prev_dir == "D":
                #         print(f"{prev_dir} > {dir} GONE RETRO")
                #         if is_station:
                #             retro_state = "SR"
                #     # retro_data[name] = {"state": retro_state}
                # elif dir == "D":
                #     retro_state = dir
                #     if prev_dir == "R":
                #         print(f"{prev_dir} > {dir} GONE DIRECT")
                #         if is_station:
                #             retro_state = "SD"
                # update previous direction
            # retro_data[name] = {
            #     # "state": retro_state,
            #     # "station": is_station,
            #     "prevdir": prev_dir,
            #     # "dir": dir,
            # }
            # print(f"RETRO : state : {retro_state}")
            # msg += (
            #     f"{name} : {speed:9.5f} | S : {is_station} | "
            #     f"prevdir : {prev_direction} | dir : {direction} || "
            #     f"state : {retro_state}\n"
            # )
        # msg += f"retrodata : {retro_data}\n"
    notify.debug(
        msg,
        source="retro",
        route=["terminal"],
    )
