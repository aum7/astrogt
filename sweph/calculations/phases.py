# sweph/calculations/aspects.py
# ruff: noqa: E402, E701
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore

# fixed slowest->fastest order by synodic period
SLOW_ORDER = ["pl", "ne", "ur", "sa", "ra", "ju", "ma", "su", "ve", "me", "mo"]


def angle_diff(a: float, b: float) -> float:
    """angular distance from a to b forward 0..360"""
    return (b - a) % 360.0


def phase_pair(lon_slow: float, lon_fast: float):
    """compute raw angle, signed phase (+/-) and separation <=180"""
    raw = angle_diff(lon_slow, lon_fast)  # 0..360
    if raw <= 180.0:
        angle = raw
        phase = "+"
    else:
        angle = 360.0 - raw
        phase = "-"
    return raw, angle, phase


def compound_column(col_idx, ordered, pos_map):
    # compute cumulative phase per column
    col_name = ordered[col_idx]
    num = len(ordered)
    compound_vals = [None for _ in range(num)]
    synodic_vals = [None for _ in range(num)]
    # initial value (diagonal)
    compound = None
    for row_idx in range(num):
        # row_name = ordered[row_idx]
        if row_idx == col_idx:
            compound_vals[row_idx] = None
            synodic_vals[row_idx] = None
            continue
        # get synodic value for col-row pair
        lon_slow = pos_map[col_name]["lon"]
        lon_fast = pos_map[ordered[row_idx]]["lon"]
        raw, angle, phase = phase_pair(lon_slow, lon_fast)
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
            compound %= 360.0
        compound_vals[row_idx] = compound
    return synodic_vals, compound_vals


def phases_matrix(ordered, pos_map):
    # make phases table matrix
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
                continue
            synodic_vals, compound_vals = compound_column(col_idx, ordered, pos_map)
            # if synodic_vals and compound_vals:
            angle, phase = synodic_vals[row_idx]
            compound = compound_vals[row_idx]
            cell = {
                "angle": round(angle, 1) if angle else None,
                "phase": phase,
                "compound": round(compound, 1) if compound else None,
                "type": "phase",
            }
            row.append(cell)
        matrix.append(row)
    return ordered, matrix


def calculate_phases(event: str):
    # calculate compound phase table for event
    app = Gtk.Application.get_default()
    notify = app.notify_manager
    if event not in ("e1", "e2"):
        return
    pos = getattr(app, f"{event}_positions", None)
    if not pos:
        notify.error(
            f"missing positions for {event} : exiting ...",
            source="phases",
            route=["terminal"],
        )
        return
    # build name -> obj map (only numeric keys)
    pos_map = {v["name"]: v for k, v in pos.items() if isinstance(k, int)}
    # filter slow order by available names
    ordered = [n for n in SLOW_ORDER if n in pos_map]
    obj_names, phase_matrix = phases_matrix(ordered, pos_map)
    phases_data = {
        "obj names": obj_names,
        "matrix": phase_matrix,
    }
    # debug print
    msg = "\n--- phases matrix ---\n"
    # header
    msg += " > | " + "          | ".join(obj_names) + "\n"
    num = len(obj_names)
    for row_idx in range(num):
        row_label = obj_names[row_idx]
        msg += f"{row_label:>2} |"
        for col_idx in range(num):
            cell = phase_matrix[row_idx][col_idx]
            if cell["type"] == "diag":
                msg += " *********** |"
            else:
                angle = cell["angle"]
                phase = cell["phase"]
                compound = cell["compound"]
                val = f"{angle:5.1f} {phase}{compound:6.1f}|"
                msg += f"{val}"
        msg += "\n"
    app.signal_manager._emit("phases_changed", event, phases_data)
    notify.debug(
        msg,
        source="phases",
        route=["terminal"],
    )


def connect_signals_phases(signal_manager):
    """update phases when positions change"""
    signal_manager._connect("positions_changed", calculate_phases)
