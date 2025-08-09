# sweph/calculations/aspects.py
# ruff: noqa: E402, E701
# import math
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore

# fixed slowest->fastest order (filter later for available objects)
SLOW_ORDER = ["pl", "ne", "ur", "sa", "ra", "ju", "ma", "su", "ve", "me", "mo"]
# SLOW_ORDER = ["pl", "ne", "ur", "sa", "ju", "ma", "su", "ve", "me", "mo", "ra"]


def angle_diff_0_360(a: float, b: float) -> float:
    """angular distance from a to b forward 0..360"""
    return (b - a) % 360.0


def phase_pair(lon_slow: float, speed_slow: float, lon_fast: float, speed_fast: float):
    """compute raw angle, signed phase (+/-) and separation <=180"""
    raw = angle_diff_0_360(lon_slow, lon_fast)  # 0..360
    delta_speed = speed_fast - speed_slow
    if raw <= 180.0:
        separation = raw
        angle = "+"
    else:
        separation = 360.0 - raw
        angle = "-"
    return raw, separation, angle, delta_speed


def calculate_phases(event: str):
    """calculate compound phase table for one event"""
    app = Gtk.Application.get_default()
    notify = app.notify_manager
    if event not in ("e1", "e2"):
        return
    pos = getattr(app, f"{event}_positions", None)
    if not pos:
        notify.error(
            f"missing positions for {event} : compound abort",
            source="compound",
            route=["terminal", "user"],
        )
        return
    # build name -> obj map (only numeric keys)
    pos_map = {v["name"]: v for k, v in pos.items() if isinstance(k, int)}
    # filter slow order by available names
    ordered = [n for n in SLOW_ORDER if n in pos_map]
    # collect pairs (unique slower->faster)
    pairs = []
    for i in range(len(ordered)):
        slow = ordered[i]
        lon_slow = pos_map[slow]["lon"]
        speed_slow = pos_map[slow]["lon speed"]
        for j in range(i + 1, len(ordered)):
            fast = ordered[j]
            lon_fast = pos_map[fast]["lon"]
            speed_fast = pos_map[fast]["lon speed"]
            raw, sep, phase, speed = phase_pair(
                lon_slow, speed_slow, lon_fast, speed_fast
            )
            pairs.append({
                "slower": slow,
                "faster": fast,
                "separation": round(sep, 2),
                "raw": round(raw, 2),
                "phase": phase,
                "delta_speed": speed,
            })
    # build cumulative waves (cyclic indices)
    # for each planet from third onward (index >=2) sum all separations
    # among subset ordered[0..k]
    # preindex separations for speed
    pair_sep = {}
    for p in pairs:
        pair_sep[(p["slower"], p["faster"])] = p["separation"]
    waves = []
    for k in range(2, len(ordered)):
        members = ordered[0 : k + 1]
        s = 0.0
        for i in range(len(members)):
            for j in range(i + 1, len(members)):
                slow = members[i]
                fast = members[j]
                s += pair_sep.get((slow, fast), 0.0)
        waves.append({
            "planet": ordered[k],
            "members": members.copy(),
            "sum": round(s, 2),
        })
    phases_data = {
        "ordered": ordered,
        "pairs": pairs,
        "waves": waves,
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
