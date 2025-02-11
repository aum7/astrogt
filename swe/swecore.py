# from typing import Callable
# "EventData": Callable
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
    """swisseph calculations need be closed at the end of computations"""

    # EVENT_ONE: Callable
    # EVENT_TWO: Callable

    def __init__(self):
        # print(f"swecore : OBJECTS : {OBJECTS}")
        print(f"swecore : HOUSE_SYSTEMS : {HOUSE_SYSTEMS}")
        self.OBJECTS = OBJECTS
        self.HOUSE_SYSTEMS = HOUSE_SYSTEMS

    def get_events_data(self, event_one, event_two):
        # def get_events_data(self, event_one: "EventData", event_two: "EventData"):
        self.EVENT_ONE = event_one
        self.EVENT_TWO = event_two
        print(f"swecore : get_events_data : EVENT_ONE: {self.EVENT_ONE}")
        print(f"swecore : get_events_data : EVENT_TWO: {self.EVENT_TWO}")
