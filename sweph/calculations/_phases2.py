# sweph/calculations/aspects.py
# ruff: noqa: E402, E701
import math
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore

# import helpers from aspects
from .aspects import (
    angle_diff,  # shortest signed angle -180..180
    nearest_major_aspect,
    is_applying,
)

# same draw order as aspects (fastest -> slowest)
DRAW_ORDER = ["mo", "me", "ve", "su", "ma", "ju", "sa", "ur", "ne", "pl", "ra"]


def angle_fwd(a: float, b: float) -> float:
    """forward angle a->b in 0..360"""
    return (b - a) % 360.0


def phases_matrix(objs_map: list[str], pos_map: dict, aspect_orb: float = 3.0):
    """build phases/aspects hybrid matrix"""
    n = len(objs_map)
    matrix = []
    # prepare speeds
    speeds = {name: pos_map[name]["lon speed"] for name in objs_map}
    for i in range(n):
        row_name = objs_map[i]
        row_obj = pos_map[row_name]
        row = []
        cumulative = 0.0  # per-row cumulative (phase cells only)
        for j in range(n):
            col_name = objs_map[j]
            col_obj = pos_map[col_name]
            if i == j:
                row.append({
                    "type": "diag",
                    "obj1": row_name,
                    "obj2": col_name,
                })
                continue
            lon_row = row_obj["lon"]
            lon_col = col_obj["lon"]
            speed_row = row_obj["lon speed"]
            speed_col = col_obj["lon speed"]
            if i > j:
                # phase cell (row slower than column in draw_order fast->slow)
                slower = row_name
                faster = col_name
                lon_slow = lon_row
                lon_fast = lon_col
                raw = angle_fwd(lon_slow, lon_fast)
                if raw <= 180.0:
                    separation = raw
                    phase = "up"
                    cumulative = (cumulative + separation) % 360.0
                else:
                    separation = 360.0 - raw
                    phase = "dn"
                    cumulative = (cumulative - separation) % 360.0
                cell = {
                    "type": "phase",
                    "slower": slower,
                    "faster": faster,
                    "raw": round(raw, 2),
                    "separation": round(separation, 2),
                    "phase": phase,
                    "cumulative": round(cumulative, 2),
                }
                row.append(cell)
            else:
                # aspect cell (above diagonal)
                ang = angle_diff(lon_row, lon_col)
                maj = nearest_major_aspect(abs(ang), aspect_orb)
                if maj:
                    asp_angle, glyph, asp_name, orb_actual = maj
                    signed_asp_angle = math.copysign(asp_angle, ang)
                    applying = is_applying(
                        lon_row, speed_row, lon_col, speed_col, signed_asp_angle
                    )
                    cell = {
                        "type": "aspect",
                        "obj1": row_name,
                        "obj2": col_name,
                        "angle": round(ang, 2),
                        "major": True,
                        "aspect": asp_name,
                        "aspect angle": asp_angle,
                        "glyph": glyph,
                        "orb": round(orb_actual, 2),
                        "applying": applying,
                    }
                else:
                    cell = {
                        "type": "aspect",
                        "obj1": row_name,
                        "obj2": col_name,
                        "angle": round(ang, 2),
                        "major": False,
                        "aspect": None,
                        "aspect angle": None,
                        "glyph": "",
                        "orb": None,
                        "applying": None,
                    }
                row.append(cell)
        matrix.append(row)
    return objs_map, matrix, speeds


def calculate_phases(event: str):
    """calculate phases matrix for one event"""
    app = Gtk.Application.get_default()
    notify = app.notify_manager
    if event not in ("e1", "e2"):
        return
    pos = getattr(app, f"{event}_positions", None)
    if not pos or not isinstance(pos, dict):
        notify.error(
            f"missing positions for {event} : phases abort",
            source="phases",
            route=["terminal"],
        )
        return
    # map by name (only numeric keys)
    pos_map = {v["name"]: v for k, v in pos.items() if isinstance(k, int)}
    objs_map = [name for name in DRAW_ORDER if name in pos_map]
    if not objs_map:
        notify.error(
            f"no objects available for {event}",
            source="phases",
            route=["terminal"],
        )
        return
    obj_names, matrix, speeds = phases_matrix(objs_map, pos_map, aspect_orb=3.0)
    phases_data = {
        "obj names": obj_names,
        "matrix": matrix,
        "speeds": speeds,
    }
    app.signal_manager._emit("phases_changed", event, phases_data)
    notify.debug(
        f"phases updated for {event}",
        source="phases",
        route=[""],
    )


def connect_signals_phases(signal_manager):
    """update phases when positions change"""
    signal_manager._connect("positions_changed", calculate_phases)
