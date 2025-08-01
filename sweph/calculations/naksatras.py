# sweph/calculations/naksatras.py
# simplified calculaton format : data stored in positions
# ruff : noqa : E402
# import gi

# gi.require_version("Gtk", "4.0")
# from gi.repository import Gtk  # type: ignore
from sweph.constants import NAKSATRAS27, MANSIONS28


def calculate_naksatra(lon: float, use_28_nak: bool = False):
    # calculate naksatras of planets
    if use_28_nak:
        naksatras = MANSIONS28
        span = 360 / 28
        nak_num = 28
    else:
        naksatras = NAKSATRAS27
        span = 360 / 27
        nak_num = 27
    idx = int(lon // span) + 1
    if idx > nak_num:
        idx = nak_num
    ruler, name = naksatras.get(idx, ("", ""))
    return idx, name, ruler
    # app = Gtk.Application.get_default()
    # notify = app.notify_manager
    # msg = f"event {event}\n"
    # # event 1 is mandatory
    # use_28_nak = app.chart_settings["28 naksatras"]
    # if event == "e1":
    #     if not app.e1_sweph.get("jd_ut"):
    #         notify.error(
    #             "missing event 1 data : exiting ...",
    #             source="p3",
    #             route=[""],
    #         )
    #         return
    # if event == "e2":
    #     # gather data
    #     e2_pos = getattr(app, "e1_positions", {})
    #     if not e2_pos.get("jd_ut"):
    #         notify.error(
    #             "missing event 2 data : exiting ...",
    #             source="p3",
    #             route=[""],
    #         )
    #         return
    #     if e2_pos:
    #         for key, value in e2_pos.items():
    #             if not isinstance(value, dict) or "lon" not in value:
    #                 continue
    #             print(f"e2pos : {e2_pos}")
    #             # name=
    #             e2_mo = next(
    #                 (
    #                     v["lon"]
    #                     for v in e2_pos.values()
    #                     if isinstance(v, dict) and v.get("name") == "mo"
    #                 ),
    #                 None,
    #             )

    # # emit signal
    # app.signal_manager._emit("p3_changed", event)
    # notify.debug(
    #     msg,
    #     source="p3",
    #     route=[""],
    # )
