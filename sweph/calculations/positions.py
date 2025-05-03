# sweph/calculations/positions.py
# ruff: noqa: E402, E701
# import gi

# gi.require_version("Gtk", "4.0")
# from gi.repository import Gtk  # type: ignore
import swisseph as swe
from user.settings import OBJECTS  # , CHART_SETTINGS
from ui.mainpanes.panetables import pane_tables


def calculate_positions(
    event, sweph, objs, use_mean_node, sweph_flag, flags=None, _notify=None
):
    """calculate planetary positions & present in a table as stack widget"""
    # print(f"positions : sweph : {sweph}\n\tselobjs : {objs}")
    if not sweph or "jd_ut" not in sweph or not objs:
        return {}
    # swe.calc_ut() with topocentric flag needs topographic location
    if (
        flags
        and "topocentric" in flags
        and all(k in sweph for k in ("lon", "lat", "alt"))
    ):
        """coordinates are reversed here : lon lat alt"""
        # print("found 'topocentric' flag")
        swe.set_topo(sweph["lon"], sweph["lat"], sweph["alt"])
    jd_ut = sweph.get("jd_ut")
    # print(f"jd_ut : {jd_ut}")
    if jd_ut is None:
        return {}
    # print(f"objs : {objs}")
    positions = {}
    for obj in objs:
        # print(f"positions : obj : {obj}")
        code, name = object_name_to_code(obj, use_mean_node)
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
    # positions["event"] = event
    keys = [k for k in positions.keys() if isinstance(k, int)]
    keys.sort()
    positions_ordered = {"event": event}
    for k in keys:
        positions_ordered[k] = positions[k]
    positions.clear()
    positions.update(positions_ordered)
    # call tables & pass _notify
    pane_tables(positions, _notify)
    return positions


def object_name_to_code(name: str, use_mean_node: bool) -> int | None:
    """get object name as int"""
    if name == "true node" and use_mean_node:
        name = "mean node"
    for key, obj in OBJECTS.items():
        if obj[1] == name:
            # return int & short name
            return key, obj[0]
    if name == "mean node":
        # return mean node int & same short name as true node
        return 10, "ra"
    return None
