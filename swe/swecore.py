import os
import swisseph as swe
# from datetime import datetime
# from typing import Callable, Dict, List, Tuple, Optional
# from user.settings.settings import (
#     OBJECTS,
#     HOUSE_SYSTEMS,
#     SWE_FLAG,
#     FILES,
#     CHART_SETTINGS,
#     SOLAR_YEAR,
#     LUNAR_MONTH,
#     AYANAMSA,
#     CUSTOM_AYANAMSA,
# )


class SweCore:
    """note : swisseph calculations need be closed at the end of computations"""

    def __init__(self, get_application=None):
        # swiss ephemeris path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ephe_path = os.path.join(current_dir, "ephe")
        swe.set_ephe_path(ephe_path)
        # todo : move to end or leave it
        swe.close()
        self.get_application = get_application
        self.event_one_name = ""
        self.event_one_location = ""
        self.event_one_date_time = ""
        self.event_two_name = ""
        self.event_two_location = ""
        self.event_two_date_time = ""

    @staticmethod
    def get_events_data(window, event_one=None, event_two=None):
        """process event data using swisseph ; parent window / widget (optional)"""

        if event_one:
            print("processing event one :")
            if (
                not event_one["name"]
                or not event_one["date_time"]
                or not event_one["location"]
            ):
                window.get_application().notify_manager.warning(
                    message="event one : data missing",
                    source="swecore",
                )
                return {}
            # data received
            SweCore.event_one_name = event_one["name"]
            SweCore.event_one_date_time = event_one["date_time"]
            SweCore.event_one_location = event_one["location"]

            window.get_application().notify_manager.success(
                message=f"event one data received :\n\t{event_one['name']} : {event_one['date_time']} : {event_one['location']}",
                source="swecore",
            )
        if event_two:
            print("processing event two :")
            # for event two only datetime is mandatory
            if not event_two["date_time"]:
                window.get_application().notify_manager.warning(
                    message="event two : datetime missing",
                    source="swecore",
                    timeout=1,
                )
                return {}

            if not event_two["name"]:
                event_two["name"] = SweCore.event_one_name
            # if location not provided, use event one location
            if not event_two["location"]:
                event_two["location"] = SweCore.event_one_location
            SweCore.event_two_name = event_two["name"]
            SweCore.event_two_date_time = event_two["date_time"]
            SweCore.event_two_location = event_two["location"]

            window.get_application().notify_manager.success(
                message=f"event two data received :\n\t{event_two['name']} : {event_two['date_time']} : {event_two['location']}",
                source="swecore",
            )
            # todo test print
            window.get_application().notify_manager.debug(
                message=f"self.event_one_name : {SweCore.event_one_name}"
                f"\nself.event_one_date_time : {SweCore.event_one_date_time}"
                f"\nself.event_one_location : {SweCore.event_one_location}"
                f"\nself.event_two_name : {SweCore.event_two_name}"
                f"\nself.event_two_date_time : {SweCore.event_two_date_time}"
                f"\nself.event_two_location : {SweCore.event_two_location}",
                source="swecore",
            )

    # print(f"swecore : OBJECTS : {OBJECTS}")
    # print(f"swecore : HOUSE_SYSTEMS : {HOUSE_SYSTEMS}")
    # window.OBJECTS = OBJECTS
    # window.HOUSE_SYSTEMS = HOUSE_SYSTEMS
