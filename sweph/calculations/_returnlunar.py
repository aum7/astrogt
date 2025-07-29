# sweph/calculations/lunarreturn.py
# ruff: noqa: E402, E701
import swisseph as swe
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore
from ui.helpers import _decimal_to_hms, _object_name_to_code as objcode


def calculate_lr(event: str):
    # tertiary direction calculation
    app = Gtk.Application.get_default()
    notify = app.notify_manager
    msg = f"event {event}\n"
    # event 1 & 2 data is mandatory : natal / event & progression chart
    # check against lumies since e1_sweph can have 0 objects (user-selectable)
    if not app.e1_sweph.get("jd_ut") or not app.e2_sweph.get("jd_ut"):
        notify.error(
            "missing event 1 or 2 data needed for p3 : exiting ...",
            source="p3",
            route=[""],
        )
        return
    # gather data
    # e1 positions for su / mo longitude crosscheck only
    e1_pos = getattr(app, "e1_positions", None)
    # sweph 3 members < pos upto 11 members
    e1_sweph = getattr(app, "e1_sweph", None)
    e2_sweph = getattr(app, "e2_sweph", None)
    if e1_pos:
        e1_jd = e1_pos.get("jd_ut")
    if e2_sweph:
        e2_jd = e2_sweph.get("jd_ut")
    sel_year = getattr(app, "selected_year_period", (365.256363, "sidereal"))
    sel_month = getattr(app, "selected_month_period", (27.321661, "sidereal"))
    YEARLENGTH = sel_year[0]
    MONTHLENGTH = sel_month[0]
    if e1_jd and e2_jd:
        # period elapsed from birth in years : needs event 2 datetime
        period = e2_jd - e1_jd
        delta_years = period / YEARLENGTH
        app.age_y = delta_years
        # how many lunar months
        delta_months = period / MONTHLENGTH
        app.age_m = delta_months
    objs = getattr(app, "selected_objects_e2", None)
    # above is repetetive code
    # solcross & mooncros always search forward
    # from period get fraction
    age_fract = delta_months % 1.0
    msg += f"agefract : {age_fract}\n"
    # convert to days by month for lunar
    frac_days = age_fract * MONTHLENGTH
    # remove fraction days from e2 julian day
    frac_jd = e2_jd - frac_days
    # remove 1 julian day to ensure crossing (fwd search)
    start_jd = frac_jd  # - 1.0
    # get natal su & mo longitude
    if e1_pos:
        for _, v in e1_pos.items():
            if isinstance(v, dict):
                # if v.get("name") == "su":
                #     e1_su = v.get("lon")
                if v.get("name") == "mo":
                    e1_mo = v.get("lon")
    msg += f" e1mo : {e1_mo} [crosscheck longitudes]\n"
    # search lunar crossing
    lun_ret_jd = swe.mooncross_ut(e1_mo, start_jd, app.sweph_flag)
    # if e2_jd < lun_ret_jd:
    #     return
    lunret = swe.revjul(lun_ret_jd, swe.GREG_CAL)
    y, m, d, h = lunret
    H, M, S = _decimal_to_hms(h)
    msg += (
        f"lunretjd : {lun_ret_jd} | lun return : "
        f"{y}-{m:02}-{d:02} {H:02}:{M:02}:{S:02}\n"
    )
    # gather data needed for calc_ut() function
    objs = getattr(app, "selected_objects_e2")
    use_mean_node = app.chart_settings["mean node"]
    # calculate positions on solar return julian day
    lun_ret_data: list[dict] = []
    for obj in objs:
        code, name = objcode(obj, use_mean_node)
        if code is None:
            continue
        # calc_ut() returns array of 6 floats [0] + error string [1]:
        # longitude, latitude, distance, lon speed, lat speed, dist speed
        try:
            result = swe.calc_ut(lun_ret_jd, code, app.sweph_flag)
            # print(f"positions with speeds & flag used : {result}")
            data = result[0] if isinstance(result, tuple) else result
            lun_ret_data.append({"name": name, "lon": data[0]})
            msg += f"{name} : {data[0]}\n"
        except swe.Error as e:
            notify.error(
                f"lunar return positions calculation failed for : "
                f"{event}\n\tdata {lun_ret_data[code]}\n\tswe error :\n\t{e}",
                source="lunarreturn",
                route=["terminal"],
            )
    # also calculate houses
    hsys = app.selected_house_sys
    # houses = {}
    if lun_ret_jd and e1_sweph and hsys:
        try:
            # todo also draw house cusps
            cusps, ascmc = swe.houses_ex(
                lun_ret_jd,
                e1_sweph["lat"],
                e1_sweph["lon"],
                hsys.encode("ascii"),
                app.sweph_flag,
            )
        except swe.Error as e:
            notify.error(
                f"lunar return houses calculation failed\n\tswe error\n\t{e}",
                source="lunarreturn",
                route=["terminal"],
            )
        if ascmc:
            lun_ret_cusps = cusps
            lun_ret_data.append(lun_ret_cusps)
            lun_ret_asc = ascmc[0]
            lun_ret_data.append({"name": "asc", "lon": lun_ret_asc})
            lun_ret_mc = ascmc[1]
            lun_ret_data.append({"name": "mc", "lon": lun_ret_mc})
        # msg += f"lunretdata :\n\t{lun_ret_data}"
    app.lun_ret_data = lun_ret_data
    # emit signal
    app.signal_manager._emit("lunar_return_changed", event)
    notify.debug(
        msg,
        source="lunarreturn",
        route=["terminal"],
    )


def e2_cleared(event):
    # todo clear all event 2 data
    if event == "e2":
        return "e2 was cleared : todo\n"


def connect_signals_lunarreturn(signal_manager):
    # update progressions when data used changes
    signal_manager._connect("event_changed", calculate_lr)
    signal_manager._connect("settings_changed", calculate_lr)
    signal_manager._connect("e2_cleared", e2_cleared)
