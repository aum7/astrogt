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


def which_period_years(mo_deg, lvl_depth=5):
    dy = dasa_years()
    idx, frac = find_nakshatra(mo_deg)
    init_lord = NAKSATRAS27[idx][0]
    init_dur = dy[init_lord]

    def rec(level, curr_lord, curr_dur, curr_portion):
        periods = []
        lst = get_lord_seq(curr_lord)
        for i in range(9):
            if i == 0:
                # use calculated remainder and portion
                portion = curr_portion
                rem = (1 - portion) * curr_dur
                next_idx = int(curr_portion * 9)
                new_portion = (curr_portion * 9) - next_idx
                period_dur = rem
                new_lord = lst[next_idx]
                new_dur = curr_dur * dy[new_lord] / 120
            else:
                portion = 0
                period_dur = dy[lst[i]]
                new_portion = 0
                new_dur = dy[lst[i]]
            period = {
                "lord": lst[i],
                "portion": portion,
                "duration": curr_dur if i == 0 else dy[lst[i]],
                "rem": period_dur,
            }
            if level < lvl_depth:
                period["subperiods"] = rec(level + 1, lst[i], new_dur, new_portion)
            periods.append(period)
        return periods

    return rec(1, init_lord, init_dur, frac)


def jd_to_date(jd):
    y, m, d, h = swe.revjul(jd, swe.GREG_CAL)
    hh = int(h)
    mi = int((h - hh) * 60)
    s = int((((h - hh) * 60) - mi) * 60)
    return f"{y:04d}-{m:02d}-{d:02d} {hh:02d}:{mi:02d}:{s:02d}"


def vimsottari_table(mo_deg, jd, current_lvl=1, lvl_depth=5, lvl_indent=3, e2_jd=None):
    # single func: calculates and formats vimsottari table as plain text
    idx, frac = find_nakshatra(mo_deg)
    nak_lord, nak_name = NAKSATRAS27[idx]
    dy = dasa_years()
    year_length = 365.2425  # gregorian year length in days

    # get period data for desired depth
    p_data = which_period_years(mo_deg, lvl_depth=current_lvl)
    print(f"vimso pdata : {p_data}")
    # prepare table as plain text
    separ = f"{'-' * 34}\n"
    header = f"\n 'v' : toggle dasas level\n{separ}"
    header += f" nak {idx:02} {nak_name} {nak_lord} | traversed {frac * 100:.2f} %"
    header += f"\n{separ}"

    def format_periods(periods, level, cur_jd):
        lines = ""
        # iterate over 9 periods at this level
        for period in periods:
            indent = " " * ((level - 1) * lvl_indent)
            line = (
                f"{indent}{period['lord']:<2} "
                f"{period['rem']:.4f} y | {jd_to_date(cur_jd)}"
            )
            lines += line + "\n"
            if ("subperiods" in period) and (level < current_lvl):
                sub_lines, cur_jd = format_periods(
                    period["subperiods"], level + 1, cur_jd
                )
                lines += sub_lines
            cur_jd += period["rem"] * year_length
        return lines, cur_jd

    table_str, _ = format_periods(p_data, 1, jd)
    return header + table_str.rstrip()


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
        msg += "e2 detected : todo maybe\n"
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
    e2_jd = app.e2_lumies.get("jd_ut") if hasattr(app, "e2_lumies") else "-"
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
    lvl_depth = 5
    msg += f"cur lvl : {current_lvl}\n"
    event_dasas = vimsottari_table(
        mo_lon,
        e1_jd,
        current_lvl=current_lvl,
        lvl_depth=lvl_depth,
        lvl_indent=3,
        e2_jd=e2_jd,
    )
    # msg += f"dasas : {event_dasas}"
    msg += f"dasas : {event_dasas[:3000]}"
    app.signal_manager._emit("vimsottari_changed", event, event_dasas)
    notify.debug(
        msg,
        source="vimsottari",
        route=["terminal"],
    )


def connect_signals_vimsottari(signal_manager):
    """update vimsottari when positions of luminaries change"""
    signal_manager._connect("luminaries_changed", calculate_vimsottari)
