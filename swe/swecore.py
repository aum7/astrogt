import os
import swisseph as swe
from datetime import datetime
from typing import Callable, Dict, List, Tuple, Optional
from user.settings.settings import (
    OBJECTS,
    HOUSE_SYSTEMS,
    SWE_FLAG,
    FILES,
    CHART_SETTINGS,
    SOLAR_YEAR,
    LUNAR_MONTH,
    AYANAMSA,
    CUSTOM_AYANAMSA,
)


class SweCore:
    """note : swisseph calculations need be closed at the end of computations"""

    # EVENT_ONE: Callable
    # EVENT_TWO: Callable

    def __init__(self):
        # swiss ephemeris path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ephe_path = os.path.join(current_dir, "ephe")
        swe.set_ephe_path(ephe_path)
        # todo : move to end
        swe.close()

    # print(f"swecore : OBJECTS : {OBJECTS}")
    # print(f"swecore : HOUSE_SYSTEMS : {HOUSE_SYSTEMS}")
    # self.OBJECTS = OBJECTS
    # self.HOUSE_SYSTEMS = HOUSE_SYSTEMS

    @staticmethod
    def get_events_data(parent=None, event_one=None, event_two=None):
        """process event data using swisseph
        args :
            parent : parent window / widget (optional)
            event_one : dictionary of event one
            event_two : dictionary of event two
        """
        if event_one:
            print("processing event one :")
            if event_one.get("name") == "":
                print("event_one : name missing")
            if not event_one.get("name"):
                print("event_one not name")
            print(f"name : {event_one.get('name')}")
            print(f"datetime : {event_one.get('date_time')}")
            print(f"location : {event_one.get('location')}")

        if event_two:
            print("processing event two :")
            print(f"name : {event_two.get('name')}")
            print(f"datetime : {event_two.get('date_time')}")
            print(f"location : {event_two.get('location')}")
