# sweph/calculations/vimsottari.py
# output line num : lvl1-18 lvl2-91 lvl3-763 lvl4-6764 lvl5-61198
# ruff: noqa: E402, E701
import swisseph as swe
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore
# from typing import Optional, Dict, Any, List

from ui.mainpanes.panechart.chartcircles import NAKSATRAS27

YEARLENGTH = 365.2425


def dasa_years():
    # 9 maha dasa year lengths
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
    # naksatra index & fraction from moon longitude
    part = 360 / 27
    idx = int(mo_deg // part) + 1
    frac = (mo_deg % part) / part
    return idx, frac


def get_lord_seq(start_lord):
    # get naksatra lord data
    seq = [NAKSATRAS27[i][0] for i in range(1, 10)]
    idx = seq.index(start_lord)
    return seq[idx:] + seq[:idx]


def jd_to_date(jd):
    # julian day to year, month, day, hour, min, sec
    y, m, d, h = swe.revjul(jd, swe.GREG_CAL)
    H = int(h)
    M = int((h - H) * 60)
    S = int((((h - H) * 60) - M) * 60)
    return f"{y:04d}-{m:02d}-{d:02d} {H:02d}:{M:02d}:{S:02d}"


def period_to_ymd(period):
    # decimal period to years, months, days
    y = int(period)
    rem_y = period - y
    dec_m = rem_y * 12
    m = int(dec_m)
    rem_m = dec_m - m
    rem_d = rem_m * (YEARLENGTH / 12)
    d = int(rem_d)
    rem_h = rem_d * 24
    H = int(rem_h)
    if y != 0 and m == 0 and d == 0:
        return f"{y:02} y"
    elif y == 0 and m == 0 and d == 0:
        return f"{H:02} h"
    elif y == 0 and m == 0:
        return f"{d:02d} d"
    elif y == 0:
        return f"{m:02d} m {d:02d} d"
    return f"{y:02d} y {m:02d} m {d:02d} d"


# gemini code
def initial_dasa(mo_deg, cur_lvl=1, max_lvl=3):
    # 1st dasa length is fractional by moon longitude
    dy = dasa_years()
    idx, frac = find_nakshatra(mo_deg)
    result = {}
    # level 1 (always calculated)
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
    # level 2
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
        lvl2_frac = 0.0
        lvl2_seq = []
        lvl2_lord = None
    # level 3
    if 3 <= cur_lvl <= max_lvl:
        lvl3_idx_f = lvl2_frac * 9
        lvl3_idx = int(lvl3_idx_f)
        lvl3_frac = lvl3_idx_f - lvl3_idx
        lvl3_lord = lvl2_seq[lvl3_idx] if lvl2_seq else None
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
    # level 4
    if 4 <= cur_lvl <= max_lvl:
        lvl4_idx_f = lvl3_frac * 9
        lvl4_idx = int(lvl4_idx_f)
        lvl4_frac = lvl4_idx_f - lvl4_idx
        lvl4_lord = lvl3_seq[lvl4_idx] if lvl3_seq else None
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
    # level 5
    if 5 <= cur_lvl <= max_lvl:
        lvl5_idx_f = lvl4_frac * 9
        lvl5_idx = int(lvl5_idx_f)
        lvl5_frac = lvl5_idx_f - lvl5_idx
        lvl5_lord = lvl4_seq[lvl5_idx] if lvl4_seq else None
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


def vimsottari_table(mo_deg, e1_jd, e2_jd=None, current_lvl=1, max_lvl=3):
    dy = dasa_years()
    # get data for initial dasa by level
    res = initial_dasa(mo_deg, cur_lvl=current_lvl, max_lvl=max_lvl)
    # prepare header text
    idx, frac = find_nakshatra(mo_deg)
    nak_lord, nak_name = NAKSATRAS27[idx]
    separ = f"{'-' * 35}\n"
    header = (
        f"\n 'v' : toggle dasas level\n"
        " level 1 & 2 : complete dasas\n"
        " levels 3-5 : (current) maha dasa only > needs event 2 datetime\n"
        f"{separ}"
        f" nak {idx:02} {nak_name} {nak_lord} | traversed "
        f"{frac * 100:.2f} %\n{separ}"
        # " lvl / lord - period in years-months-days | period start\n"
    )
    lvl1_lord_initial = res["lvl1"]["lord"]
    lvl1_seq = get_lord_seq(lvl1_lord_initial)
    lvl1_idx_initial = lvl1_seq.index(lvl1_lord_initial)
    # year_length = 365.2425
    cur_jd_lvl1 = e1_jd
    out = ""
    for l1 in range(9):
        lord_lvl1 = lvl1_seq[(lvl1_idx_initial + l1) % 9]
        years_lvl1 = dy[lord_lvl1]
        # Determine remaining years for the *initial* Maha Dasa, otherwise full years
        rem_years_lvl1 = res["lvl1"]["rem"] if l1 == 0 else years_lvl1
        start_lvl1 = cur_jd_lvl1
        end_lvl1 = cur_jd_lvl1 + rem_years_lvl1 * YEARLENGTH
        # Flag to indicate if e2_jd falls within the current lvl1 period
        e2_jd_inside_lvl1 = (e2_jd is not None) and (start_lvl1 <= e2_jd < end_lvl1)
        lvl1_str = (
            f" {lord_lvl1:<2} {jd_to_date(start_lvl1)} {period_to_ymd(rem_years_lvl1)}"
        )
        out += lvl1_str + "\n"
        # filter out level 2 if not level 1 'current' (e2jd) period
        # if e2_jd is not None and current_lvl >= 3 and not e2_jd_inside_lvl1:
        #     continue
        cur_jd_lvl2 = cur_jd_lvl1  # Initialize JD for lvl2 loop
        if current_lvl >= 2:
            lvl2_seq = get_lord_seq(lord_lvl1)
            # Determine starting index for Antardasa (lvl2)
            lvl2_idx_start = int(res["lvl1"]["portion"] * 9) if l1 == 0 else 0
            lvl2_portion_current = (
                res["lvl2"]["portion"] if l1 == 0 else 0.0
            )  # for use in lvl3 start index
            for l2 in range(lvl2_idx_start, 9):
                lord_lvl2 = lvl2_seq[l2 % 9]
                years_lvl2 = years_lvl1 * dy[lord_lvl2] / 120
                rem_years_lvl2 = (
                    res["lvl2"]["rem"]
                    if l1 == 0 and l2 == lvl2_idx_start
                    else years_lvl2
                )
                start_lvl2 = cur_jd_lvl2
                lvl2_str = (
                    f" {lord_lvl2:<2} "
                    f"{jd_to_date(start_lvl2)} "
                    f"{period_to_ymd(rem_years_lvl2)}"
                )
                out += " 2 " + lvl2_str + "\n"
                cur_jd_lvl3 = cur_jd_lvl2  # Initialize JD for lvl3 loop
                if current_lvl >= 3:
                    # skip level 3+ if e2_jd is none
                    # if e2_jd is not None and not e2_jd_inside_lvl1:
                    #     cur_jd_lvl3 += rem_years_lvl2 * year_length
                    #     continue
                    lvl3_seq = get_lord_seq(lord_lvl2)
                    lvl3_idx_start = (
                        int(lvl2_portion_current * 9)
                        if l1 == 0 and l2 == lvl2_idx_start
                        else 0
                    )
                    for l3 in range(lvl3_idx_start, 9):
                        lord_lvl3 = lvl3_seq[l3 % 9]
                        years_lvl3 = rem_years_lvl2 * dy[lord_lvl3] / 120
                        rem_years_lvl3 = (
                            res["lvl3"]["rem"]
                            if l1 == 0 and l2 == lvl2_idx_start and l3 == lvl3_idx_start
                            else years_lvl3
                        )
                        start_lvl3 = cur_jd_lvl3
                        lvl3_str = (
                            f" {lord_lvl3:<2} "
                            f"{jd_to_date(start_lvl3)} "
                            f"{period_to_ymd(rem_years_lvl3)}"
                        )
                        out += " 3    " + lvl3_str + "\n"
                        # advance jd for next lvl period
                        # cur_jd_lvl3 += rem_years_lvl3 * year_length
                        cur_jd_lvl4 = cur_jd_lvl3  # Initialize JD for lvl4 loop
                        if current_lvl >= 4:
                            lvl4_seq = get_lord_seq(lord_lvl3)
                            lvl4_idx_start = (
                                int(res["lvl3"]["portion"] * 9)
                                if l1 == 0
                                and l2 == lvl2_idx_start
                                and l3 == lvl3_idx_start
                                else 0
                            )
                            for l4 in range(lvl4_idx_start, 9):
                                lord_lvl4 = lvl4_seq[l4 % 9]
                                years_lvl4 = rem_years_lvl3 * dy[lord_lvl4] / 120
                                rem_years_lvl4 = (
                                    res["lvl4"]["rem"]
                                    if l1 == 0
                                    and l2 == lvl2_idx_start
                                    and l3 == lvl3_idx_start
                                    and l4 == lvl4_idx_start
                                    else years_lvl4
                                )
                                start_lvl4 = cur_jd_lvl4
                                lvl4_str = (
                                    f" {lord_lvl4:<2} "
                                    f"{jd_to_date(start_lvl4)} "
                                    f"{period_to_ymd(rem_years_lvl4)}"
                                )
                                out += " 4       " + lvl4_str + "\n"
                                # advance jd
                                cur_jd_lvl5 = cur_jd_lvl4  # Initialize JD for lvl5 loop
                                if current_lvl >= 5:
                                    lvl5_seq = get_lord_seq(lord_lvl4)
                                    lvl5_idx_start = (
                                        int(res["lvl4"]["portion"] * 9)
                                        if l1 == 0
                                        and l2 == lvl2_idx_start
                                        and l3 == lvl3_idx_start
                                        and l4 == lvl4_idx_start
                                        else 0
                                    )
                                    for l5 in range(lvl5_idx_start, 9):
                                        lord_lvl5 = lvl5_seq[l5 % 9]
                                        years_lvl5 = (
                                            rem_years_lvl4 * dy[lord_lvl5] / 120
                                        )
                                        rem_years_lvl5 = (
                                            res["lvl5"]["rem"]
                                            if l1 == 0
                                            and l2 == lvl2_idx_start
                                            and l3 == lvl3_idx_start
                                            and l4 == lvl4_idx_start
                                            and l5 == lvl5_idx_start
                                            else years_lvl5
                                        )
                                        start_lvl5 = cur_jd_lvl5
                                        lvl5_str = (
                                            f" {lord_lvl5:<2} "
                                            f"{jd_to_date(start_lvl5)} "
                                            f"{period_to_ymd(rem_years_lvl5)}"
                                        )
                                        out += "            " + lvl5_str + "\n"
                                        cur_jd_lvl5 += rem_years_lvl5 * YEARLENGTH
                                cur_jd_lvl4 += rem_years_lvl4 * YEARLENGTH
                        cur_jd_lvl3 += rem_years_lvl3 * YEARLENGTH
                cur_jd_lvl2 += rem_years_lvl2 * YEARLENGTH
        cur_jd_lvl1 += rem_years_lvl1 * YEARLENGTH
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
    e1_jd = None
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
        msg += "no e2jd\n"
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
    # on missing e2_jd notify user & cap current_lvl
    # if e2_jd is None and current_lvl >= 3:
    #     notify.warning(
    #         "event 2 datetime required for levels 3-5 : reseting to level 1",
    #         source="vimsottari",
    #         route=["terminal", "user"],
    #         timeout=4,
    #     )
    #     app.current_lvl = current_lvl = 1
    max_lvl = 5
    msg += f"cur lvl : {current_lvl}\n"
    event_dasas = vimsottari_table(
        mo_lon,
        e1_jd,
        e2_jd=e2_jd,
        current_lvl=current_lvl,
        max_lvl=max_lvl,
    )
    # msg += f"dasas :\n{str(event_dasas)[:800]}"
    app.signal_manager._emit("vimsottari_changed", event, event_dasas)
    notify.debug(
        msg,
        source="vimsottari",
        route=["terminal"],
    )


def connect_signals_vimsottari(signal_manager):
    """update vimsottari when positions of luminaries change"""
    signal_manager._connect("luminaries_changed", calculate_vimsottari)
