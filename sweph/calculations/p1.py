# sweph/calculations/p1.py
# ruff: noqa: E402, E701
# import swisseph as swe
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore

# from datetime import datetime
from ui.helpers import _object_name_to_code as objcode


def calculate_p1(event: str):
    # actual motion of heavens in hours following birth, brings objects to
    # places in natal chart, unfolding events in years to come; each degree
    # of such motion corresponds to approximately 1 year of life
    app = Gtk.Application.get_default()
    notify = app.notify_manager
    msg = f"event {event}\n"
    # event 1 & 2 data is mandatory : natal / event & progression chart
    # check against lumies since e1_sweph can have 0 objects (user-selectable)
    if not app.e1_sweph.get("jd_ut") or not app.e2_sweph.get("jd_ut"):
        notify.error(
            "missing event 1 or 2 data needed for p1 : exiting ...",
            source="p1",
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
    YEARLENGTH = sel_year[0]
    if e1_jd and e2_jd:
        # period elapsed from birth in years
        delta_years = (e2_jd - e1_jd) / YEARLENGTH
        # print(f"deltayears : {delta_years}")
    chart_sett = getattr(app, "chart_settings")
    true_node = chart_sett.get("mean node")
    objs = getattr(app, "selected_objects_e2", None)
    e1_pos = getattr(app, "e1_positions", None)
    # msg += f"e1pos : {e1_pos}\n"
    e1_houses = getattr(app, "e1_houses", None)
    # clear previous data
    p1_data: list[dict] = []
    p1_data.append({"name": "age", "age": delta_years})
    # add delta years to each position
    if e1_houses and objs and e1_jd and e1_pos:
        # ascendant
        asc = e1_houses[1][0]
        p1_data.append({"name": "asc", "lon": asc + delta_years})
        # nadir
        mc = e1_houses[1][1]
        p1_data.append({"name": "mc", "lon": mc + delta_years})
        # msg += f"\tobjs : {objs}\n\tasc : {asc} | mc : {mc}\n"
        # filter objects selected for event 2
        for obj in objs:
            code, name = objcode(obj, true_node)
            if code is None:
                continue
            pos = e1_pos.get(code)
            if not isinstance(pos, dict):
                continue
            lon = pos.get("lon")
            if lon is None:
                continue
            data = {"name": name, "lon": lon + delta_years}
            # if "lat" in pos:
            #     data["lat"] = pos["lat"]
            # if "lon speed" in pos:
            #     data["lon speed"] = pos["lon speed"]
            p1_data.append(data)
        msg += f"p1data : {p1_data}\n"
    app.p1_pos = p1_data
    # emit signal
    app.signal_manager._emit("p1_changed", event)
    notify.debug(
        msg,
        source="p1",
        route=[""],
    )


def e2_cleared(event):
    # todo clear all event 2 data
    if event == "e2":
        return "e2 was cleared : todo\n"


def connect_signals_p1(signal_manager):
    # update progressions when data used changes
    signal_manager._connect("event_changed", calculate_p1)
    signal_manager._connect("settings_changed", calculate_p1)
    signal_manager._connect("e2_cleared", e2_cleared)
