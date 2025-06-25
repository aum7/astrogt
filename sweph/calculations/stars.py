# sweph/calculations/start.py
# ruff: noqa: E402
# swe.fixstar2_ut : star name (catalog or nomenclature), tjd_ut, flags
# returns : (lon, lat, dist, speeds : lon, lat, dist), star name, flags used
# eta tauri : ("Alcyone", "Alcyone, Krttika", "etTau"),
import swisseph as swe
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore
from typing import Optional, List
from user.fixedstars import fixedstars
from user.settings import CHART_SETTINGS


def calculate_stars(event: Optional[str] = None) -> None:
    """calculate positions of stars, listed in user/fixedstars.py"""
    # todo draw all 27 / 28 naksatras stars in naksatras ring
    app = Gtk.Application.get_default()
    notify = app.notify_manager
    # get stars from selected category
    chart_settings = getattr(app, "chart_settings", {})
    stars_category = chart_settings.get("fixed stars", CHART_SETTINGS["fixed stars"][0])
    stars = fixedstars.get(stars_category, [])
    # event 1 data is mandatory
    if not app.e1_sweph.get("jd_ut"):
        notify.warning(
            "missing event one data needed for stars\n\texiting ...",
            source="stars",
            route=["terminal", "user"],
        )
        return
    events: List[str] = [event] if event else ["e1", "e2"]
    if "e2" in events and not app.e2_sweph.get("jd_ut"):
        # skip e2 if no datetime / julian day utc set = user not interested in e2
        events.remove("e2")
    for event in events:
        sweph = app.e1_sweph if event == "e1" else app.e2_sweph
        if not sweph or "jd_ut" not in sweph:
            notify.debug(
                f"missing data for event : {event}\n\tsweph : {sweph}\n\texiting ...",
                source="stars",
                route=["terminal"],
            )
            return
        jd_ut = sweph.get("jd_ut")
        # get stars dict
        star_positions = {}
        for star in stars:
            # unpack : nomenclature, traditional, alternative name
            nomenclature, name, _ = star
            try:
                pos, _, _ = swe.fixstar2_ut(name, jd_ut, app.sweph_flag)
                lon = pos[0]
                # pack what we need only
                star_positions[name] = (lon, nomenclature)
            except Exception as e:
                notify.error(
                    f"search error\n\t{e}",
                    source="stars",
                    route=["terminal"],
                )
        app.signal_manager._emit("stars_changed", event, star_positions)
    notify.debug(
        "starspositions calculated",
        source="stars",
        route=["none"],
    )


def connect_signals_stars(signal_manager):
    """initialize in mainwindow.py"""
    signal_manager._connect("settings_changed", calculate_stars)
    signal_manager._connect("event_changed", calculate_stars)
