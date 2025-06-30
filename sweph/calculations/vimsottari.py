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
    # print(f"vmst : moon : {mo_lon} | jd : {jd_ut}")
    event_dasas = output(mo_lon, jd_ut)
    # print(f"dasas : {event_dasas}")
    app.signal_manager._emit("vimsottari_changed", event, event_dasas)
    notify.debug(
        f"start_jd_ut : {jd_ut}\n\tdasas : {event_dasas}",
        source="vimsottari",
        route=["none"],
    )


def find_nakshatra(mo_deg):
    part = 360 / 27
    idx = int(mo_deg // part) + 1
    frac = (mo_deg % part) / part
    return idx, frac


def get_lord_seq(start_lord):
    seq = [NAKSATRAS27[i][0] for i in range(1, 10)]
    idx = seq.index(start_lord)
    return seq[idx:] + seq[:idx]


def which_period_years(mo_deg):
    dy = dasa_years()
    idx, frac = find_nakshatra(mo_deg)
    maha_lord = NAKSATRAS27[idx][0]
    maha_seq = get_lord_seq(maha_lord)
    maha_portion = frac
    antara_idx_f = frac * 9
    antara_idx = int(antara_idx_f)
    antara_frac = antara_idx_f - antara_idx
    antara_lord = maha_seq[antara_idx]
    antara_seq = get_lord_seq(antara_lord)
    praty_idx_f = antara_frac * 9
    praty_idx = int(praty_idx_f)
    praty_frac = praty_idx_f - praty_idx
    praty_lord = antara_seq[praty_idx]
    maha_yrs = dy[maha_lord]
    maha_rem = (1 - maha_portion) * maha_yrs
    antara_yrs = maha_yrs * dy[antara_lord] / 120
    antara_rem = (1 - antara_frac) * antara_yrs
    praty_yrs = antara_yrs * dy[praty_lord] / 120
    praty_rem = (1 - praty_frac) * praty_yrs
    return {
        "maha": {
            "lord": maha_lord,
            "portion": maha_portion,
            "years": maha_yrs,
            "rem": maha_rem,
        },
        "antara": {
            "lord": antara_lord,
            "portion": antara_frac,
            "years": antara_yrs,
            "rem": antara_rem,
        },
        "praty": {
            "lord": praty_lord,
            "portion": praty_frac,
            "years": praty_yrs,
            "rem": praty_rem,
        },
    }


def jd_to_date(jd):
    y, m, d, h = swe.revjul(jd, swe.GREG_CAL)
    hh = int(h)
    mi = int((h - hh) * 60)
    s = int((((h - hh) * 60) - mi) * 60)
    return f"{y:04d}-{m:02d}-{d:02d} {hh:02d}:{mi:02d}:{s:02d}"


def output(mo_deg, jd):
    # as before, but return dict with header and dasas by level
    lines = []
    idx, frac = find_nakshatra(mo_deg)
    nak_lord, nak_name = NAKSATRAS27[idx]
    # header line
    lines.append(f"nak {idx:02} {nak_name} {nak_lord} | traversed {frac * 100:.2f} %")
    year_length = 365.2425
    dy = dasa_years()
    res = which_period_years(mo_deg)
    maha_lord = res["maha"]["lord"]
    maha_seq = get_lord_seq(maha_lord)
    maha_idx = maha_seq.index(maha_lord)
    current_jd = jd
    for mi in range(0, 9):
        lord = maha_seq[(maha_idx + mi) % 9]
        years = dy[lord]
        start = jd_to_date(current_jd)
        if mi == 0:
            rem_years = res["maha"]["rem"]
        else:
            rem_years = years
        lines.append(f"{lord} {rem_years:.4f} y | start {start}")
        antara_seq = get_lord_seq(lord)
        antara_idx = 0
        antara_jd = current_jd
        antara_portion_passed = 0.0
        if mi == 0:
            antara_idx = int(res["maha"]["portion"] * 9)
            antara_portion_passed = res["antara"]["portion"]
        for ai in range(antara_idx, 9):
            antara_lord = antara_seq[ai % 9]
            antara_years = years * dy[antara_lord] / 120
            antara_start = jd_to_date(antara_jd)
            if mi == 0 and ai == antara_idx:
                rem_antara = res["antara"]["rem"]
            else:
                rem_antara = antara_years
            lines.append(f"   {antara_lord} {rem_antara:.4f} y | start {antara_start}")
            praty_seq = get_lord_seq(antara_lord)
            praty_idx = 0
            praty_jd = antara_jd
            if mi == 0 and ai == antara_idx:
                praty_idx = int(antara_portion_passed * 9)
            for pi in range(praty_idx, 9):
                praty_lord = praty_seq[pi % 9]
                praty_years = antara_years * dy[praty_lord] / 120
                praty_start = jd_to_date(praty_jd)
                if mi == 0 and ai == antara_idx and pi == praty_idx:
                    rem_praty = res["praty"]["rem"]
                else:
                    rem_praty = praty_years
                lines.append(
                    f"      {praty_lord} {rem_praty:.4f} y | start {praty_start}"
                )
                praty_jd += rem_praty * year_length
            antara_jd += rem_antara * year_length
        current_jd += rem_years * year_length
        if mi == 0:
            antara_idx = 0
            antara_portion_passed = 0.0
    # create dict by level
    out = {"header": lines[0], "dasas": {1: [], 2: [], 3: []}}
    for ln in lines[1:]:
        if ln.startswith("      "):
            out["dasas"][3].append(ln.strip())
        elif ln.startswith("   "):
            out["dasas"][2].append(ln.strip())
        else:
            out["dasas"][1].append(ln.strip())
    return out


def connect_signals_vimsottari(signal_manager):
    """update vimsottari when positions of luminaries change"""
    signal_manager._connect("luminaries_changed", calculate_vimsottari)
