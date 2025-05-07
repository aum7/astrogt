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
    notify = app.notify_manager
    # event 1 data is mandatory
    if not app.e1_sweph.get("jd_ut"):
        notify.warning(
            "missing event one data needed for positions\n\texiting ...",
            source="positions",
            route=["terminal", "user"],
        )
        return {}
    positions = {}
    events: List[str] = [event] if event else ["e1", "e2"]
    if "e2" in events and not app.e2_sweph.get("jd_ut"):
        # skip e2 if no datetime / julian day utc set = user not interested in e2
        events.remove("e2")
    notify.debug(
        f"event(s) : {events}",
        source="positions",
        route=["none"],
    )
    for event in events:
        sweph = app.e1_sweph if event == "e1" else app.e2_sweph
        objs = app.selected_objects_e1 if event == "e1" else app.selected_objects_e2
        # print(f"positions : sweph : {sweph}\n\tselobjs : {objs}")
        if not sweph or "jd_ut" not in sweph or not objs:
            notify.debug(
                f"missing :\n\tsweph : {sweph}\n\tobjs : {objs}\n\texiting ...",
                source="positions",
                route=["terminal"],
            )
            return {}
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
        notify.debug(
            f"\n\tusemeannode : {use_mean_node}\n\tswephflag : {sweph_flag}\n\tjdut : {jd_ut}",
            source="positions",
            route=["none"],
        )
        for obj in objs:
            code, name = object_name_to_code(obj, use_mean_node)
            notify.debug(
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
            except swe.Error as e:
                notify.warning(
                    f"swe.calc_ut() failed\n\tdata {positions[code]} swe error :\n\t{e}",
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
    notify.debug(
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
            return code, obj[0]
    if name == "mean node":
        # return mean node int & same short name as true node
        return 10, "ra"
    return None, ""
