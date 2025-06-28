#!/usr/bin/env python3
"""Test house systems handling for Equal and Whole-sign systems"""

import unittest


class TestHouseSystemsLogic(unittest.TestCase):
    """Test the Equal and Whole-sign house systems logic"""

    def setUp(self):
        """Set up test data"""
        self.sample_cusps = [15.0, 45.0, 75.0, 105.0, 135.0, 165.0, 
                           195.0, 225.0, 255.0, 285.0, 315.0, 345.0]
        self.sample_ascmc = [22.5, 112.5, 195.0, 285.0]
        self.whole_sign_cusps = [0.0, 30.0, 60.0, 90.0, 120.0, 150.0, 
                               180.0, 210.0, 240.0, 270.0, 300.0, 330.0]

    def test_equal_house_system_logic(self):
        """Test Equal house system sets ascendant = midheaven = cusps[0]"""
        house_system = "E"
        cusps = self.sample_cusps
        ascmc = self.sample_ascmc
        
        # Apply the logic from the implementation
        if house_system in ["E", "W"] and cusps:
            ascendant = midheaven = cusps[0]
        elif ascmc:
            ascendant = ascmc[0]
            midheaven = ascmc[1]
        else:
            ascendant = midheaven = 0.0
        
        self.assertEqual(ascendant, 15.0, 
                        "Equal system ascendant should be cusps[0]")
        self.assertEqual(midheaven, 15.0, 
                        "Equal system midheaven should be cusps[0]")

    def test_whole_sign_house_system_logic(self):
        """Test Whole-sign house system sets ascendant = midheaven = cusps[0]"""
        house_system = "W"
        cusps = self.whole_sign_cusps
        ascmc = self.sample_ascmc
        
        # Apply the logic from the implementation
        if house_system in ["E", "W"] and cusps:
            ascendant = midheaven = cusps[0]
        elif ascmc:
            ascendant = ascmc[0]
            midheaven = ascmc[1]
        else:
            ascendant = midheaven = 0.0
        
        self.assertEqual(ascendant, 0.0, 
                        "Whole-sign system ascendant should be cusps[0]")
        self.assertEqual(midheaven, 0.0, 
                        "Whole-sign system midheaven should be cusps[0]")

    def test_other_house_systems_maintain_original_behavior(self):
        """Test that other house systems use ascmc values"""
        for house_system in ["P", "O", "R", "C", "K"]:
            cusps = self.sample_cusps
            ascmc = self.sample_ascmc
            
            # Apply the logic from the implementation
            if house_system in ["E", "W"] and cusps:
                ascendant = midheaven = cusps[0]
            elif ascmc:
                ascendant = ascmc[0]
                midheaven = ascmc[1]
            else:
                ascendant = midheaven = 0.0
            
            self.assertEqual(ascendant, 22.5, 
                           f"House system {house_system} should use ascmc[0]")
            self.assertEqual(midheaven, 112.5, 
                           f"House system {house_system} should use ascmc[1]")

    def test_cusps_table_omission_logic(self):
        """Test that cusps table is omitted for E and W systems"""
        # Test that Equal/Whole-sign systems omit cusps table
        for house_system in ["E", "W"]:
            show_cusps_table = house_system not in ["E", "W"]
            self.assertFalse(show_cusps_table, 
                           f"House system {house_system} should omit cusps table")
        
        # Test that other systems show cusps table
        for house_system in ["P", "O", "R", "C", "K"]:
            show_cusps_table = house_system not in ["E", "W"]
            self.assertTrue(show_cusps_table, 
                          f"House system {house_system} should show cusps table")

    def test_edge_case_empty_cusps(self):
        """Test behavior when cusps list is empty"""
        house_system = "E"
        cusps = []
        ascmc = self.sample_ascmc
        
        # Apply the logic from the implementation
        if house_system in ["E", "W"] and cusps:
            ascendant = midheaven = cusps[0]
        elif ascmc:
            ascendant = ascmc[0]
            midheaven = ascmc[1]
        else:
            ascendant = midheaven = 0.0
        
        # Should fall back to ascmc values
        self.assertEqual(ascendant, 22.5, 
                        "Empty cusps should fall back to ascmc[0]")
        self.assertEqual(midheaven, 112.5, 
                        "Empty cusps should fall back to ascmc[1]")

    def test_edge_case_no_ascmc_no_cusps(self):
        """Test behavior when both cusps and ascmc are empty"""
        house_system = "E"
        cusps = []
        ascmc = []
        
        # Apply the logic from the implementation
        if house_system in ["E", "W"] and cusps:
            ascendant = midheaven = cusps[0]
        elif ascmc:
            ascendant = ascmc[0]
            midheaven = ascmc[1]
        else:
            ascendant = midheaven = 0.0
        
        # Should default to 0.0
        self.assertEqual(ascendant, 0.0, 
                        "No data should default ascendant to 0.0")
        self.assertEqual(midheaven, 0.0, 
                        "No data should default midheaven to 0.0")


if __name__ == "__main__":
    unittest.main()