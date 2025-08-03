# sweph/calculations/p2.py
# ruff: noqa: E402
# secondary progression : a day for a year
import swisseph as swe
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore
from ui.helpers import _object_name_to_code as objcode, _decimal_to_hms as dectohms


def tuple_to_iso(jd):
    date = swe.revjul(jd, swe.GREG_CAL)
    y, m, d, h = date
    H, M, S = dectohms(h)
    return f"{y}-{m:02}-{d:02} {H:02}:{M:02}:{S:02}"


def calculate_p2(event: str):
    # calculate lunar returns before and after e2 (gives exact lunar month)
    app = Gtk.Application.get_default()
    notify = app.notify_manager
    msg = f"event {event}\n"
    # event 1 & 2 data is mandatory : natal / event & progression chart
    if not app.e1_sweph.get("jd_ut") or not app.e2_sweph.get("jd_ut"):
        notify.error(
            "missing event 1 or 2 data : exiting ...",
            source="p2",
            route=[""],
        )
        return
    # gather data
    e1_sweph = getattr(app, "e1_sweph", None)
    e2_sweph = getattr(app, "e2_sweph", None)
    if e1_sweph:
        e1_jd = e1_sweph.get("jd_ut")
    if e2_sweph:
        e2_jd = e2_sweph.get("jd_ut")
    sel_year = getattr(app, "selected_year_period", (365.2425, "gregorian"))
    # # substitute with exact lunar return calculations : before & after e2 datetime
    # sel_month = getattr(app, "selected_month_period", (27.321661, "sidereal"))
    YEARLENGTH = sel_year[0]
    # MONTHLENGTH = sel_month[0]
    if e1_jd and e2_jd:
        # period elapsed from birth in years : needs event 2 datetime
        period = e2_jd - e1_jd
        age_years = period / YEARLENGTH
    chart_sett = getattr(app, "chart_settings")
    use_mean_node = chart_sett.get("mean node")
    objs = getattr(app, "selected_objects_e2", None)
    e1_pos = getattr(app, "e1_positions", None)
    e1_houses = getattr(app, "e1_houses", None)
    # msg += f"e2objs : {objs}\n"
    if e1_pos:
        # get natal sun for solar return, p2 asc & mc arc calculation
        e1_su = next(
            (
                v["lon"]
                for v in e1_pos.values()
                if isinstance(v, dict) and v.get("name") == "su"
            )
        )
    if e1_houses:
        # get ascendant & midheaven
        e1_asc = e1_houses[1][0]
        e1_mc = e1_houses[1][1]
    if e1_su:
        if e1_mc:
            e1_mc_arc = (e1_mc - e1_su) % 360
        if e1_asc:
            e1_asc_arc = (e1_asc - e1_su) % 360
    # msg += (
    # f"e1mo : {e1_mo} | e1su : {e1_su} | "
    # f"e1ascarc : {e1_asc_arc} | e1mcarc : {e1_mc_arc}\n"
    # )
    # previous solar return : search x days back range
    prev_jd = e2_jd - YEARLENGTH - 0.1
    sr_prev_jd = swe.solcross_ut(e1_su, prev_jd, app.sweph_flag)
    # next lunar return
    next_jd = e2_jd
    sr_next_jd = swe.solcross_ut(e1_su, next_jd, app.sweph_flag)
    # calculate lunar month length
    sr_year = sr_next_jd - sr_prev_jd
    p2_diff = (age_years / sr_year) * sr_year
    p2_jd = e1_jd + p2_diff
    p2_date = tuple_to_iso(p2_jd)
    msg += p2_date
    p2_data: list[dict] = []
    # insert p2 date
    p2_data.append({"p2jdut": p2_jd})
    p2_data.append({"p2date": p2_date})
    try:
        result, e = swe.calc_ut(p2_jd, swe.SUN, app.sweph_flag)  # su lon
    except Exception as e:
        raise ValueError(f"p2 : sun position calculation failed\n\terror :\n\t{e}")
    p2_su = result[0]
    # msg += f"p2su : {p2_su}\n"
    # true asc & mc : experimental
    hsys = app.selected_house_sys
    if e1_sweph:
        try:
            _, ascmc = swe.houses_ex(
                p2_jd,
                e1_sweph["lat"],
                e1_sweph["lon"],
                hsys.encode("ascii"),
                app.sweph_flag,
            )
        except swe.Error as e:
            notify.error(
                f"cross points calculation failed\n\tswe error\n\t{e}",
                source="p2",
                route=["terminal"],
            )
    p2_tasc = ascmc[0]
    p2_tmc = ascmc[1]
    p2_data.append({"name": "tas", "lon": p2_tasc})
    p2_data.append({"name": "tmc", "lon": p2_tmc})
    # todo asc by tables of houses ???
    p2_asc = p2_su + e1_asc_arc
    # progress mc by solar arc : p2-su + (Nsu - Nmc)
    p2_mc = p2_su + e1_mc_arc
    # insert ascendant & midheaven with p1solarc
    p2_data.append({"name": "asc", "lon": p2_asc})
    p2_data.append({"name": "mc", "lon": p2_mc})
    # find positions on p2 date
    if objs:
        for obj in objs:
            code, name = objcode(obj, use_mean_node)
            if code is None:
                continue
            # calc_ut() returns array of 6 floats [0] + error string [1]:
            # longitude, latitude, distance, lon speed, lat speed, dist speed
            try:
                result = swe.calc_ut(p2_jd, code, app.sweph_flag)
                # print(f"positions with speeds & flag used : {result}")
                data = result[0] if isinstance(result, tuple) else result
                # print(f"name : {name} | lon : {data[0]}")
                p2_data.append({
                    "name": name,
                    "lon": data[0],
                    "lon speed": data[3],
                })
            except swe.Error as e:
                notify.error(
                    f"p2 positions calculation failed\n\tdata {p2_data[code]}\n\tswe error :\n\t{e}",
                    source="p2",
                    route=["terminal"],
                )
    for obj in p2_data:
        name = obj.get("name")
        if name in ("su", "mo", "asc", "mc", "p2jdut", "p2date"):
            continue
        if name:
            speed = obj.get("lon speed")
            msg += f"{name} : {speed}\n"
    # msg += f"p2data : {p2_data}\n"
    app.p2_pos = p2_data
    # emit signal
    app.signal_manager._emit("p2_changed", event)
    notify.debug(
        msg,
        source="p2",
        route=[""],
    )


def connect_signals_p2(signal_manager):
    # update progressions when data used changes
    signal_manager._connect("event_changed", calculate_p2)
    signal_manager._connect("settings_changed", calculate_p2)
