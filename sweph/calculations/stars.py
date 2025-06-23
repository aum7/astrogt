# sweph/calculations/start.py
# ruff: noqa: E402
# swe.fixstar2_ut : star name (catalog or nomenclature), tjd_ut, flags
# returns : (lon, lat, dist, speeds : lon, lat, dist), star name, flags used
# eta tauri : ("Alcyone", "Alcyone, Krttika", "etTau"),
import swisseph as swe
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore
from typing import Optional, List


def calculate_stars(event: Optional[str] = None) -> None:
    """calculate positions of start, listed in user/fixedstart.txt"""
    app = Gtk.Application.get_default()
    notify = app.notify_manager
    print(f"stars : olo : {event}")
    events: List[str] = [event] if event else ["e1", "e2"]
    if "e2" in events and not app.e2_sweph.get("jd_ut"):
        events.remove("e2")
    # todo draw all 27 / 28 naksatras stars in naksatras ring


def connect_signals_stars(signal_manager):
    signal_manager._connect("settings_changed", calculate_stars)
    # signal_manager._connect("event_changed", calculate_stars)
