#!/usr/bin/env python3
"""
Test module for vimsottari period calculations
"""
import unittest
import sys
import os
from unittest.mock import Mock

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Mock the dependencies that are not essential for testing the core logic
sys.modules["swisseph"] = Mock()
sys.modules["gi"] = Mock()
sys.modules["gi.repository"] = Mock()
sys.modules["gi.repository.Gtk"] = Mock()
sys.modules["ui.mainpanes.panechart.chartcircles"] = Mock()
sys.modules["ui.mainpanes.panechart.chartcircles"].NAKSATRAS27 = {
    1: ("ke", "test_nakshatra")
}

# Import the module under test after mocking
from sweph.calculations.vimsottari import get_vimsottari_periods


class TestVimsottariPeriods(unittest.TestCase):
    """Test vimsottari period calculations"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Mock notify object
        self.mock_notify = Mock()
        self.mock_notify.info = Mock()
        
    def test_level_0_period_calculations(self):
        """Test that level 0 periods are calculated correctly"""
        # Test parameters
        start_jd_ut = 2460000.0  # Arbitrary julian day
        start_lord = "ke"  # Ketu - 7 years
        start_frac = 0.3  # 30% already elapsed
        levels = 2  # Only test main level and one sublevel
        
        result = get_vimsottari_periods(
            self.mock_notify, start_jd_ut, start_lord, start_frac, levels
        )
        
        # Verify we got 9 periods (one for each lord)
        self.assertEqual(len(result), 9)
        
        # Expected dasha years for reference
        dasa_years = {
            "ke": 7, "ve": 20, "su": 6, "mo": 10, "ma": 7,
            "ra": 18, "ju": 16, "sa": 19, "me": 17,
        }
        
        # Test first period (Ketu) - should be truncated
        first_period = result[0]
        self.assertEqual(first_period["lord"], "ke")
        expected_first_duration = 7 * (1 - 0.3)  # 7 * 0.7 = 4.9 years
        self.assertAlmostEqual(first_period["years"], expected_first_duration, places=3)
        
        # Test second period (Venus) - should be full length
        # This is where the current bug would manifest
        second_period = result[1]
        self.assertEqual(second_period["lord"], "ve")
        # With the current bug, this would be: 7 * 20 / 120 = 1.167 years
        # With the fix, this should be: 20 years (full length)
        expected_second_duration = 20.0  # Full Venus period
        
        # This assertion will fail with the current buggy code
        # and should pass after the fix
        self.assertAlmostEqual(second_period["years"], expected_second_duration, places=3)
        
    def test_level_0_all_periods_full_length_except_first(self):
        """Test that all level 0 periods except first use full dasha lengths"""
        start_jd_ut = 2460000.0
        start_lord = "ke"
        start_frac = 0.4  # 40% elapsed
        levels = 1  # Only main level
        
        result = get_vimsottari_periods(
            self.mock_notify, start_jd_ut, start_lord, start_frac, levels
        )
        
        dasa_years = {
            "ke": 7, "ve": 20, "su": 6, "mo": 10, "ma": 7,
            "ra": 18, "ju": 16, "sa": 19, "me": 17,
        }
        
        # Check all periods
        for i, period in enumerate(result):
            if i == 0:
                # First period should be truncated
                expected_duration = dasa_years[period["lord"]] * (1 - start_frac)
            else:
                # All other periods should be full length
                expected_duration = float(dasa_years[period["lord"]])
            
            self.assertAlmostEqual(
                period["years"], expected_duration, places=3,
                msg=f"Period {i} ({period['lord']}) has incorrect duration"
            )
    
    def test_level_1_periods_use_proportional_scaling(self):
        """Test that level 1+ periods still use proportional scaling"""
        start_jd_ut = 2460000.0
        start_lord = "ke"
        start_frac = 0.0  # No fraction for simplicity
        levels = 2  # Test subperiods
        
        result = get_vimsottari_periods(
            self.mock_notify, start_jd_ut, start_lord, start_frac, levels
        )
        
        # Check that subperiods exist and are scaled
        first_period = result[0]
        self.assertIn("sub", first_period)
        sub_periods = first_period["sub"]
        self.assertEqual(len(sub_periods), 9)
        
        # For level 1, periods should be proportional to the parent period
        # Parent Ketu period is 7 years, so subperiods should be scaled accordingly
        parent_duration = 7.0
        
        for sub_period in sub_periods:
            # Each sub-period should be: parent_duration * dasa_years[lord] / 120
            dasa_years = {
                "ke": 7, "ve": 20, "su": 6, "mo": 10, "ma": 7,
                "ra": 18, "ju": 16, "sa": 19, "me": 17,
            }
            expected_duration = parent_duration * dasa_years[sub_period["lord"]] / 120
            self.assertAlmostEqual(
                sub_period["years"], expected_duration, places=3,
                msg=f"Sub-period {sub_period['lord']} has incorrect proportional scaling"
            )


if __name__ == "__main__":
    unittest.main()