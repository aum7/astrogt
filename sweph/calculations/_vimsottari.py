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


def which_period_years(mo_deg, lvl_depth=5):
    # calculate full nested periods for all 9 branches at each level.
    # for the active branch (index 0) use the given fraction; all others
    # start from 0, so they represent the whole period
    dy = dasa_years()
    idx, frac = find_nakshatra(mo_deg)
    init_lord = NAKSATRAS27[idx][0]
    # level1 duration is fixed from dasa_years based on lord
    init_dur = dy[init_lord]

    def rec(level, curr_lord, curr_dur, curr_frac):
        lst = get_lord_seq(curr_lord)
        periods = []
        for i in range(9):
            # for active branch, use provided fraction to take only
            # remaining part of the period; for inactive, use full period.
            if i == 0:
                period_duration = (1 - curr_frac) * curr_dur
                # compute new fraction for next level from active branch
                new_idx_f = curr_frac * 9
                new_idx = int(new_idx_f)
                new_frac = new_idx_f - new_idx
                # guard against index overflow
                if new_idx >= 9:
                    new_idx = 8
                    new_frac = 0.0
                new_lord = lst[new_idx]
                new_dur = period_duration * dy[new_lord] / 120
                period_portion = curr_frac
            else:
                # inactive branch always starts from 0 fraction,
                # and its duration is computed proportional to parent's
                # period
                new_lord = lst[i]
                period_duration = curr_dur * dy[new_lord] / 120
                new_dur = period_duration  # next level from full period
                new_frac = 0.0
                period_portion = 0.0
            period = {
                "lord": lst[i],
                "portion": period_portion,
                "duration": period_duration,
                "rem": period_duration,  # remaining equals full period here
            }
            if level < lvl_depth:
                period["subperiods"] = rec(level + 1, new_lord, new_dur, new_frac)
            periods.append(period)
        return periods

    return rec(1, init_lord, init_dur, frac)


def vimsottari_table(mo_deg, jd, current_lvl=1, lvl_depth=5, lvl_indent=3, e2_jd=None):
    # calculate and format vimsottari table as plain text.
    # adjust lvl1 start datetime using birth jd and fraction passed.
    idx, frac = find_nakshatra(mo_deg)
    nak_lord, nak_name = NAKSATRAS27[idx]
    dy = dasa_years()
    year_length = 365.2425  # gregorian year length in days

    # compute full nested periods
    all_periods = which_period_years(mo_deg, lvl_depth=lvl_depth)
    print(f"vimso data : {str(all_periods)[:800]}")

    separ = f"{'-' * 34}\n"
    header = (
        f"\n 'v' : toggle dasas level\n{separ}"
        f" nak {idx:02} {nak_name} {nak_lord} | traversed "
        f"{frac * 100:.2f} %\n{separ}"
    )

    # determine correct start jd for current lvl1 period.
    init_lord = NAKSATRAS27[idx][0]
    init_dur = dy[init_lord]
    passed = init_dur * frac  # elapsed years in current period
    start_lvl1 = jd - (passed * year_length)

    # convert e2_jd to float if needed
    if e2_jd is not None and isinstance(e2_jd, str):
        try:
            e2_jd = float(e2_jd)
        except Exception:
            e2_jd = None

    def format_periods(periods, level, cur_jd):
        lines = ""
        new_cur_jd = cur_jd
        # loop through each period at this level
        for period in periods:
            period_start = new_cur_jd
            period_end = period_start + (period["rem"] * year_length)
            # if filtering by e2_jd, only display the period that
            # contains e2_jd at this level
            if level >= current_lvl and e2_jd is not None:
                if not (period_start <= e2_jd < period_end):
                    new_cur_jd = period_end
                    continue
            indent = " " * ((level - 1) * lvl_indent)
            line = (
                f"{indent}{period['lord']:<2} "
                f"{period['rem']:.4f} y | "
                f"{jd_to_date(period_start)}"
            )
            lines += line + "\n"
            if "subperiods" in period and level < lvl_depth:
                sub_lines = ""
                # when filtering by e2_jd, descend only into the subperiod
                # that contains e2_jd
                if level + 1 >= current_lvl and e2_jd is not None:
                    sub_cur = period_start
                    for sub in period["subperiods"]:
                        sub_start = sub_cur
                        sub_end = sub_start + (sub["rem"] * year_length)
                        if sub_start <= e2_jd < sub_end:
                            sub_lines, sub_cur = format_periods(
                                [sub], level + 1, sub_start
                            )
                            break
                        sub_cur = sub_end
                else:
                    sub_lines, _ = format_periods(
                        period["subperiods"], level + 1, period_start
                    )
                lines += sub_lines
            new_cur_jd = period_end
        return lines, new_cur_jd

    table_str, _ = format_periods(all_periods, 1, start_lvl1)
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
    msg += f"dasas : {str(event_dasas)[:800]}"
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
