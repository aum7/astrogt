# sweph/calculations/positions.py
# ruff: noqa: E402, E701
import swisseph as swe
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore
from typing import Dict, List, Optional, Tuple
from user.settings import OBJECTS
from ui.mainpanes.panetables import update_tables


def calculate_positions(event: Optional[str] = None) -> Dict:
    """calculate planetary positions for one or both events"""
    # get app
    app = Gtk.Application.get_default()
    _notify = app.notify_manager
    events: List[str] = ["e1", "e2"] if event is None else [event]
    _notify.debug(
        f"where is our sweph & objs ?\n\tapp : {app}\n\tevent(s) : {events}",
        source="positions",
        route=["none"],
    )
    for event in events:
        sweph = app.e1_sweph if event == "e1" else app.e2_sweph
        objs = app.selected_objects_e1 if event == "e1" else app.selected_objects_e2
        # print(f"positions : sweph : {sweph}\n\tselobjs : {objs}")
        if not sweph or "jd_ut" not in sweph or not objs:
            _notify.debug(
                f"missing :\n\tsweph : {sweph}\n\tobjs : {objs}",
                source="positions",
                route=["terminal"],
            )
            continue
        # swe.calc_ut() with topocentric flag needs topographic location
        if (
            app.selected_flags
            and "topocentric" in app.selected_flags
            and all(k in sweph for k in ("lon", "lat", "alt"))
        ):
            """coordinates are reversed here : lon lat alt"""
            # print("found 'topocentric' flag")
            swe.set_topo(sweph["lon"], sweph["lat"], sweph["alt"])
        use_mean_node = app.chart_settings["mean node"]
        sweph_flag = app.sweph_flag
        jd_ut = sweph.get("jd_ut")
        # print(f"jd_ut : {jd_ut}")
        if jd_ut is None:
            return {}
        # print(f"objs : {objs}")
        positions = {}
        for obj in objs:
            # print(f"positions : obj : {obj}")
            if obj:
                code, name = object_name_to_code(obj, use_mean_node)
                _notify.debug(
                    f"iterating objs : {code} | {obj}",
                    source="positions",
                    route=["none"],
                )
            if code is None:
                continue
            # calc_ut() returns array of 6 floats + error string :
            # longitude, latitude, distance
            # lon speed, lat speed, dist speed
            try:
                # we also need flags
                result = swe.calc_ut(jd_ut, code, sweph_flag)
                # print(f"positions : result : {result}")
                data = result[0] if isinstance(result, tuple) else result
                positions[code] = {
                    "name": name,
                    "lon": data[0],
                    "lat": data[1],
                    "dist": data[2],
                    "lon speed": data[3],
                    "lat speed": data[4],
                    "dist speed": data[5],
                }
            except Exception as e:
                _notify.warning(
                    f"swe.calc_ut() failed\n\tdata {positions[code]} error :\n\t{e}",
                    source="positions",
                    route=["terminal"],
                )
        keys = [k for k in positions.keys() if isinstance(k, int)]
        keys.sort()
        positions_ordered = {"event": event}
        for k in keys:
            positions_ordered[str(k)] = positions[k]
        positions.clear()
        positions.update(positions_ordered)
        # call tables & serve positions
    _notify.debug(
        f"sending positions : {positions}",
        source="positions",
        route=["none"],
    )
    update_tables(positions)
    return positions


def object_name_to_code(name: str, use_mean_node: bool) -> Tuple[Optional[int], str]:
    """get object name as int"""
    if name == "true node" and use_mean_node:
        name = "mean node"
    for code, obj in OBJECTS.items():
        if obj[1] == name:
            # return int & short name
            # print(f"objnametocode : {code} | {obj[0]}")
            return code, obj[0]
    if name == "mean node":
        # return mean node int & same short name as true node
        # print(f"objnametocode : {name}")
        return 10, "ra"
    # print("objnametocode : returned none & ''")
    return None, ""
