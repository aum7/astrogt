# sweph/calculations/lunation.py
# ruff: noqa: E402
import swisseph as swe
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore
from typing import List
from sweph.swetime import jd_to_custom_iso as jdtoiso


def calculate_lunation(event: str):
    """calculate prenatal (last) full or new moon - syzygy"""
    app = Gtk.Application.get_default()
    notify = app.notify_manager
    msg = f"event {event}\n"
    events: List[str] = [event] if event else ["e1", "e2"]
    if "e2" in events and not app.e2_sweph.get("jd_ut"):
        # skip e2 if no datetime / julian day utc set = user not interested in e2
        events.remove("e2")
        msg += "e2 removed\n"
    for event_name in events:
        event_data, jd_ut = None, None
        swe_flag = getattr(app, "sweph_flag", None)
        # get existing data needed
        if event_name == "e1":
            event_data = getattr(app, "e1_sweph", None)
            prenatal = getattr(app, "selected_prenatal_e1")
        elif event_name in ("e2", "p3"):
            # progression is linked to event 2
            event_data = getattr(app, "e2_sweph", None)
            prenatal = getattr(app, "selected_prenatal_e2", None)
        if event_data:
            jd_ut = event_data.get("jd_ut")
        # msg += f"eventdata : {event_data}\n"
        if jd_ut is None:
            notify.warning(
                f"data for {event_name} missing : exiting ...",
                source="eclipses",
                route=["terminal"],
            )
            return
        elif prenatal:
            # clear eclipses data
            lunation_data = []
            if "lunation" in prenatal:
                flag = swe_flag
                # find closest lunation
                flag |= swe.ECL_ONE_TRY
                # get lunar occultation of sun 0 & 180 degrees
                find_type = 0  # any eclipse type
                _, tret = swe.lun_occult_when_glob(
                    jd_ut, 0, swe_flag, find_type, backwards=True
                )
                # maximum lunation
                jd_max_lun = tret[0]
                msg += f"lunation datetime : {jdtoiso(jd_max_lun)}\n"
                try:
                    data, e = swe.calc_ut(jd_max_lun, 1, swe_flag)
                    mo_lon = data[0]
                    lunation_data.append({"event": event})
                    lunation_data.append({"name": "conj", "lon": mo_lon})
                    # lunation_data.append({"lon": mo_lon})
                except Exception as e:
                    notify.error(
                        f"lunation error : exiting ...\n\t{e}",
                        source="lunation",
                        route=["terminal"],
                    )
                    return
                msg += f"lunationdata : {lunation_data}\n"
    notify.debug(
        msg,
        source="lunation",
        route=["terminal"],
    )
    return lunation_data


def find_last_solar_lunation(jd_ut, samanthafox):
    print(f"solarlunation : {samanthafox}")


def format_eclipse_type(eclflag):
    """convert eclipse flag to human-readable"""
    # definitions
    ECL_CENTRAL = 1
    ECL_NONCENTRAL = 2
    ECL_TOTAL = 4
    ECL_ANNULAR = 8
    ECL_PARTIAL = 16
    ECL_ANNULAR_TOTAL = 32  # = ECL_HYBRID
    ECL_PENUMBRAL = 64

    types = []

    if eclflag & ECL_CENTRAL:
        types.append("central")
    elif eclflag & ECL_NONCENTRAL:
        types.append("non-central")
    elif eclflag & ECL_TOTAL:
        types.append("total")
    elif eclflag & ECL_ANNULAR:
        types.append("annular")
    elif eclflag & ECL_PARTIAL:
        types.append("partial")
    elif eclflag & ECL_ANNULAR_TOTAL:
        types.append("annular-total")
    elif eclflag & ECL_PENUMBRAL:
        types.append("penumbral")

    if not types:
        return f"unknown flag : {eclflag}"
    # print(f"eclflag : {eclflag}")
    return " - ".join(types)
