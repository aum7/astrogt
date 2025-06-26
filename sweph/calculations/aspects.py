# sweph/calculations/aspects.py
# ruff: noqa: E402, E701
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore
from typing import List, Optional, Dict, Any
from ui.fonts.glyphs import ASPECTS


def calculate_aspects(event: Optional[str] = None, positions: Dict[str, Any] = {}):
    """calculate aspectarian for one or both events"""
    app = Gtk.Application.get_default()
    notify = app.notify_manager
    # event 1 data is mandatory
    if not app.e1_sweph.get("jd_ut"):
        notify.warning(
            "missing event one data needed for aspectarian\n\texiting ...",
            source="aspects",
            route=["terminal", "user"],
        )
        return
    events: List[str] = [event] if event else ["e1", "e2"]
    if "e2" in events and not app.e2_sweph.get("jd_ut"):
        # skip e2 if no datetime / julian day utc set = user not interested in e2
        events.remove("e2")
    notify.debug(
        f"event(s) : {events} | positions : {positions}",
        source="aspects",
        route=["none"],
    )
    positions = {k: v for k, v in positions.items() if k.isdigit()}
    orb = 1.5
    obj_names, aspect_matrix = pairwise_aspects(positions, orb)
    data = {
        "obj names": obj_names,
        "matrix": aspect_matrix,
    }
    app.signal_manager._emit("aspects_changed", event, data)
    notify.debug(
        f"aspects calculated for {event}",
        source="aspects",
        route=["none"],
    )


def angle_diff(a: float, b: float) -> float:
    d = (a - b) % 360
    if d > 180:
        d -= 360
    return d


def is_applying(lon1, speed1, lon2, speed2, angle):
    diff = angle_diff(lon1, lon2)
    orb = diff - angle
    delta_speed = speed2 - speed1
    return orb * delta_speed < 0


def nearest_major_aspect(angle: float, orb: float):
    """get major aspects within defined orb"""
    for aspect_angle, (glyph, aspect_name) in ASPECTS.items():
        diff = min(abs(angle - aspect_angle), abs(360 - abs(angle - aspect_angle)))
        if diff <= orb:
            return aspect_angle, glyph, aspect_name, diff
    return None


def pairwise_aspects(positions: Dict[str, Any], orb: float):
    draw_order = ["mo", "me", "ve", "su", "ma", "ju", "sa", "ur", "ne", "pl", "ra"]
    objs_map = {v["name"]: v for k, v in positions.items()}
    obj_names = [name for name in draw_order if name in objs_map]
    keys = [k for name in obj_names for k, v in positions.items() if v["name"] == name]
    num = len(obj_names)
    matrix = []
    for i in range(num):
        row = []
        obj1 = positions[keys[i]]
        for j in range(num):
            obj2 = positions[keys[j]]
            if i == j:
                # both obj are same planet : needed for matrix consistency only
                row.append({
                    "obj1": obj1["name"],
                    "obj2": obj2["name"],
                    "angle": None,
                    "major": False,
                    "aspect": None,
                    "aspect angle": None,
                    "glyph": "",
                    "orb": None,
                    "applying": None,
                })
                continue
            lon1, lon2 = obj1["lon"], obj2["lon"]
            speed1, speed2 = obj1["lon speed"], obj2["lon speed"]
            angle = angle_diff(lon1, lon2)
            applying = None
            asp_angle, glyph, asp_name, orb_actual = None, "", "", None
            major = False
            maj = nearest_major_aspect(angle, orb)
            if maj:
                asp_angle, glyph, asp_name, orb_actual = maj
                applying = is_applying(lon1, speed1, lon2, speed2, asp_angle)
                major = True
            row.append({
                "obj1": obj1["name"],
                "obj2": obj2["name"],
                "angle": round(angle, 2),
                "major": major,
                "aspect": asp_name if major else None,
                "aspect angle": asp_angle if major else None,
                "glyph": glyph if major else "",
                "orb": round(orb_actual, 1)
                if orb_actual is not None and major
                else None,
                "applying": applying if major else None,
            })
            # if (obj1["name"] == "ve" and obj2["name"] == "mo") or (
            #     obj1["name"] == "mo" and obj2["name"] == "ve"
            # ):
            #     print(
            #         f"row {i} {obj1['name']}->{obj2['name']}: "
            #         f"angle={round(angle, 2) if i != j else None} "
            #         f"major={major} "
            #         f"aspect={asp_name if major else None} "
            #         f"aspect angle={asp_angle if major else None} "
            #         f"orb={round(orb_actual, 1) if orb_actual is not None and major else None} "
            #         f"applying={applying if major else None} "
            #         f"lon1={lon1:.2f} speed1={speed1:.4f} "
            #         f"lon2={lon2:.2f} speed2={speed2:.4f}"
            #     )
        matrix.append(row)
    return obj_names, matrix


def connect_signals_aspects(signal_manager):
    """update aspects when positions change"""
    signal_manager._connect("positions_changed", calculate_aspects)
