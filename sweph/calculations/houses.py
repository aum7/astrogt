# sweph/calculations/houses.py
# ruff: noqa: E402, E701
import swisseph as swe
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore
from typing import Optional, Tuple, List


def calculate_houses(event: Optional[str] = None) -> Tuple:
    """calculate houses & ascendant & midheaven + planet sign"""
    # ascmc : 0 asc 1 mc 2 armc 3 vertex 4 equ. asc
    # 5 co-asc koch 6 co-asc munkasey 7 polar asc munkasey
    app = Gtk.Application.get_default()
    notify = app.notify_manager
    # event 1 data is manadatory : already validated in positions.py
    events: List[str] = [event] if event else ["e1", "e2"]
    if "e2" in events and not app.e2_sweph.get("jd_ut"):
        # skip event two if no datetime / julian day utc set = user not interested
        events.remove("e2")
    notify.debug(
        f"events : {events}",
        source="houses",
        route=["none"],
    )
    for event in events:
        sweph = app.e1_sweph if event == "e1" else app.e2_sweph
        hsys = app.selected_house_system
        sweph_flag = app.sweph_flag
        jd_ut = sweph.get("jd_ut")
        notify.debug(
            f"\n\thouse system : {hsys}\n\tswephflag : {sweph_flag}\n\tjdut : {jd_ut}",
            source="houses",
            route=["none"],
        )
        try:
            cusps, ascmc = swe.houses_ex(
                jd_ut,
                sweph["lat"],
                sweph["lon"],
                hsys.encode("ascii"),
                sweph_flag,
            )
            return (cusps, ascmc)
        except swe.Error as e:
            raise ValueError(f"house calculation :\n\terror\n\t{e}")
    return ([], [])
