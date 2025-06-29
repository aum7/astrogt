# sweph/calculations/vimsottari.py
# ruff: noqa: E402, E701
import swisseph as swe
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore
from typing import Optional, Dict, Any, List

from ui.mainpanes.panechart.chartcircles import NAKSATRAS27


def dasa_years():
    return {
        "ke": 7,
        "ve": 20,
        "su": 6,
        "mo": 10,
        "ma": 7,
        "ra": 18,
        "ju": 16,
        "sa": 19,
        "me": 17,
    }


def calculate_vimsottari(event: Optional[str] = None, luminaries: Dict[str, Any] = {}):
    """calculate vimsottari for event"""
    app = Gtk.Application.get_default()
    notify = app.notify_manager
    # event 1 data is mandatory
    if not app.e1_sweph.get("jd_ut"):
        notify.warning(
            "missing event one data needed for vimsottari\n\texiting ...",
            source="vimsottari",
            route=["terminal", "user"],
        )
        return
    events: List[str] = [event] if event else ["e1", "e2"]
    if "e2" in events and not app.e2_sweph.get("jd_ut"):
        # skip e2 if no datetime / julian day utc set = user not interested in e2
        events.remove("e2")
    notify.debug(
        f"event(s) : {events} | luminaries : {luminaries}",
        source="vimsottari",
        route=["none"],
    )
    sol_year_sel = get_sol_year_sel()
    print(f"selyear : {sol_year_sel}")
    jd_pos = {k: v for k, v in luminaries.items() if isinstance(k, int)}
    # grab moon position
    moon = next((p for p in jd_pos.values() if p["name"] == "mo"), None)
    jd_ut = luminaries.get("start_jd_ut")
    if not moon or not jd_ut:
        notify.error(
            "missing luminaries data\n\texiting ...",
            source="vimsottari",
            route=["terminal"],
        )
        return
    mo_lon = moon["lon"]
    # print(f"vimsottari : moon lon : {mo_lon}")
    nak_length = 360 / 27
    nak_idx = int(mo_lon // nak_length) + 1
    nak_frac = (mo_lon % nak_length) / nak_length
    start_lord, _ = NAKSATRAS27[nak_idx]
    dasa_yrs = dasa_years()
    years = dasa_yrs[start_lord]
    event_dasas = get_vimsottari_periods(
        sol_year_sel, jd_ut, start_lord, nak_frac, years, 0, 3
    )
    app.signal_manager._emit("vimsottari_changed", event, event_dasas)
    notify.debug(
        f"start_jd_ut : {jd_ut}\n\tdasas : {event_dasas}",
        source="vimsottari",
        route=["none"],
    )


def get_vimsottari_periods(
    sel_year,
    jd_ut,
    start_lord,
    frac=0.0,
    years=0.0,
    level=0,
    max_level=3,
):
    app = Gtk.Application.get_default()
    notify = app.notify_manager
    dasa_yrs = dasa_years()
    lord_seq = list(dasa_yrs)
    start_idx = lord_seq.index(start_lord)
    # print(f"vims.py.lord_seq : {lord_seq}")
    # def recurse(jd_ut, lord, frac, years, level, max_level):
    dasas = []
    for i in range(9):
        lord = lord_seq[(start_idx + i) % 9] if level == 0 else lord_seq[i]
        if level == 0 and i == 0:
            # 1st period reminder
            dur = (1 - frac) * dasa_yrs[start_lord]
        else:
            # recursive levels scaled
            dur = years * dasa_yrs[lord] / 120
        # todo set period from user selection
        days = dur * sel_year
        jd_end = jd_ut + days
        entry = {
            "lord": lord,
            "years": round(dur, 4),
            "from": swe.revjul(jd_ut, cal=swe.GREG_CAL),
            "to": swe.revjul(jd_end, cal=swe.GREG_CAL),
        }
        if level + 1 < max_level:
            entry["sub"] = get_vimsottari_periods(
                sel_year,
                jd_ut,
                lord,
                0,
                dur,
                level + 1,
                max_level,
            )
        dasas.append(entry)
        jd_ut = jd_end
    notify.info(
        f"entry : {str(entry)[:900]}",
        source="vimsottari",
        route=["none"],
    )
    return dasas

    # return recurse(start_jd_ut, start_lord, start_frac, years, 0, 3)


def get_sol_year_sel():
    app = Gtk.Application.get_default()
    year_sel = getattr(app, "selected_year_period")
    year_sel = year_sel[0]
    if year_sel:
        return year_sel
    return 365.2425  # gregorian default


def connect_signals_vimsottari(signal_manager):
    """update vimsottari when positions of luminaries change"""
    signal_manager._connect("luminaries_changed", calculate_vimsottari)
    signal_manager._connect("solar_year_changed", calculate_vimsottari)
