# sweph/calculations/vimsottari.py
# ruff: noqa: E402, E701
import swisseph as swe
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore
from typing import Optional, Dict, Any, List

# from datetime import timedelta
from ui.mainpanes.panechart.chartcircles import NAKSATRAS27


def calculate_vimsottari(event: Optional[str] = None, luminaries: Dict[str, Any] = {}):
    """calculate aspectarian for one or both events"""
    app = Gtk.Application.get_default()
    # start_jd_ut = luminaries.get("jd_ut")
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
    jd_pos = {k: v for k, v in luminaries.items() if isinstance(k, int)}
    # grab moon position
    moon = next((p for p in jd_pos.values() if p["name"] == "mo"), None)
    start_jd_ut = luminaries.get("start_jd_ut")
    if not moon or not start_jd_ut:
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
    event_dasas = get_vimsottari_periods(
        notify,
        start_jd_ut,
        nak_idx,
        start_lord,
        nak_frac,
    )
    app.signal_manager._emit("vimsottari_changed", event, event_dasas)
    notify.debug(
        f"start_jd_ut : {start_jd_ut}\n\tdasas : {event_dasas}",
        source="vimsottari",
        route=["none"],
    )


def get_vimsottari_periods(
    notify,
    start_jd_ut,
    start_idx,
    start_lord,
    start_frac=0.0,
    years=0.0,
    level=0,
):
    dasa_years = {
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
    lord_seq = [
        "ke",
        "ve",
        "su",
        "mo",
        "ma",
        "ra",
        "ju",
        "sa",
        "me",
    ]
    # start_idx = lord_seq.index(start_lord)

    # def recurse(start_jd_ut, level, years, lord_seq):
    dasas = []
    for i, lord in enumerate(lord_seq):
        if level == 0:
            if i == 0:
                # 1st period reminder
                duration = (1 - start_frac) * dasa_years[start_lord]
            else:
                # rest are full lenght
                duration = dasa_years[lord]
        else:
            # recursive levels scaled
            duration = years * dasa_years[lord]
        # lord = lord_seq[(start_idx + i) % 9] if level == 0 else lord_seq[i]
        # duration = years * dasa_years[lord] / 120
        # if level == 0 and i == 0:
        #     duration *= 1 - start_frac
        days = duration * 365.2425
        jd_end = start_jd_ut + days
        entry = {
            "lord": lord,
            "years": round(duration, 4),
            "from": swe.revjul(start_jd_ut, cal=swe.GREG_CAL),
            "to": swe.revjul(jd_end),
        }
        dasas.append(duration)
        start_jd_ut = jd_end
    notify.info(
        f"duration :{duration:5.2f} years",
        source="vimsottari",
        route=["none"],
    )
    return dasas


def connect_signals_vimsottari(signal_manager):
    """update vimsottari when positions of luminaries change"""
    signal_manager._connect("luminaries_changed", calculate_vimsottari)
