# ruff: noqa: E402
import swisseph as swe


def swetime_to_jd(year, month, day, hour=0, min=0, sec=0, calendar=b"g"):
    """convert swe-time to julian date"""
    decimal_hour = hour + min / 60 + sec / 3600
    is_valid, jd, dt_corr = swe.date_conversion(
        year, month, day, decimal_hour, calendar
    )
    return is_valid, jd, dt_corr
    # auto-detect calendar if not explicitly specified
    # if autoselect and calendar not in (b"g", b"j"):
    #     # julian to gregorian calendar
    #     if year > 1582 or (
    #         year == 1582 and (month > 10 or (month == 10 and day >= 15))
    #     ):
    #         calendar = b"g"
    #     else:
    #         calendar = b"j"
    # decimal hour


def jd_to_swetime(jd, calendar=b"g"):
    """convert julian day to tuple"""
    y, m, d, h = swe.revjul(jd, calendar)
    hour = int(h)
    min = int((h - hour) * 60)
    sec = int(round((((h - hour) * 60) - min) * 60))
    return (y, m, d, hour, min, sec)


def jd_to_iso(jd, calendar=b"g"):
    """convert julian day to iso string"""
    # convert bytes to int
    cal_int = swe.GREG_CAL if calendar == b"g" else swe.JUL_CAL
    # ensure jd is a float
    y, m, d, h = swe.revjul(jd, cal_int)
    # y, m, d, h = swe.revjul(jd, calendar)
    hour = int(h)
    min = int((h - hour) * 60)
    sec = int(round((((h - hour) * 60) - min) * 60))
    return f"{y:04d}-{m:02d}-{d:02d} {hour:02d}:{min:02d}:{sec:02d}"


# import gi
# gi.require_version("Gtk", "4.0")
# from gi.repository import Gtk, GObject  # type: ignore

# class SweTime(GObject.Object):
#     """note : swisseph calculations need be closed at the end of computations"""

#     # signals
#     __gsignals__ = {
#         "event-one-changed": (
#             GObject.SignalFlags.RUN_FIRST,
#             None,
#             (GObject.TYPE_PYOBJECT,),
#         ),
#         "event-two-changed": (
#             GObject.SignalFlags.RUN_FIRST,
#             None,
#             (GObject.TYPE_PYOBJECT,),
#         ),
#     }

#     def __init__(self, app=None):
#         super().__init__()
#         self._app = app or Gtk.Application.get_default()
#         self._notify = self._app.notify_manager
#         self._signal = self._app.signal_manager
#         # swiss ephemeris path
#         current_dir = os.path.dirname(os.path.abspath(__file__))
#         ephe_path = os.path.join(current_dir, "ephe")
#         swe.set_ephe_path(ephe_path)
#         # close swe after initialisation
#         swe.close()
