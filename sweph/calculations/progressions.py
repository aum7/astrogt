# sweph/calculations/progressions.py
# ruff: noqa: E402, E701
import swisseph as swe
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore
from ui.helpers import _object_name_to_code as objcode


def calculate_p1(event: str):
    # grab application data & calculate vimsottari for event 1
    app = Gtk.Application.get_default()
    notify = app.notify_manager
    msg = f"event {event}\n"
    # event 1 data is mandatory : natal / event chart
    # check against lumies since e1_sweph can have 0 objects (user-selectable)
    if not app.e1_lumies.get("jd_ut") or not app.e2_lumies.get("jd_ut"):
        notify.error(
            "missing event 1 or 2 data needed for progressions : exiting ...",
            source="progressions",
            route=["terminal", "user"],
        )
        return
    # sidereal flag is detected on settings change & stored application-wide
    # FLG_SIDEREAL vs FLG_TROPICAL (default)
    is_sidereal = getattr(app, "is_sidereal", False)
    is_topocentric = getattr(app, "is_topocentric", False)
    use_mean_node = (
        app.chart_settings["mean node"] if hasattr(app, "chart_settings") else False
    )
    # need tropical equatorial houses for p1
    h_sys = (
        app.selected_house_sys.encode("ascii")
        if hasattr(app, "selected_house_sys")
        else None  # "B".encode("ascii")  # alcabitus
    )
    # initialize needed data
    e1_armc = 0.0
    # gather e1 data : luminaries are mandatory - e1/2_positions can be empty
    if event == "e1":
        msg += "e1 detected\n"
        e1_sweph = app.e1_sweph if hasattr(app, "e1_sweph") else None
        if e1_sweph:
            e1_jd = e1_sweph.get("jd_ut")
            e1_lat = e1_sweph.get("lat")
            e1_lon = e1_sweph.get("lon")
        e1_houses_ra = swe.houses(e1_jd, e1_lat, e1_lon, h_sys)
        e1_armc = e1_houses_ra[1][2]
        # get true obliquity of ecliptic
        # flagret = swe_calc_ut(tjd_ut, swe.ECL_NUT)[x] > filled by :
        # x[0] = true obliquity of the Ecliptic (includes nutation)
        # x[1] = mean obliquity of the Ecliptic
        # x[2] = nutation in longitude
        # x[3] = nutation in obliquity
        # x[4] = x[5] = 0
        e1_ecl = swe.calc_ut(e1_jd, swe.ECL_NUT)[0]
        e1_obliquity = e1_ecl[0]
        # msg += (
        #     f"e1armc : {e1_armc}\ne1ecl(nut) : {e1_ecl}\ne1obliquity : {e1_obliquity}\n"
        # )
    if event == "e2":
        msg += "e2 detected\n"
        msg += f"{e2_cleared(event)}"
        # gather e2 data
        e2_jd = app.e2_lumies.get("jd_ut")
        # objects list from sidepane > settings > objects panel
        e2_sel_objs = getattr(app, "selected_objects_e2", None)
        # msg += f"e2jd : {e2_jd}\ne2selobjs : {e2_sel_objs}\n"
        # calculate tropical positions : valid for both zodiacs : prepare custom flag
        flag = swe.FLG_SWIEPH | swe.FLG_SPEED | swe.FLG_EQUATORIAL
        # add flag if topocentric positions are wanted
        if is_topocentric:
            flag |= swe.FLG_TOPOCTR
        # msg += (
        #     f"sidereal : {is_sidereal}\ntopocentric : {is_topocentric}\nflag : {flag}\n"
        # )
        e2_pos_ra = {}
        if e2_jd and e2_sel_objs and flag:
            for obj in e2_sel_objs:
                code, name = objcode(obj, use_mean_node)
                if code is None:
                    continue
                # calc_ut() returns array of 6 floats [0] + error string [1]:
                # longitude, latitude, distance, lon speed, lat speed, dist speed
                try:
                    result = swe.calc_ut(e2_jd, code, flag)
                    # msg += f"ra positions with speeds & flag used : {result}"
                    data = result[0] if isinstance(result, tuple) else result
                    # meridian distance from midheaven todo ???
                    md = data[0] - e1_armc
                    # md = swe.degnorm(data[0] - e1_armc)
                    e2_pos_ra[code] = {
                        "name": name,
                        "ra": data[0],
                        "decl": data[1],
                        # "dist": data[2],
                        "ra speed": data[3],
                        # "decl speed": data[4],
                        # "dist speed": data[5],
                        "md": md,
                    }
                except swe.Error as e:
                    notify.error(
                        f"tropical positions calculation failed for : {event}\n\tdata {e2_pos_ra[code]}\n\tswe error :\n\t{e}",
                        source="progressions",
                        route=["terminal"],
                    )
        msg += f"e2selobjra :\n\t{e2_pos_ra}\n"
        # add / remove ayanamsa from tropical positions
        e2_pos_sid = {}
        if e2_pos_ra and is_sidereal:
            # get ayanamsa value
            cur_ayanamsa = swe.get_ayanamsa_ex_ut(e2_jd, flag)[1] if e2_jd else None
            # msg += f"curayan : {cur_ayanamsa}\n"
            # convert tropical to sidereal
            e2_pos_sid = ra_to_sidereal(e2_pos_ra, cur_ayanamsa)
        # msg += f"possidereal : {e2_pos_sid}\n"
    # app.signal_manager._emit("progressions_changed", event)
    notify.debug(
        msg,
        source="progressions",
        route=["terminal"],
    )


def ra_to_sidereal(positions, ayanamsa):
    print(f"trotosid : {positions}")


def e2_cleared(event):
    # todo clear all event 2 data
    if event == "e2":
        return "e2 was cleared : todo\n"


def connect_signals_progressions(signal_manager):
    # update progressions when data used changes
    signal_manager._connect("positions_changed", calculate_p1)
    signal_manager._connect("houses_changed", calculate_p1)
    signal_manager._connect("e2_cleared", e2_cleared)
