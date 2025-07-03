# sweph/calculations/vimsottari.py
# ruff: noqa: E402, E701
import swisseph as swe
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore
from typing import Optional, Dict, Any, List

# from datetime import timedelta
from ui.mainpanes.panechart.chartcircles import NAKSATRAS27


def calculate_vimsottari(event: Optional[str] = None, luminaries: Dict[str, Any] = {}):
    """calculate aspectarian for one or both events"""
    app = Gtk.Application.get_default()
    # start_jd_ut = luminaries.get("jd_ut")
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
    start_jd_ut = luminaries.get("start_jd_ut")
    if not moon or not start_jd_ut:
        notify.error(
            "missing luminaries data\n\texiting ...",
            source="vimsottari",
            route=["terminal"],
        )
        return
    mo_lon = moon["lon"]
    # print(f"vimsottari : moon lon : {mo_lon}")
    nak_length = 360 / 27
    nak_idx = int(mo_lon // nak_length) + 1
    nak_frac = (mo_lon % nak_length) / nak_length
    start_lord, _ = NAKSATRAS27[nak_idx]
    event_dasas = get_vimsottari_periods(notify, start_jd_ut, start_lord, nak_frac)
    app.signal_manager._emit("vimsottari_changed", event, event_dasas)
    notify.debug(
        f"start_jd_ut : {start_jd_ut}\n\tdasas : {event_dasas}",
        source="vimsottari",
        route=["none"],
    )


def get_vimsottari_periods(notify, start_jd_ut, start_lord, start_frac=0.0, levels=3):
    dasa_years = {
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
    lord_seq = list(dasa_years.keys())
    start_idx = lord_seq.index(start_lord)

    def recurse(start_jd_ut, level, years, lord_seq):
        dasas = []
        for i in range(9):
            lord = lord_seq[(start_idx + i) % 9] if level == 0 else lord_seq[i]
            duration = years * dasa_years[lord] / 120
            if level == 0 and i == 0:
                duration *= 1 - start_frac
            days = duration * 365.2425
            jd_end = start_jd_ut + days
            entry = {
                "lord": lord,
                "years": round(duration, 4),
                "from": swe.revjul(start_jd_ut, cal=swe.GREG_CAL),
                "to": swe.revjul(jd_end),
            }
            if level + 1 < levels:
                entry["sub"] = recurse(start_jd_ut, level + 1, duration, lord_seq)
            dasas.append(entry)
            start_jd_ut = jd_end
        notify.info(
            f"duration :{duration:5.2f} years",
            source="vimsottari",
            route=["none"],
        )
        return dasas

    return recurse(start_jd_ut, 0, dasa_years[start_lord], lord_seq)


# Helper functions for vimsottari_table
def find_nakshatra(mo_lon):
    """Find nakshatra and percentage from moon longitude"""
    nak_length = 360 / 27
    nak_idx = int(mo_lon // nak_length) + 1
    nak_frac = (mo_lon % nak_length) / nak_length
    start_lord, nak_name = NAKSATRAS27[nak_idx]
    return nak_idx, nak_name, start_lord, nak_frac


def dasa_years():
    """Get the dasa years mapping - reuse existing calculation"""
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


def get_lord_seq():
    """Get the sequence of lords - reuse existing calculation"""
    return list(dasa_years().keys())


def which_period_years(start_lord, start_frac):
    """Get remainder and portion for periods - reuse existing calculations"""
    years = dasa_years()
    main_years = years[start_lord]
    remainder = main_years * (1 - start_frac)
    portion = start_frac
    
    return {
        "maha": {"remainder": remainder, "portion": portion},
        "antara": {"remainder": remainder, "portion": portion},
        "praty": {"remainder": remainder, "portion": portion}
    }


def vimsottari_table(mo_lon, start_jd_ut, current_lvl=3):
    """
    Recursive implementation to display vimsottari periods with controlled depth.
    
    Args:
        mo_lon: Moon longitude 
        start_jd_ut: Starting Julian day UTC
        current_lvl: Maximum level to display (1-5)
        
    Returns:
        String representation of the vimsottari table
    """
    # Get nakshatra information using find_nakshatra
    nak_idx, nak_name, start_lord, nak_frac = find_nakshatra(mo_lon)
    years = dasa_years()
    lord_seq = get_lord_seq()
    start_idx = lord_seq.index(start_lord)
    
    # Get remainder and portion values using which_period_years  
    res = which_period_years(start_lord, nak_frac)
    
    # Preserve original header showing nakshatra information
    header = f"Vimsottari Dasa Table\n"
    header += f"Nakshatra: {nak_name} ({nak_idx}) - Lord: {start_lord}\n"
    header += f"Percentage: {nak_frac:.2%}\n"
    header += f"{'='*50}\n"
    
    def recurse_periods(jd_start, level, period_years, lords, indent=""):
        """Recursive function to generate periods at each level"""
        if level > current_lvl:
            return ""
        
        result = ""
        current_jd = jd_start
        
        # Iterate 9 times for the 9 periods at each level
        for i in range(9):
            # Get the lord for this period
            if level == 1:
                lord = lords[(start_idx + i) % 9]
            else:
                lord = lords[i]
            
            # Calculate duration using existing calculations
            duration = period_years * years[lord] / 120
            
            # For levels 1-3, if it is the first period (i==0), use remainder and portion
            if level <= 3 and i == 0:
                level_keys = ["maha", "antara", "praty"]
                level_key = level_keys[level - 1]
                if level_key in res:
                    duration = res[level_key]["remainder"]
            
            # Time calculations using gregorian year length of 365.2425 days
            days = duration * 365.2425
            jd_end = current_jd + days
            
            # Format dates (simplified for testing, would use swe.revjul in real implementation)
            try:
                if hasattr(swe, 'revjul'):
                    from_date = swe.revjul(current_jd, cal=swe.GREG_CAL)
                    to_date = swe.revjul(jd_end, cal=swe.GREG_CAL)
                    from_str = f"{from_date[2]:02d}/{from_date[1]:02d}/{from_date[0]}"
                    to_str = f"{to_date[2]:02d}/{to_date[1]:02d}/{to_date[0]}"
                else:
                    from_str = f"JD{current_jd:.1f}"
                    to_str = f"JD{jd_end:.1f}"
            except:
                from_str = f"JD{current_jd:.1f}"
                to_str = f"JD{jd_end:.1f}"
            
            # Use attribute names based on level number (lvl1, lvl2, lvl3, etc.)
            lvl_name = f"lvl{level}"
            result += f"{indent}{lvl_name}: {lord} - {duration:.4f} years ({from_str} to {to_str})\n"
            
            # If current level is less than current_lvl, recurse to print next level's periods
            if level < current_lvl:
                result += recurse_periods(current_jd, level + 1, duration, lords, indent + "  ")
            
            current_jd = jd_end
        
        return result
    
    # Start recursion at level 1
    table_content = recurse_periods(start_jd_ut, 1, years[start_lord], lord_seq)
    
    return header + table_content


def connect_signals_vimsottari(signal_manager):
    """update vimsottari when positions of luminaries change"""
    signal_manager._connect("luminaries_changed", calculate_vimsottari)
