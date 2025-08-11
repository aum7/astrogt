# sweph/calculations/cyclicindex.py
# ruff: noqa: E402, E701
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore
from typing import List, Tuple, Optional

# fixed slowest->fastest order by synodic period todo ra yes no ???
SLOW_ORDER = ["pl", "ne", "ur", "sa", "ra", "ju", "ma", "su", "ve", "me", "mo"]


def angle_diff(a: float, b: float) -> float:
    """angular distance from a to b forward 0..360"""
    return (b - a) % 360.0


def cycle_pair(lon_slow: float, lon_fast: float):
    """compute raw angle, signed cycle phase (+/-) and separation <=180"""
    ang_diff = angle_diff(lon_slow, lon_fast)  # 0..360
    if ang_diff <= 180.0:
        angle = ang_diff
        phase = "+"
    else:
        angle = 360.0 - ang_diff
        phase = "-"
    return angle, phase


def compound_column(
    col_idx: int, ordered: List[str], pos_map: dict
) -> Tuple[List[Optional[Tuple[float, str]]], List[Optional[Tuple[float, str]]]]:
    # compute cumulative cycle per column
    col_name = ordered[col_idx]
    num = len(ordered)
    synodic_vals: List[Optional[Tuple[float, str]]] = [None] * num
    compound_vals: List[Optional[Tuple[float, str]]] = [None] * num
    compound: Optional[float] = None
    # initial value (diagonal)
    for row_idx in range(num):
        row_name = ordered[row_idx]
        if row_idx <= col_idx:
            compound_vals[row_idx] = None
            synodic_vals[row_idx] = None
            continue
        # get synodic value for col-row pair
        lon_slow = pos_map[col_name]["lon"]
        lon_fast = pos_map[row_name]["lon"]
        angle, phase = cycle_pair(lon_slow, lon_fast)
        synodic_vals[row_idx] = (angle, phase)
        # compound calculation
        if compound is None:
            compound = angle
        else:
            # add/subtract as per phase
            if phase == "+":
                compound = (compound + angle) % 360
            else:
                compound = (compound - angle) % 360
            # keep in 0..360
        compound_cycle = "+" if compound < 180 else "-"
        compound_vals[row_idx] = (compound, compound_cycle)
    return synodic_vals, compound_vals


def cycles_matrix(ordered, pos_map):
    # make cycles table matrix
    num = len(ordered)
    matrix = []
    for row_idx in range(num):
        row = []
        for col_idx in range(num):
            if row_idx == col_idx:
                row.append({
                    "angle": None,
                    "phase": None,
                    "compound": None,
                    "type": "diag",
                })
            elif row_idx < col_idx:
                # above-diagonal cells : empty
                row.append({
                    "angle": None,
                    "phase": None,
                    "compound": None,
                    "type": "skip",
                })
            else:
                synodic_vals, compound_vals = compound_column(col_idx, ordered, pos_map)
                synodic_val = synodic_vals[row_idx]
                if synodic_val is not None:
                    angle, phase = synodic_val
                else:
                    angle, phase = None, None
                compound = compound_vals[row_idx]
                cell = {
                    "angle": round(angle, 1) if angle else None,
                    "phase": phase,
                    "compound": (round(compound[0], 1), compound[1])
                    if compound
                    else None,
                    "type": "phase",
                }
                row.append(cell)
        matrix.append(row)
    return ordered, matrix


def calculate_cycles(event: str):
    # calculate compound cycle table for event
    app = Gtk.Application.get_default()
    notify = app.notify_manager
    if event not in ("e1", "e2"):
        return
    division = int(app.chart_settings.get("harmonic ring", "1").strip())
    use_varga = app.chart_settings.get("use varga", False)
    pos = getattr(app, f"{event}_positions", None)
    if not pos:
        notify.error(
            f"missing positions for {event} : exiting ...",
            source="cyclicindex",
            route=["terminal"],
        )
        return
    if use_varga and division > 1:
        pos_map = {
            v["name"]: {"name": v["name"], "lon": v["varga"]}
            for k, v in pos.items()
            if isinstance(k, int)
            # if "name" in v and "lon" in v
        }
    else:
        pos_map = {v["name"]: v for k, v in pos.items() if isinstance(k, int)}
    # filter slow order by available names
    ordered = [n for n in SLOW_ORDER if n in pos_map]
    obj_names, cycle_matrix = cycles_matrix(ordered, pos_map)
    cycles_data = {
        "obj names": obj_names,
        "matrix": cycle_matrix,
    }
    # debug print
    msg = f"\n--- {event} cyclic index matrix ---\n"
    # header
    msg += " > | " + "            | ".join(obj_names) + "\n"
    num = len(obj_names)
    for row_idx in range(num):
        row_label = obj_names[row_idx]
        msg += f"{row_label:>2} |"
        for col_idx in range(num):
            cell = cycle_matrix[row_idx][col_idx]
            if cell["type"] == "diag":
                msg += " ************* |"
            else:
                angle = cell["angle"]
                phase = cell["phase"]
                compound = cell["compound"]
                if angle is not None and compound is not None:
                    val = f"{angle:5.1f} {phase}{compound[0]:6.1f} {compound[1]}|"
                elif angle is not None:
                    val = f"{angle:5.1f} {phase}       |"
                else:
                    val = "       -       |"
                msg += f"{val}"
        msg += "\n"
    app.signal_manager._emit("cycles_changed", event, cycles_data)
    notify.debug(
        msg,
        source="cyclicindex",
        route=["terminal"],
    )


def connect_signals_cycles(signal_manager):
    """update cyclic index when positions change"""
    signal_manager._connect("positions_changed", calculate_cycles)
    signal_manager._connect("settings_changed", calculate_cycles)
