# sweph/calculations/retro.py
# ruff: noqa: E402, E701
# retro periods : (max & average speed)
# legend :
#     Rl - average length of retro period
#     f - (yearly) frequency
#     as - average speed
#     ms - max speed
# obj : Rl : f : as : ms
# me : 21 d : 3 times a year : 1.607 : 1.6667  # (6') 5' / d : 24 h
# ve : 40:44 d : every 18 months : 1.174 : 1.25  # 3' / d : 3 d 4 h
# ma : 60:80 d : every 26 months : 0.524 : 0.7833  # 90" / d : 6 d 12 h
# ju : 4 m : every 13 months : 0.083 : 0.2333  # 60" / d : 7 d
# sa : 4.5 m : every 12 1/2 months : 0.033 : 0.12472  # 60" /  : 7 d
# ur : 5 m : every 12 months : 0.012 : 0.05722  # 20" / d : 6 d 12 h
# ne : 5 m 6 d : every 12 months : 0.006 : 0.038055556  # 10" / d
# pl : 5:6 m : every 12 months : 0.004 : 0.036388889  # 10" / d
import swisseph as swe
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore
from sweph.swetime import jd_to_custom_iso as jdtoiso
from typing import List, Optional
from ui.helpers import _object_name_to_code as objcode


station_speed = {  # average speed in deg/day (wikipedia) : su & mo never retro
    # station # average , maximum speed (astro wiki)
    "me": 0.1,  # 0.08333,
    "ve": 0.05,
    "ma": 0.025,
    "ju": 0.016666667,
    "sa": 0.016666667,
    "ur": 0.005555556,
    "ne": 0.002777778,
    "pl": 0.002777778,
}
# average length of retro period
retro_days = {
    2: 21.0,  # "me"
    3: 42.0,  # "ve"
    4: 70.0,  # "ma"
    5: 120.0,  # "ju"
    6: 135.0,  # "sa"
    7: 150.0,  # "ur"
    8: 156.0,  # "ne"
    9: 168.0,  # "pl"
}


def retro_marker(speed: float, threshold: float) -> str:
    if abs(speed) < threshold:
        return "S"
    return "R" if speed < 0 else "D"


def calculate_retro(event: Optional[str] = None):
    """calculate retro station & direction for event"""
    # grab existing positions with lon speed & calculate retro & stations
    app = Gtk.Application.get_default()
    notify = app.notify_manager
    msg = f"event {event}\n"
    events: List[str] = [event] if event else ["e1", "e2"]
    if "e2" in events and not app.e2_sweph.get("jd_ut"):
        # skip e2 if no datetime / julian day utc set = user not interested in e2
        events.remove("e2")
        msg += "e2 removed\n"
    for event in events:
        # grab positons & selected objects based on event
        if event in ("e1", "e2"):
            pos = getattr(app, f"{event}_positions")
            jd_ut = pos["jd_ut"]
        elif event == "p3":
            pos = getattr(app, "p3_pos")
            jd_ut = next(d["jd_ut"] for d in pos if d.get("name") == "p3jdut")
        msg += f"{event} jdut curr : {jdtoiso(jd_ut)}\n"
        # msg += f"retro [{event}] :\n\tjdut : {jd_ut}\n\tpos : {pos}\n"
        objs = app.selected_objects_e1 if event == "e1" else app.selected_objects_e2
        use_mean_node = app.chart_settings["mean node"]
        retro_data = []
        for obj in objs:
            code, name = objcode(obj, use_mean_node)
            if not code or name not in station_speed:
                continue
            speed = None
            threshold = station_speed[name]
            # e1 / e2 search in pos (dict) for matching name
            if isinstance(pos, dict):
                for v in pos.values():
                    if (
                        isinstance(v, dict)
                        and v.get("name") == name
                        and "lon speed" in v
                    ):
                        speed = v["lon speed"]
                        break
            # p3 search in pos (list) for matching name
            elif isinstance(pos, list):
                for v in pos:
                    if (
                        isinstance(v, dict)
                        and v.get("name") == name
                        and "lon speed" in v
                    ):
                        speed = v["lon speed"]
                        break
            if speed is None:
                continue
            state = retro_marker(speed, threshold)
            # station previous & next
            S_prev, S_next, dir = find_direction_flip(code, jd_ut)
            # todo debug
            station_prev = jdtoiso(S_prev) if S_prev is not None else None
            station_next = jdtoiso(S_next) if S_next is not None else None
            retro_data.append({
                "event": event,
                "name": name,
                "state": state,
            })
            # print(f"RETRO :\n\tprev : {jdtoiso(S_prev)}\n\tnext : {jdtoiso(S_next)}")
            # msg += f"{name} : {speed:9.5f} | state : {state}\n"
            msg += f"retro {event} : {name} [{dir}] prev={station_prev} next={station_next}\n"
        # msg += f"retrodata : {retro_data}\n"
    notify.debug(
        msg,
        source="retro",
        route=["terminal"],
    )


def lon_speed(body: int, jd_ut: float) -> float:
    # calculate lon speed in degree/day
    app = Gtk.Application.get_default()
    _, _, _, speed_lon, _, _ = swe.calc_ut(jd_ut, body, app.sweph_flag)[0]
    return speed_lon


def refine_root(body: int, bracket: tuple[float, float], tol: float) -> float:
    # fast exact direction change calculation
    a, b = bracket
    fa = lon_speed(body, a)
    fb = lon_speed(body, b)
    # bisect until interval cca 1 minute
    while (b - a) > tol:
        m = 0.5 * (a + b)
        fm = lon_speed(body, m)
        if fa * fm <= 0:
            b, fb = m, fm
        else:
            a, fa = m, fm
    # secant polish (3 iterations)
    for _ in range(3):
        fa = lon_speed(body, a)
        fb = lon_speed(body, b)
        denom = fb - fa
        if denom == 0:
            break
        m = (a * fb - b * fa) / denom
        if not (a < m < b):
            break
        fm = lon_speed(body, m)
        if fa * fm <= 0:
            b, fb = m, fm
        else:
            a, fa = m, fm
    return 0.5 * (a + b)


last_brackets = {}


def find_direction_flip(
    body: int, jd: float, tol: float = 1e-5
) -> tuple[Optional[float], Optional[float], Optional[str]]:
    # find previous & next station
    retro_length = retro_days.get(body, 180.0)
    step = min(retro_length / 20.0, 0.5)
    eps = 0.01
    # reuse last bracket
    prev_bracket, next_bracket = last_brackets.get(body, (None, None))
    # prev_bracket = None
    # search previous station
    if not prev_bracket:
        start, end = jd - retro_length, jd
        # prev_bracket = None
        s0 = lon_speed(body, start)
        t = start + step
        while t <= end:
            s = lon_speed(body, t)
            if s0 * s <= 0:
                prev_bracket = (t - step, t)
                break
            s0 = s
            t += step
    # check exact boundary at end
    if not prev_bracket and s0 * lon_speed(body, end) <= 0:
        prev_bracket = (end - eps, end)
    # fallback tiny
    if not prev_bracket:
        prev_bracket = (jd - eps, jd)
    t_prev = refine_root(body, prev_bracket, tol) if prev_bracket else None
    # search next station
    if not next_bracket:
        # next_bracket = None
        start2, end2 = jd, jd + retro_length
        s0 = lon_speed(body, start2)
        t = start2 + step
        while t <= end2:
            s = lon_speed(body, t)
            if s0 * s <= 0:
                next_bracket = (t - step, t)
                break
            s0 = s
            t += step
    # check exact boundary at end 2
    if not next_bracket and s0 * lon_speed(body, end2) <= 0:
        next_bracket = (end2 - eps, end2)
    # fallback tiny
    if not next_bracket:
        next_bracket = (jd, jd + eps)
    t_next = refine_root(body, next_bracket, tol) if next_bracket else None
    last_brackets[body] = {prev_bracket, next_bracket}
    speed_curr = lon_speed(body, jd)
    dir_curr = "D" if speed_curr > 0 else "R" if speed_curr < 0 else "S"
    return t_prev, t_next, dir_curr
