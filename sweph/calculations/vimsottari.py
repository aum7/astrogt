# sweph/calculations/vimsottari.py
# ruff: noqa: E402, E701
import swisseph as swe
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore
# from typing import Optional, Dict, Any, List

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


def jd_to_date(jd):
    y, m, d, h = swe.revjul(jd, swe.GREG_CAL)
    hh = int(h)
    mi = int((h - hh) * 60)
    s = int((((h - hh) * 60) - mi) * 60)
    return f"{y:04d}-{m:02d}-{d:02d} {hh:02d}:{mi:02d}:{s:02d}"


def which_period_years(mo_deg, cur_lvl=1, max_lvl=3):
    dy = dasa_years()
    idx, frac = find_nakshatra(mo_deg)

    result = {}
    # Level 1 (always calculated)
    lvl1_lord = NAKSATRAS27[idx][0]
    lvl1_seq = get_lord_seq(lvl1_lord)
    lvl1_portion = frac
    lvl1_years = dy[lvl1_lord]
    lvl1_rem = (1 - lvl1_portion) * lvl1_years
    result["lvl1"] = {
        "lord": lvl1_lord,
        "portion": lvl1_portion,
        "years": lvl1_years,
        "rem": lvl1_rem,
    }

    # Level 2
    if 2 <= cur_lvl <= max_lvl:
        lvl2_idx_f = frac * 9
        lvl2_idx = int(lvl2_idx_f)
        lvl2_frac = lvl2_idx_f - lvl2_idx
        lvl2_lord = lvl1_seq[lvl2_idx]
        lvl2_seq = get_lord_seq(lvl2_lord)
        lvl2_years = lvl1_years * dy[lvl2_lord] / 120
        lvl2_rem = (1 - lvl2_frac) * lvl2_years
        result["lvl2"] = {
            "lord": lvl2_lord,
            "portion": lvl2_frac,
            "years": lvl2_years,
            "rem": lvl2_rem,
        }
    else:
        # Initialize default values if not calculated
        lvl2_frac = 0.0
        lvl2_seq = []
        lvl2_lord = None  # Or a suitable default/error handling

    # Level 3
    if 3 <= cur_lvl <= max_lvl:
        lvl3_idx_f = lvl2_frac * 9
        lvl3_idx = int(lvl3_idx_f)
        lvl3_frac = lvl3_idx_f - lvl3_idx
        lvl3_lord = lvl2_seq[lvl3_idx] if lvl2_seq else None  # Ensure lvl2_seq exists
        lvl3_seq = get_lord_seq(lvl3_lord) if lvl3_lord else []
        lvl3_years = (
            result["lvl2"]["years"] * dy[lvl3_lord] / 120
            if "lvl2" in result and lvl3_lord
            else 0.0
        )
        lvl3_rem = (1 - lvl3_frac) * lvl3_years
        result["lvl3"] = {
            "lord": lvl3_lord,
            "portion": lvl3_frac,
            "years": lvl3_years,
            "rem": lvl3_rem,
        }
    else:
        lvl3_frac = 0.0
        lvl3_seq = []
        lvl3_lord = None

    # Level 4
    if 4 <= cur_lvl <= max_lvl:
        lvl4_idx_f = lvl3_frac * 9
        lvl4_idx = int(lvl4_idx_f)
        lvl4_frac = lvl4_idx_f - lvl4_idx
        lvl4_lord = lvl3_seq[lvl4_idx] if lvl3_seq else None  # Ensure lvl3_seq exists
        lvl4_seq = get_lord_seq(lvl4_lord) if lvl4_lord else []
        lvl4_years = (
            result["lvl3"]["years"] * dy[lvl4_lord] / 120
            if "lvl3" in result and lvl4_lord
            else 0.0
        )
        lvl4_rem = (1 - lvl4_frac) * lvl4_years
        result["lvl4"] = {
            "lord": lvl4_lord,
            "portion": lvl4_frac,
            "years": lvl4_years,
            "rem": lvl4_rem,
        }
    else:
        lvl4_frac = 0.0
        lvl4_seq = []
        lvl4_lord = None

    # Level 5
    if 5 <= cur_lvl <= max_lvl:
        lvl5_idx_f = lvl4_frac * 9
        lvl5_idx = int(lvl5_idx_f)
        lvl5_frac = lvl5_idx_f - lvl5_idx
        lvl5_lord = lvl4_seq[lvl5_idx] if lvl4_seq else None  # Ensure lvl4_seq exists
        # lvl5_seq = get_lord_seq(lvl5_lord) if lvl5_lord else []
        lvl5_years = (
            result["lvl4"]["years"] * dy[lvl5_lord] / 120
            if "lvl4" in result and lvl5_lord
            else 0.0
        )
        lvl5_rem = (1 - lvl5_frac) * lvl5_years
        result["lvl5"] = {
            "lord": lvl5_lord,
            "portion": lvl5_frac,
            "years": lvl5_years,
            "rem": lvl5_rem,
        }

    return result


def vimsottari_table(mo_deg, e1_jd, e2_jd=None, current_lvl=1, max_lvl=3, lvl_indent=3):
    # single func: calculates and formats vimsottari table as plain text
    dy = dasa_years()
    # Pass current_lvl and max_lvl to which_period_years
    res = which_period_years(mo_deg, cur_lvl=current_lvl, max_lvl=max_lvl)
    # prepare header text
    idx, frac = find_nakshatra(mo_deg)
    nak_lord, nak_name = NAKSATRAS27[idx]
    separ = f"{'-' * 35}\n"
    header = (
        f"\n 'v' : toggle dasas level\n"
        " level 1 & 2 : complete dasas\n"
        " levels 3-5 : event 2 (ie current) maha dasa only\n"
        f"{separ}"
        f" nak {idx:02} {nak_name} {nak_lord} | traversed "
        f"{frac * 100:.2f} %\n{separ}"
    )

    lvl1_lord = res["lvl1"]["lord"]
    lvl1_seq = get_lord_seq(lvl1_lord)
    lvl1_idx = lvl1_seq.index(lvl1_lord)

    year_length = 365.2425
    cur_jd = e1_jd
    out = ""

    for mi in range(9):
        lord_lvl1 = lvl1_seq[(lvl1_idx + mi) % 9]
        years_lvl1 = dy[lord_lvl1]
        rem_years_lvl1 = res["lvl1"]["rem"] if mi == 0 else years_lvl1

        start_lvl1 = jd_to_date(cur_jd)
        lvl1_str = f"{lord_lvl1:<2} {rem_years_lvl1:.4f} y | {start_lvl1}"
        out += lvl1_str + "\n"

        if current_lvl >= 2:
            lvl2_seq = get_lord_seq(lord_lvl1)
            lvl2_idx_start = int(res["lvl1"]["portion"] * 9) if mi == 0 else 0
            lvl2_portion_current = res["lvl2"]["portion"] if mi == 0 else 0.0
            lvl2_jd = cur_jd

            for ai in range(lvl2_idx_start, 9):
                lord_lvl2 = lvl2_seq[ai % 9]
                years_lvl2 = years_lvl1 * dy[lord_lvl2] / 120
                rem_years_lvl2 = (
                    res["lvl2"]["rem"]
                    if mi == 0 and ai == lvl2_idx_start
                    else years_lvl2
                )
                start_lvl2 = jd_to_date(lvl2_jd)
                lvl2_str = f"{lord_lvl2:<2} {rem_years_lvl2:.4f} y | {start_lvl2}"
                out += " " * lvl_indent + lvl2_str + "\n"

                if current_lvl >= 3:
                    lvl3_seq = get_lord_seq(lord_lvl2)
                    lvl3_idx_start = (
                        int(lvl2_portion_current * 9)
                        if mi == 0 and ai == lvl2_idx_start
                        else 0
                    )
                    lvl3_jd = lvl2_jd

                    for pi in range(lvl3_idx_start, 9):
                        lord_lvl3 = lvl3_seq[pi % 9]
                        years_lvl3 = rem_years_lvl2 * dy[lord_lvl3] / 120
                        rem_years_lvl3 = (
                            res["lvl3"]["rem"]
                            if mi == 0 and ai == lvl2_idx_start and pi == lvl3_idx_start
                            else years_lvl3
                        )
                        start_lvl3 = jd_to_date(lvl3_jd)
                        lvl3_str = (
                            f"{lord_lvl3:<2} {rem_years_lvl3:.4f} y | {start_lvl3}"
                        )
                        out += " " * (2 * lvl_indent) + lvl3_str + "\n"

                        if current_lvl >= 4:
                            lvl4_seq = get_lord_seq(lord_lvl3)
                            # To get the correct portion for calculating start index of lvl4
                            # We need the portion of the current lvl3 lord *within its own sub-period*.
                            # This portion is found in `res["lvl3"]["portion"]` ONLY IF
                            # the current lvl3 lord is the one that's active at the birth moment.
                            # Otherwise, for subsequent lords, the portion is 0.
                            lvl4_idx_start = (
                                int(res["lvl3"]["portion"] * 9)
                                if mi == 0
                                and ai == lvl2_idx_start
                                and pi == lvl3_idx_start
                                else 0
                            )
                            lvl4_jd = lvl3_jd

                            for xi in range(lvl4_idx_start, 9):
                                lord_lvl4 = lvl4_seq[xi % 9]
                                years_lvl4 = rem_years_lvl3 * dy[lord_lvl4] / 120
                                rem_years_lvl4 = (
                                    res["lvl4"]["rem"]
                                    if mi == 0
                                    and ai == lvl2_idx_start
                                    and pi == lvl3_idx_start
                                    and xi == lvl4_idx_start
                                    else years_lvl4
                                )
                                start_lvl4 = jd_to_date(lvl4_jd)
                                lvl4_str = f"{lord_lvl4:<2} {rem_years_lvl4:.4f} y | {start_lvl4}"
                                out += " " * (3 * lvl_indent) + lvl4_str + "\n"

                                if current_lvl >= 5:
                                    lvl5_seq = get_lord_seq(lord_lvl4)
                                    # Similar logic for lvl5 start index
                                    lvl5_idx_start = (
                                        int(res["lvl4"]["portion"] * 9)
                                        if mi == 0
                                        and ai == lvl2_idx_start
                                        and pi == lvl3_idx_start
                                        and xi == lvl4_idx_start
                                        else 0
                                    )
                                    lvl5_jd = lvl4_jd

                                    for yi in range(lvl5_idx_start, 9):
                                        lord_lvl5 = lvl5_seq[yi % 9]
                                        years_lvl5 = (
                                            rem_years_lvl4 * dy[lord_lvl5] / 120
                                        )
                                        rem_years_lvl5 = (
                                            res["lvl5"]["rem"]
                                            if mi == 0
                                            and ai == lvl2_idx_start
                                            and pi == lvl3_idx_start
                                            and xi == lvl4_idx_start
                                            and yi == lvl5_idx_start
                                            else years_lvl5
                                        )
                                        start_lvl5 = jd_to_date(lvl5_jd)
                                        lvl5_str = f"{lord_lvl5:<2} {rem_years_lvl5:.4f} y | {start_lvl5}"
                                        out += " " * (4 * lvl_indent) + lvl5_str + "\n"
                                        lvl5_jd += rem_years_lvl5 * year_length
                                lvl4_jd += rem_years_lvl4 * year_length
                        lvl3_jd += rem_years_lvl3 * year_length
                lvl2_jd += rem_years_lvl2 * year_length
        cur_jd += rem_years_lvl1 * year_length
    return header + out.rstrip()


def calculate_vimsottari(event: str):
    # grab application data & calculate vimsottari for event 1
    app = Gtk.Application.get_default()
    notify = app.notify_manager
    msg = f"event {event}\n"
    # event 1 data is mandatory and main source
    if not app.e1_sweph.get("jd_ut"):
        notify.error(
            "missing event one data needed for vimsottari\n\texiting ...",
            source="vimsottari",
            route=["terminal", "user"],
        )
        return
    # skip e2 calculations for vimsottari dasas
    if event == "e2":
        # event = "e1"
        msg += "e2 detected : todo what ???\n"
    # get data
    e1_lumies = getattr(app, "e1_lumies", None)
    mo_lon = 0.0
    if e1_lumies:
        e1_jd = e1_lumies.get("jd_ut")
        # build name-keyed dict from int keys
        for v in e1_lumies.values():
            if isinstance(v, dict) and v.get("name") == "mo":
                # grab moon position
                mo_lon = v.get("lon")
                # msg += f"mo : {mo_lon:7.3f}\n"
                break
    e2_jd = app.e2_lumies.get("jd_ut") if hasattr(app, "e2_lumies") else None
    if not e2_jd:
        msg += "no e2jd"
    # msg += (
    #     f"vimso data :\n"
    #     f"lums : {e1_lumies}\n"
    #     f"e1jd : {e1_jd}\n"
    #     # f"e1lumpos : {e1_lum_pos}\n"
    #     f"e1pos : {str(e1_pos)[:800]}\n"
    #     f"e2jd : {e2_jd}\n"
    # )
    if not mo_lon or not e1_jd:
        notify.error(
            "missing luminaries data : exiting ...",
            source="vimsottari",
            route=["terminal"],
        )
        return
    current_lvl = getattr(app, "current_lvl", 1)
    max_lvl = 5
    msg += f"cur lvl : {current_lvl}\n"
    event_dasas = vimsottari_table(
        mo_lon,
        e1_jd,
        e2_jd,
        current_lvl=current_lvl,
        max_lvl=max_lvl,
        lvl_indent=3,
    )
    msg += f"dasas :\n{str(event_dasas)[:800]}"
    # msg += f"dasas : {event_dasas[:3000]}"
    app.signal_manager._emit("vimsottari_changed", event, event_dasas)
    notify.debug(
        msg,
        source="vimsottari",
        route=["terminal"],
    )


def connect_signals_vimsottari(signal_manager):
    """update vimsottari when positions of luminaries change"""
    signal_manager._connect("luminaries_changed", calculate_vimsottari)
