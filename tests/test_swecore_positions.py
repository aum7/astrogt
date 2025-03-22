# ruff: noqa: E402
import unittest
import sys
import os
from unittest.mock import patch, MagicMock, Mock
from typing import cast, Dict, Any
# import logging
# from datetime import datetime

# add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# mock issues
sys.modules["user.settings.settings"] = Mock()
sys.modules["user.settings.settings"].OBJECTS = {
    "sun": (0, ["sun"]),
    "moon": (1, ["moon"]),
    "mercury": (2, ["mercury"]),
}
sys.modules["user.settings.settings"].SWE_FLAG = {
    "swe_flag_default": 0,
    "sidereal_zodiac": False,
    "nutation": False,
    "heliocentric": False,
    "true_positions": False,
    "topocentric": False,
    "equatorial": False,
}
from sweph.swecore import SweCore
from sweph.calculations.positions import SwePositions


@patch(
    "sweph.calculations.positions.OBJECTS",
    sys.modules["user.settings.settings"].OBJECTS,
)
@patch(
    "sweph.calculations.positions.SWE_FLAG",
    sys.modules["user.settings.settings"].SWE_FLAG,
)
# logger = logging.getLogger("test_swecore_positions")
class TestSwePositionsIntegration(unittest.TestCase):
    """test the integration between SweCore and SwePositions"""

    @patch("sweph.swecore.swe.close")
    @patch("sweph.swecore.Gtk.Application.get_default")
    # def setUp(self, mock_get_default):
    def setUp(self, mock_get_default, mock_swe_close):
        """Set up test environment"""
        self.mock_app = MagicMock()
        mock_get_default.return_value = self.mock_app
        # create instances with mocked dependencies
        self.swe_core = SweCore()
        # reset class variables to ensure clean state
        SweCore.event_one_name = ""
        SweCore.event_one_country = ""
        SweCore.event_one_city = ""
        SweCore.event_one_location = ""
        SweCore.event_one_date_time = ""
        SweCore.event_two_name = ""
        SweCore.event_two_country = ""
        SweCore.event_two_city = ""
        SweCore.event_two_location = ""
        SweCore.event_two_date_time = ""

    # test 1
    @patch("sweph.calculations.positions.swe")
    def test_data_transfer_from_swecore_to_positions(
        self,
        mock_swe,
        # self, mock_calc_ut, mock_julday_ut
    ):
        """test that data is properly transferred from SweCore to SwePositions"""
        # set up mock return values
        mock_swe.julday_ut.return_value = 2460000.5
        mock_swe.calc_ut.return_value = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0]
        # set test data in swecore
        test_data = {
            "name": "TestEvent",
            "country": "Australia",
            "city": "Melbourne",
            "location": "37 47 59 s 145 00 00 e",
            "date_time": "2025-03-22 06:27:38",
        }
        # update swecore with the test data
        self.swe_core.get_events_data(event_one=test_data)
        # verify data was set in swecore
        self.assertEqual(SweCore.event_one_name, test_data["name"])
        self.assertEqual(SweCore.event_one_date_time, test_data["date_time"])
        # now create swepositions and verify it can access the data
        with patch(
            "sweph.calculations.positions.Gtk.Application.get_default",
            return_value=self.mock_app,
        ):
            positions = SwePositions()
            # verify the data transfer happened
            self.assertEqual(positions.swe_core.event_one_name, test_data["name"])
            # test swe_events_data method
            results = positions.swe_events_data()
            # verify results contain the event
            self.assertTrue(mock_swe.julday_ut.called)
            self.assertTrue(mock_swe.calc_ut.called)

    # test 2
    @patch("sweph.calculations.positions.Gtk.Application.get_default")
    def test_parse_location_format(self, mock_get_default):
        """test the location parsing function"""
        mock_get_default.return_value = self.mock_app

        positions = SwePositions()
        # test with valid location string
        location = positions._parse_location("37 47 59 s 145 00 00 e")
        self.assertIsNotNone(location)
        # inform type checker that location is not None
        location = cast(Dict[str, Any], location)
        self.assertAlmostEqual(location["lat"], -37.79972222222222, places=5)
        self.assertAlmostEqual(location["lon"], 145.0, places=5)
        # test with invalid location string
        invalid_location = positions._parse_location("invalid location")
        self.assertIsNone(invalid_location)

    # test 3
    @patch("sweph.calculations.positions.Gtk.Application.get_default")
    def test_parse_datetime_format(self, mock_get_default):
        """test the datetime parsing function"""
        mock_get_default.return_value = self.mock_app

        positions = SwePositions()
        # test with valid datetime string
        dt = positions._parse_datetime("2025-03-22 06:27:38")
        self.assertIsNotNone(dt)
        # inform type checker that dt is not None
        dt = cast(Dict[str, int], dt)
        self.assertEqual(dt["year"], 2025)
        self.assertEqual(dt["month"], 3)
        self.assertEqual(dt["day"], 22)
        self.assertEqual(dt["hour"], 6)
        self.assertEqual(dt["minute"], 27)
        self.assertEqual(dt["second"], 38)
        # test with invalid datetime string
        invalid_dt = positions._parse_datetime("invalid datetime")
        self.assertIsNone(invalid_dt)


if __name__ == "__main__":
    unittest.main()
