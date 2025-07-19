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
# pl : 5:6 m   : every 12 months     : 0.004 : 0.036388889  # 10" / d
import swisseph as swe
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore
from typing import List, Optional, Tuple  # Dict
from ui.helpers import _object_name_to_code as objcode
from sweph.swetime import jd_to_custom_iso as jdtoiso
from functools import lru_cache


station_speed = {  # stationary speed
    2: 0.1,  # 0.08333, "me"
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


def retro_marker(speed: float, threshold: float) -> str:
    if abs(speed) < threshold:
        return "S"
    return "R" if speed < 0 else "D"


def calculate_retro(event: Optional[str] = None):
    """calculate retro stations & direction for event"""
    # grab existing positions with lon speed & calculate direction & stations
    app = Gtk.Application.get_default()
    notify = app.notify_manager
    # msg = f"event {event}\n"
    msg = "\n"
    events: List[str] = [event] if event else ["e1", "e2"]
    if "e2" in events and not app.e2_sweph.get("jd_ut"):
        # skip e2 if no datetime / julian day utc set = user not interested in e2
        events.remove("e2")
        msg += "e2 removed\n"
    for event_name in events:
        # grab positons & selected objects based on event
        if event_name in ("e1", "e2"):
            pos = getattr(app, f"{event_name}_positions")
            jd_ut = pos.get("jd_ut")
        elif event_name == "p3":
            pos = getattr(app, "p3_pos")
            jd_ut = next(d["jd_ut"] for d in pos if d.get("name") == "p3jdut")
        # msg += f"{event} jdut curr : {jdtoiso(jd_ut)}\n"
        objs = app.selected_objects_e1 if event == "e1" else app.selected_objects_e2
        use_mean_node = app.chart_settings["mean node"]
        retro_data = []
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


@lru_cache(maxsize=128)
def lon_speed(body: int, jd_ut: float) -> float:
    # calculate lon speed in degree/day
    app = Gtk.Application.get_default()
    result = swe.calc_ut(jd_ut, body, app.sweph_flag)
    # longitude speed
    return result[0][3]


def refine_root(body: int, bracket: Tuple[float, float]) -> float:
    # fast exact direction change calculation
    a, b = bracket
    # ensure a < b for consistent processing
    if a > b:
        a, b = b, a
    fa = lon_speed(body, a)
    # bisect for guaranted convergence
    for _ in range(20):
        mid = (a + b) / 2
        if (b - a) / 2 < 1e-7:
            return mid
        fmid = lon_speed(body, mid)
        if fa * fmid < 0:
            b = mid
        else:
            a = mid
            fa = fmid
    return (a + b) / 2


@lru_cache(maxsize=128)
def find_closest_station(body: int, start_jd: float, step: float) -> Optional[float]:
    # search iteratively for nearest station from start date
    # shift start slightly to avoid missing stations
    t = start_jd + (1e-5 * (1 if step > 0 else -1))
    s0 = lon_speed(body, t)
    # search max 3 years
    max_iter = int(365.25 * 3 / abs(step))
    for _ in range(max_iter):
        t += step
        s = lon_speed(body, t)
        # sign change indicates stationary planet
        if s0 * s <= 0:
            return refine_root(body, (t - step, t))
        s0 = s
    return None


@lru_cache(maxsize=32)
def find_stations(body: int, jd: float) -> Tuple[Optional[float], Optional[float], str]:
    # find previous & next station, use cache to avoid recalculation
    retro_length = retro_days.get(body, 180.0)
    step = retro_length / 20.0
    # step = min(retro_length / 20.0, 0.5)
    threshold = station_speed[body]
    curr_speed = lon_speed(body, jd)
    curr_dir = retro_marker(curr_speed, threshold)
    # find previous & next station
    s_prev = find_closest_station(body, jd, -step)
    s_next = find_closest_station(body, jd, step)
    return s_prev, s_next, curr_dir
