# sweph/calculations/lunarreturn.py
# ruff: noqa: E402, E701
import swisseph as swe
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore
from ui.helpers import _object_name_to_code as objcode
from sweph.swetime import jd_to_custom_iso as jdtoiso


def calculate_lr(event: str):
    # tertiary direction calculation
    app = Gtk.Application.get_default()
    notify = app.notify_manager
    msg = f"event {event}\n"
    # event 1 & 2 data is mandatory : natal / event & progression chart
    # check against lumies since e1_sweph can have 0 objects (user-selectable)
    if not app.e1_sweph.get("jd_ut") or not app.e2_sweph.get("jd_ut"):
        notify.error(
            "missing event 1 or 2 data : exiting ...",
            source="lunarreturn",
            route=[""],
        )
        return
    # gather data
    # e1 positions for su / mo longitude crosscheck only
    e1_pos = getattr(app, "e1_positions", None)
    e2_pos = getattr(app, "e2_positions", None)
    # sweph 3 members < pos upto 11 members
    e1_sweph = getattr(app, "e1_sweph", None)
    e2_sweph = getattr(app, "e2_sweph", None)
    if e1_pos:
        e1_jd = e1_pos.get("jd_ut")
    if e2_sweph:
        e2_jd = e2_sweph.get("jd_ut")
    # msg += f"e1jd : {jdtoiso(e1_jd)} | e2jd : {jdtoiso(e2_jd)}\n"
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
    # get natal su & mo longitude
    if e1_pos:
        for _, v in e1_pos.items():
            if isinstance(v, dict):
                if v.get("name") == "mo":
                    e1_mo = v.get("lon")
    if e2_pos:
        for _, v in e2_pos.items():
            if isinstance(v, dict):
                if v.get("name") == "mo":
                    e2_mo = v.get("lon")
    msg += f"e1mo : {e1_mo:.7f} [crosscheck] e2mo : {e2_mo:.7f}\n"
    # solcross & mooncros always search forward
    # globally store previous & next lunar return julian day
    if not hasattr(app, "lr_prev_jd") or not hasattr(app, "lr_next_jd"):
        app.lr_prev_jd = None
        app.lr_next_jd = None
    # previous lunar return : search x days back range
    prev_jd = e2_jd - MONTHLENGTH
    lr_prev_jd = swe.mooncross_ut(e1_mo, prev_jd, app.sweph_flag)
    # next lunar return
    next_jd = e2_jd
    lr_next_jd = swe.mooncross_ut(e1_mo, next_jd, app.sweph_flag)
    lr_month = lr_next_jd - lr_prev_jd
    # store values for checking while lr month is proper
    if (MONTHLENGTH - 1) < lr_month < (MONTHLENGTH + 1):
        app.lr_prev_jd = lr_prev_jd
        app.lr_next_jd = lr_next_jd
    else:
        # recalculate values only inside problematic time window
        if e1_mo and e2_mo and app.lr_prev_jd and app.lr_next_jd:
            # we are in smaller lr cycle
            if lr_month == 0.0:
                # transit time is before next lr jd > keep old values
                if e2_jd <= app.lr_next_jd:
                    lr_prev_jd = app.lr_prev_jd
                    lr_next_jd = app.lr_next_jd
                # transit time is before prev lr jd > should be in prev lr cycle
                # which could be bigger lr cycle > extend range by 1 day back
                if e2_jd <= app.lr_prev_jd:
                    new_prev_jd = e2_jd - MONTHLENGTH - 1
                    lr_prev_jd = swe.mooncross_ut(e1_mo, new_prev_jd, app.sweph_flag)
                    # new_next_jd = e2_jd - 1
                    lr_next_jd = swe.mooncross_ut(e1_mo, e2_jd, app.sweph_flag)
                    # lr_next_jd = swe.mooncross_ut(e1_mo, new_next_jd, app.sweph_flag)
            # we are in bigger lr cycle
            if lr_month > 53.0:
                if e2_jd < app.lr_next_jd:
                    new_prev_jd = e2_jd - 1
                    lr_prev_jd = swe.mooncross_ut(e1_mo, new_prev_jd, app.sweph_flag)
        # update stored values
        app.lr_prev_jd = lr_prev_jd
        app.lr_next_jd = lr_next_jd
    # current lunar return on chart
    lr_curr_jd = lr_prev_jd
    # debug data
    if lr_month < MONTHLENGTH:
        this = "smaller"
        diff = round(MONTHLENGTH - lr_month, 5)
    elif lr_month > MONTHLENGTH:
        this = "bigger"
        diff = round(lr_month - MONTHLENGTH, 5)
    msg += (
        f"lrmonth : {lr_month} |-| {this} by {diff}\n"
        f"e2jd :     {jdtoiso(e2_jd)} < current datetime\n"
        f"lrprevjd : {jdtoiso(lr_prev_jd)} < current lr cycle\n"
        # f"appprev :  {jdtoiso(app.lr_prev_jd)}\n"
        f"lrnextjd : {jdtoiso(lr_next_jd)}\n"
        # f"appnext :  {jdtoiso(app.lr_next_jd)}"
        # f"lrcurrjd : {jdtoiso(lr_curr_jd)}\n"
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
            result = swe.calc_ut(lr_curr_jd, code, app.sweph_flag)
            # print(f"positions with speeds & flag used : {result}")
            data = result[0] if isinstance(result, tuple) else result
            lun_ret_data.append({"name": name, "lon": data[0]})
            # msg += f"{name} : {data[0]}\n"
        except swe.Error as e:
            notify.error(
                f"lunar return positions calculation failed for : "
                f"{event}\n\tdata {lun_ret_data[code]}\n\tswe error :\n\t{e}",
                source="lunarreturn",
                route=["terminal"],
            )
    # also calculate houses
    hsys = app.selected_house_sys
    if lr_curr_jd and e1_sweph and hsys:
        try:
            cusps, ascmc = swe.houses_ex(
                lr_curr_jd,
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
            lun_ret_data.append(cusps)
            lun_ret_data.append({"name": "asc", "lon": ascmc[0]})
            lun_ret_data.append({"name": "mc", "lon": ascmc[1]})
        # msg += f"lunretdata :\n\t{lun_ret_data}"
    app.lun_ret_data = lun_ret_data
    # emit signal
    app.signal_manager._emit("lunar_return_changed", event)
    notify.debug(
        msg,
        source="lunarreturn",
        route=[""],
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
