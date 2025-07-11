# sweph/calculations/p3.py
# tertiary progression (aka minor progression)
# as per richard houck (astrology of death)
# divide year by sidereal month & use blocks of 13-14 days as representing
# a year in life
# use tertiary planets & tertiary solar arc'd mc (and derived asc) as they hit
# the natal chart
# a day in life (or ephemeris) is equal to a lunar month in the life
# p3 MC by amount of tertiary solar arc, ie roughly 1 degree per month
# p3 ASC just a slight variation on this : derived normally per Table of Houses
# tertiary angles for rectification : every week of event error (p3 angles) will
# correlate to about 1 minute of birthtime error ; tertiary angles will pass
# about 2 1/2 years in each sign and house : correlates to transiting Saturn
# and the p2 progressed Moon

# Dasa / Bhukti planets with p3 planets, 3 rules that apply (subject of death)
# 1. p3 planetary stations intensify amplitude to symbolic message in the chart
# quality of amplitude related directly to fundamental nature of planet
# 2. an approximate correlation between current Dasa (or Bhukti) planet and a
# p3 planetary station : often signal death if subsidiary factors confirm
# 3. expect apx p3 angle & planet hits in exact 4th harmonic to current maraka
# chart sensible to prenatal and p3 eclipses : any point in a chart ( planet or
# angle) becomes extremely sensitized if hit directly by one of these eclipses
# ancient astrologers considered eclipses evil : interrupted luminaries
# 1 degree exact ; jyotisa rules for aspects : ma 4/8 ju 5/9 sa 3/10

# calculate lunar returns before and after e2 (gives exact lunar month)
# mc progressed by solar arc with all other cusps calculated from that
# p3 su & mc move around chart at about 1 ° per month, with p3 asc typically
# at a very slight variation > p3 angles in signs about 2 & ½ years (about as
# long as Tsa spends in a sign, p3 su circles chart same as Tsa. p3 mo moves
# ½ a ° per day > 2 months in sign, 2 years to circle entire chart
# ruff: noqa: E402
import swisseph as swe
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore
from ui.helpers import _decimal_to_hms
# _object_name_to_code as objcode


def calculate_p3(event: str):
    # calculate lunar returns before and after e2 (gives exact lunar month)
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
    e1_sweph = getattr(app, "e1_sweph", None)
    e2_sweph = getattr(app, "e2_sweph", None)
    if e1_sweph:
        e1_jd = e1_sweph.get("jd_ut")
    if e2_sweph:
        e2_jd = e2_sweph.get("jd_ut")
    sel_year = getattr(app, "selected_year_period", (365.2425, "gregorian"))
    # substitute with exact lunar return calculations : before & after e2 datetime
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
        # print(f"deltayears : {delta_years}")
    P3PERIOD = YEARLENGTH / MONTHLENGTH
    msg += f"p3period [fixed] : {P3PERIOD}\n"
    chart_sett = getattr(app, "chart_settings")
    # true_node = chart_sett.get("mean node")
    # objs = getattr(app, "selected_objects_e2", None)
    e1_pos = getattr(app, "e1_positions", None)
    # msg += f"e1pos : {e1_pos}\n"
    # get moon
    if e1_pos:
        e1_mo = next(
            (
                v["lon"]
                for v in e1_pos.values()
                if isinstance(v, dict) and v.get("name") == "mo"
            ),
            None,
        )
    # msg += f"e1mo : {e1_mo}\n"
    # previous lunar return : search 30 days back range : 3 days extra
    prev_jd = e2_jd - 30.0
    lr_prev_jd = swe.mooncross_ut(e1_mo, prev_jd, app.sweph_flag)
    prev_lunret = swe.revjul(lr_prev_jd, swe.GREG_CAL)
    y, m, d, h = prev_lunret
    H, M, S = _decimal_to_hms(h)
    # msg += (
    #     f"lrprevjd : {lr_prev_jd} | prevlunret : "
    #     f"{y}-{m:02}-{d:02} {H:02}:{M:02}:{S:02}\n"
    # )
    # next lunar return : remove 1h for crossover todo this needed ???
    next_jd = e2_jd - 0.0416666667
    lr_next_jd = swe.mooncross_ut(e1_mo, next_jd, app.sweph_flag)
    next_lunret = swe.revjul(lr_next_jd, swe.GREG_CAL)
    y, m, d, h = next_lunret
    H, M, S = _decimal_to_hms(h)
    # msg += (
    #     f"lrnextjd : {lr_next_jd} | nextlunret : "
    #     f"{y}-{m:02}-{d:02} {H:02}:{M:02}:{S:02}\n"
    # )
    # calculate lunar month length
    lr_month = lr_next_jd - lr_prev_jd
    p3_period = YEARLENGTH / lr_month
    msg += f"p3period [dynamic] : {p3_period}\n"
    # todo : p3_diff = age / p3period
    # todo : p3_pos = e1_jd + p3_diff
    # todo : progress mc by solar arc ???
    # todo : progress asc by tables of houses
    p3_data: list[dict] = []
    # msg += f"p3data : {p3_data}\n"
    app.p3_pos = p3_data
    # emit signal
    app.signal_manager._emit("p3_changed", event)
    notify.debug(
        msg,
        source="p3",
        route=["terminal"],
    )

    # e1_houses = getattr(app, "e1_houses", None)
    # clear previous data
    # p3_data.append({"name": "age", "age": delta_years})
    # add delta years to each position
    # if e1_houses and objs and e1_jd and e1_pos:
    # ascendant
    # asc = e1_houses[1][0]
    # p3_data.append({"name": "asc", "lon": asc + delta_years})
    # nadir
    # mc = e1_houses[1][1]
    # p3_data.append({"name": "mc", "lon": mc + delta_years})
    # msg += f"\tobjs : {objs}\n\tasc : {asc} | mc : {mc}\n"
    # filter objects selected for event 2
    # for obj in objs:
    # code, name = objcode(obj, true_node)
    # if code is None:
    #     continue
    # pos = e1_pos.get(code)
    # if not isinstance(pos, dict):
    #     continue
    # lon = pos.get("lon")
    # if lon is None:
    #     continue
    # data = {"name": name, "lon": lon + delta_years}
    # if "lat" in pos:
    #     data["lat"] = pos["lat"]
    # if "lon speed" in pos:
    #     data["lon speed"] = pos["lon speed"]
    # p3_data.append(data)


def e2_cleared(event):
    # todo clear all event 2 data
    if event == "e2":
        return "e2 was cleared : todo\n"


def connect_signals_p3(signal_manager):
    # update progressions when data used changes
    signal_manager._connect("event_changed", calculate_p3)
    signal_manager._connect("settings_changed", calculate_p3)
    signal_manager._connect("e2_cleared", e2_cleared)
