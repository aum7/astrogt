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


def vimsottari_table(mo_deg, jd, current_lvl=1, lvl_dist=3):
    # single func: calculates and formats vimsottari table as plain text
    dy = dasa_years()
    res = which_period_years(mo_deg)
    maha_lord = res["maha"]["lord"]
    maha_seq = get_lord_seq(maha_lord)
    maha_idx = maha_seq.index(maha_lord)
    year_length = 365.2425
    cur_jd = jd
    out = ""
    for mi in range(9):
        lord = maha_seq[(maha_idx + mi) % 9]
        years = dy[lord]
        rem_years = res["maha"]["rem"] if mi == 0 else years
        start = jd_to_date(cur_jd)
        maha_str = f"{lord:<2} {rem_years:.4f} y | {start}"
        out += maha_str + "\n"
        if current_lvl >= 2:
            antara_seq = get_lord_seq(lord)
            antara_idx = int(res["maha"]["portion"] * 9) if mi == 0 else 0
            antara_portion = res["antara"]["portion"] if mi == 0 else 0.0
            antara_jd = cur_jd
            for ai in range(antara_idx, 9):
                antara_lord = antara_seq[ai % 9]
                antara_years = years * dy[antara_lord] / 120
                rem_antara = (
                    res["antara"]["rem"]
                    if mi == 0 and ai == antara_idx
                    else antara_years
                )
                antara_start = jd_to_date(antara_jd)
                antara_str = f"{antara_lord:<2} {rem_antara:.4f} y | {antara_start}"
                out += " " * lvl_dist + antara_str + "\n"
                if current_lvl == 3:
                    praty_seq = get_lord_seq(antara_lord)
                    praty_idx = (
                        int(antara_portion * 9) if mi == 0 and ai == antara_idx else 0
                    )
                    praty_jd = antara_jd
                    for pi in range(praty_idx, 9):
                        praty_lord = praty_seq[pi % 9]
                        praty_years = rem_antara * dy[praty_lord] / 120
                        rem_praty = (
                            res["praty"]["rem"]
                            if mi == 0 and ai == antara_idx and pi == praty_idx
                            else praty_years
                        )
                        praty_start = jd_to_date(praty_jd)
                        praty_str = f"{praty_lord:<2} {rem_praty:.4f} y | {praty_start}"
                        out += " " * (2 * lvl_dist) + praty_str + "\n"
                        praty_jd += rem_praty * year_length
                antara_jd += rem_antara * year_length
        cur_jd += rem_years * year_length
    return out.rstrip()


def calculate_vimsottari(event: Optional[str] = None, luminaries: Dict[str, Any] = {}):
    """calculate vimsottari for event"""
    # print(f"calc_vmst data received : {luminaries}")
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
        f"event(s) : {events} | luminaries received : {luminaries}",
        source="vimsottari",
        route=[""],
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
    current_lvl = getattr(app, "current_lvl", 1)
    event_dasas = vimsottari_table(mo_lon, jd_ut, current_lvl=current_lvl, lvl_dist=3)
    app.signal_manager._emit("vimsottari_changed", event, event_dasas)
    notify.debug(
        f"start_jd_ut : {jd_ut}\n\tdasas : {event_dasas}",
        source="vimsottari",
        route=[""],
    )


def connect_signals_vimsottari(signal_manager):
    """update vimsottari when positions of luminaries change"""
    signal_manager._connect("luminaries_changed", calculate_vimsottari)
