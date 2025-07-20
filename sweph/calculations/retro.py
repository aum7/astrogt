# sweph/calculations/retro.py
# ruff: noqa: E402, E701
# retro periods
# legend :
#     Rl - average length of retro period
#     f - (yearly) frequency
#     as - average speed
#     ms - max speed
# obj : Rl     : f                   : as    : ms
# me : 21 d    : 3 times a year      : 1.607 : 1.6667  # (6') 5' / d : 24 h
# ve : 40-44 d : every 18 months     : 1.174 : 1.25  # 3' / d : 3 d 4 h
# ma : 60-80 d : every 26 months     : 0.524 : 0.7833  # 90" / d : 6 d 12 h
# ju : 4 m     : every 13 months     : 0.083 : 0.2333  # 60" / d : 7 d
# sa : 4.5 m   : every 12 1/2 months : 0.033 : 0.12472  # 60" /  : 7 d
# ur : 5 m     : every 12 months     : 0.012 : 0.05722  # 20" / d : 6 d 12 h
# ne : 5 m 6 d : every 12 months     : 0.006 : 0.038055556  # 10" / d
# pl : 5-6 m   : every 12 months     : 0.004 : 0.036388889  # 10" / d
import swisseph as swe
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore
from typing import List, Optional, Tuple, Dict
from ui.helpers import _object_name_to_code as objcode
from sweph.swetime import jd_to_custom_iso as jdtoiso


station_speed = {  # stationary speed
    2: 0.08333,  # "me"
    3: 0.05,  # "ve"
    4: 0.025,  # "ma"
    5: 0.016666667,  # "ju"
    6: 0.016666667,  # "sa"
    7: 0.005555556,  # "ur"
    8: 0.002777778,  # "ne"
    9: 0.002777778,  # "pl"
}
retro_days = {  # average length of retro period
    2: 21.0,  # "me"
    3: 42.0,  # "ve"
    4: 70.0,  # "ma"
    5: 120.0,  # "ju"
    6: 135.0,  # "sa"
    7: 150.0,  # "ur"
    8: 156.0,  # "ne"
    9: 168.0,  # "pl"
}

last_stations: Dict[int, Tuple[Optional[float], Optional[float]]] = {}


def retro_marker(speed: float, threshold: float) -> str:
    if abs(speed) < threshold:
        return "S"
    return "R" if speed < 0 else "D"


def calculate_retro(event: Optional[str] = None):  # -> List[Dict]:
    """calculate retro stations & direction for event"""
    # grab existing positions with lon speed & calculate direction & stations
    app = Gtk.Application.get_default()
    notify = app.notify_manager
    retro_data = []
    msg = f"event {event}\n"
    events: List[str] = [event] if event else ["e1", "e2"]
    if "e2" in events and not app.e2_sweph.get("jd_ut"):
        # skip e2 if no datetime / julian day utc set = user not interested in e2
        events.remove("e2")
        msg += "e2 removed\n"
    for event_name in events:
        pos, jd_ut = None, None
        # grab positons & selected objects based on event
        if event_name in ("e1", "e2"):
            pos = getattr(app, f"{event_name}_positions")
            jd_ut = pos.get("jd_ut")
        elif event_name == "p3":
            pos = getattr(app, "p3_pos")
            jd_ut = next(d["jd_ut"] for d in pos if d.get("name") == "p3jdut")
        # msg += f"{event} jdut curr : {jdtoiso(jd_ut)}\n"
        if not jd_ut:
            notify.error(
                f"jdut for {event_name} not found : exiting ...",
                source="retro",
                route=["terminal"],
            )
            return
        objs = app.selected_objects_e1 if event == "e1" else app.selected_objects_e2
        use_mean_node = app.chart_settings["mean node"]
        retro_data.append({"event": event_name})
        for obj in objs:
            code, name = objcode(obj, use_mean_node)
            if code not in station_speed:
                continue
            speed = None
            # e1 / e2 search in pos (dict) for matching name
            if isinstance(pos, dict):
                v = pos.get(code)
                if isinstance(v, dict) and "lon speed" in v:
                    speed = v["lon speed"]
            # p3 search in pos (list) for matching name
            elif isinstance(pos, list):
                v = next((item for item in pos if item.get("name") == name), None)
                if v and "lon speed" in v:
                    speed = v["lon speed"]
            if speed is None:
                continue
            # station previous & next + current direction
            s_prev, s_next, direction = find_stations(code, jd_ut)
            if s_prev is None or s_next is None:
                msg += f"station for {name} not found\n"
                continue
            retro_data.append({
                "name": name,
                "prevstation": s_prev,
                "nextstation": s_next,
                "direction": direction,
            })
            if event == "p3":
                msg += (
                    f"[{event}] {name} [{direction}] :\nprev={jdtoiso(s_prev)} "
                    f"< curr={jdtoiso(jd_ut)} < next={jdtoiso(s_next)}\n"
                )
        # msg += f"retrodata : {retro_data}\n"
    # app.signal_manager._emit("retro_changed", "p3")
    notify.debug(
        msg,
        source="retro",
        route=["terminal"],
    )
    return retro_data


def lon_speed(body: int, jd_ut: float) -> float:
    # calculate lon speed in degree/day
    app = Gtk.Application.get_default()
    result = swe.calc_ut(jd_ut, body, app.sweph_flag)
    # longitude speed
    return result[0][3]


def refine_root(body: int, bracket: Tuple[float, float]) -> float:
    # fast exact direction change calculation
    a, b = bracket
    fa = lon_speed(body, a)
    fb = lon_speed(body, b)
    # bisect
    for _ in range(10):
        m = 0.5 * (a + b)
        fm = lon_speed(body, m)
        if fa * fm <= 0:
            b, fb = m, fm
        else:
            a, fa = m, fm

    # secant
    for _ in range(5):
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


def find_closest_station(body: int, start_jd: float, step: float) -> Optional[float]:
    # iterative search for nearest station
    eps = 0.01  # 1e-5
    t = start_jd + (eps * (1 if step > 0 else -1))
    s0 = lon_speed(body, t)
    max_iter = int(365.25 * 3 / abs(step))
    for _ in range(max_iter):
        t += step
        s = lon_speed(body, t)
        # sign change = station
        if s0 * s <= 0:
            return refine_root(body, (t - step, t))
        s0 = s
    return None


def find_stations(body: int, jd: float) -> Tuple[Optional[float], Optional[float], str]:
    # find previous & next station, use cache to avoid recalculation
    retro_length = retro_days.get(body, 180.0)
    step = min(retro_length / 20.0, 0.5)
    # tol = 1e-5
    # eps = 0.01
    threshold = station_speed[body]
    curr_speed = lon_speed(body, jd)
    curr_dir = retro_marker(curr_speed, threshold)
    # cached results first
    old_prev_s, old_next_s = last_stations.get(body, (None, None))
    if old_prev_s is not None and old_next_s is not None:
        if old_prev_s < jd < old_next_s:
            return old_prev_s, old_next_s, curr_dir
        # shift forward if past next
        if jd >= old_next_s:
            s_prev = old_next_s
            s_next = find_closest_station(body, s_prev, step)
        # shift backward if before prev
        elif jd <= old_prev_s:
            s_next = old_prev_s
            s_prev = find_closest_station(body, s_next, -step)
    else:
        # find previous & next station
        s_prev = find_closest_station(body, jd, -step)
        s_next = find_closest_station(body, jd, step)
    last_stations[body] = (s_prev, s_next)
    return s_prev, s_next, curr_dir


# def prev_station(
#     body: int, end_jd: float, retro_length: float, step: float, eps: float, tol: float
# ) -> Optional[float]:
#     start = end_jd - retro_length
#     s0 = lon_speed(body, start)
#     t = start + step
#     bracket = None
#     while t <= end_jd:
#         s = lon_speed(body, t)
#         if s0 * s <= 0:
#             bracket = (t - step, t)
#             break
#         s0, t = s, t + step
#     if not bracket and s0 * lon_speed(body, end_jd) <= 0:
#         bracket = (end_jd - eps, end_jd)
#     return refine_root(body, bracket, tol) if bracket else None


# def next_station(
#     body: int, start_jd: float, retro_length: float, step: float, eps: float, tol: float
# ) -> Optional[float]:
#     end = start_jd + retro_length
#     s0 = lon_speed(body, start_jd)
#     t = start_jd + step
#     bracket = None
#     while t <= end:
#         s = lon_speed(body, t)
#         if s0 * s <= 0:
#             bracket = (t - step, t)
#             break
#         s0, t = s, t + step
#     if not bracket and s0 * lon_speed(body, end) <= 0:
#         bracket = (end - eps, end)
#     return refine_root(body, bracket, tol) if bracket else None
