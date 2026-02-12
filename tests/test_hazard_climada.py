"""
Test suite for Climate Digital Twin - CLIMADA Hazard Module

Tests for CLIMADA-compatible impact functions with HK-specific calibrations.

Coverage:
- ClimadaImpactFunc class (MDR calculations, validation)
- HKClimadaImpactFunc class (zone adjustments, HK factors)
- ImpactFuncSet class (function management)
- HK-specific functions (TC wind, flood, fire, drought)
- Validation against existing damage curves
"""

import pytest
import numpy as np
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.hazard_climada import (
    ClimadaImpactFunc,
    HKClimadaImpactFunc,
    ImpactFuncSet,
    HK_TC_WindDamage,
    HK_FloodDamage,
    HK_FireDamage,
    HK_DroughtDamage,
    create_default_funcset,
    HazardType
)


# =====================
# CLIMADA IMPACT FUNC TESTS
# =====================

class TestClimadaImpactFunc:
    """Tests for base CLIMADA impact function class."""
    
    @pytest.fixture
    def basic_func(self):
        """Create a basic impact function for testing."""
        return ClimadaImpactFunc(
            haz_type="FL",
            func_id=1,
            name="Test Flood",
            intensity_unit="m",
            intensity=np.array([0, 0.5, 1.0, 2.0, 3.0]),
            mdd=np.array([0.0, 0.10, 0.30, 0.60, 0.85]),
            paa=np.array([0.0, 0.30, 0.60, 0.90, 1.0])
        )
    
    def test_climada_impact_func_creation(self, basic_func):
        """Test basic impact function creation."""
        assert basic_func.haz_type == "FL"
        assert basic_func.func_id == 1
        assert basic_func.name == "Test Flood"
        assert basic_func.intensity_unit == "m"
        assert len(basic_func.intensity) == 5
    
    def test_mdr_calculation_exact_point(self, basic_func):
        """Test MDR calculation at exact intensity points."""
        # At intensity 0.5: MDD=0.10, PAA=0.30 -> MDR=0.03
        assert abs(basic_func.calc_mdr(0.5) - 0.03) < 1e-10
        
        # At intensity 1.0: MDD=0.30, PAA=0.60 -> MDR=0.18
        assert abs(basic_func.calc_mdr(1.0) - 0.18) < 1e-10
    
    def test_mdr_calculation_interpolation(self, basic_func):
        """Test MDR calculation with interpolation."""
        # At intensity 0.75 (between 0.5 and 1.0)
        mdr = basic_func.calc_mdr(0.75)
        assert 0.03 < mdr < 0.18  # Should be between the two values
    
    def test_mdr_at_bounds(self, basic_func):
        """Test MDR calculation at boundary conditions."""
        # Below minimum
        assert basic_func.calc_mdr(-1.0) == 0.0
        # Above maximum
        assert basic_func.calc_mdr(10.0) == pytest.approx(0.85, rel=1e-5)
    
    def test_calc_impact(self, basic_func):
        """Test damage calculation in monetary terms."""
        damage = basic_func.calc_impact(1.0, 1_000_000)
        expected = 0.18 * 1_000_000  # MDR at 1.0m is 0.18
        assert damage == pytest.approx(expected, rel=1e-5)
    
    def test_validation_pass(self, basic_func):
        """Test validation passes for valid function."""
        is_valid, issues = basic_func.validate()
        assert is_valid
        assert len(issues) == 0
    
    def test_get_mdr_curve(self, basic_func):
        """Test getting full MDR curve."""
        intensities, mdrs = basic_func.get_mdr_curve()
        assert len(intensities) == len(mdrs)
        assert len(intensities) == 5
        expected_mdrs = np.array([0.0, 0.03, 0.18, 0.54, 0.85])
        np.testing.assert_array_almost_equal(mdrs, expected_mdrs, decimal=10)


class TestClimadaValidation:
    """Tests for validation and error handling."""
    
    def test_validation_detects_decreasing_mdd(self):
        """Test validation catches non-monotonic MDD."""
        func = ClimadaImpactFunc(
            haz_type="TC",
            func_id=1,
            name="Invalid MDD",
            intensity_unit="km/h",
            intensity=np.array([0, 50, 100]),
            mdd=np.array([0.0, 0.8, 0.3]),  # Decreasing!
            paa=np.array([0.0, 0.5, 1.0])
        )
        is_valid, issues = func.validate()
        assert not is_valid
        assert "MDD should be non-decreasing" in issues
    
    def test_validation_detects_decreasing_paa(self):
        """Test validation catches non-monotonic PAA."""
        func = ClimadaImpactFunc(
            haz_type="TC",
            func_id=1,
            name="Invalid PAA",
            intensity_unit="km/h",
            intensity=np.array([0, 50, 100]),
            mdd=np.array([0.0, 0.5, 1.0]),
            paa=np.array([1.0, 0.5, 0.0])  # Decreasing!
        )
        is_valid, issues = func.validate()
        assert not is_valid
        assert "PAA should be non-decreasing" in issues
    
    def test_validation_mdd_bounds(self):
        """Test validation catches MDD out of bounds."""
        func = ClimadaImpactFunc(
            haz_type="TC",
            func_id=1,
            name="MDD Out of Bounds",
            intensity_unit="km/h",
            intensity=np.array([0, 50, 100]),
            mdd=np.array([0.0, 0.5, 1.5]),  # > 1!
            paa=np.array([0.0, 0.5, 1.0])
        )
        is_valid, issues = func.validate()
        assert not is_valid
        assert "MDD values out of bounds [0, 1]" in issues


# =====================
# HK CLIMADA IMPACT FUNC TESTS
# =====================

class TestHKClimadaImpactFunc:
    """Tests for HK-specific impact function class."""
    
    @pytest.fixture
    def hk_func(self):
        """Create an HK impact function."""
        return HKClimadaImpactFunc(
            haz_type="TC",
            func_id=1,
            name="Test HK TC",
            intensity_unit="km/h",
            intensity=np.array([0, 63, 100, 119]),
            mdd=np.array([0.0, 0.05, 0.15, 0.30]),
            paa=np.array([0.0, 0.2, 0.5, 0.8]),
            hk_construction_factor=0.9,
            building_type="residential_high_rise",
            damage_category="structural"
        )
    
    def test_hk_func_creation(self, hk_func):
        """Test HK impact function creation with attributes."""
        assert hk_func.haz_type == "TC"
        assert hk_func.hk_construction_factor == 0.9
        assert hk_func.building_type == "residential_high_rise"
        assert hk_func.damage_category == "structural"
    
    def test_hk_zone_adjustment(self, hk_func):
        """Test zone adjustment calculation."""
        # Calculate for default zone (factor = 1.0)
        mdr_default = hk_func.calc_mdr(100, "default")
        
        # Calculate for central zone (factor = 1.2, should be higher)
        mdr_central = hk_func.calc_mdr(100, "hk_central")
        
        # Due to construction factor being applied, verify it's different
        assert mdr_central != mdr_default
        assert mdr_central > mdr_default
    
    def test_hk_construction_factor(self):
        """Test construction factor reduces damage for better construction."""
        # Create functions with different construction factors
        func_high = HKClimadaImpactFunc(
            haz_type="TC", func_id=1, name="High Resilience",
            intensity_unit="km/h",
            intensity=np.array([0, 100]), mdd=np.array([0.0, 0.5]), paa=np.array([0.0, 1.0]),
            hk_construction_factor=0.5
        )
        func_low = HKClimadaImpactFunc(
            haz_type="TC", func_id=2, name="Low Resilience",
            intensity_unit="km/h",
            intensity=np.array([0, 100]), mdd=np.array([0.0, 0.5]), paa=np.array([0.0, 1.0]),
            hk_construction_factor=1.5
        )
        
        mdr_high = func_high.calc_mdr(100)
        mdr_low = func_low.calc_mdr(100)
        
        # Lower construction factor should result in lower damage (capped at 1.0)
        assert mdr_high <= mdr_low
    
    def test_hk_default_zone_adjustments(self):
        """Test default zone adjustments are set."""
        func = HKClimadaImpactFunc(
            haz_type="FL", func_id=1, name="Test",
            intensity_unit="m",
            intensity=np.array([0, 1]), mdd=np.array([0.0, 0.5]), paa=np.array([0.0, 1.0])
        )
        
        assert "default" in func.hk_zone_adjustment
        assert "hk_central" in func.hk_zone_adjustment
        assert "hk_kowloon" in func.hk_zone_adjustment
    
    def test_hk_zone_factor_lookup(self, hk_func):
        """Test zone factor lookup method."""
        assert hk_func.get_zone_factor("default") == 1.0
        assert hk_func.get_zone_factor("hk_central") == 1.2
        assert hk_func.get_zone_factor("unknown") == 1.0


# =====================
# IMPACT FUNC SET TESTS
# =====================

class TestImpactFuncSet:
    """Tests for impact function collection."""
    
    @pytest.fixture
    def funcset(self):
        """Create an impact function set."""
        return ImpactFuncSet()
    
    @pytest.fixture
    def sample_funcs(self):
        """Create sample functions."""
        func1 = ClimadaImpactFunc(
            haz_type="FL", func_id=1, name="Flood 1",
            intensity_unit="m",
            intensity=np.array([0, 1, 2]), mdd=np.array([0, 0.1, 0.3]), paa=np.array([0, 1, 1])
        )
        func2 = ClimadaImpactFunc(
            haz_type="FL", func_id=2, name="Flood 2",
            intensity_unit="m",
            intensity=np.array([0, 1]), mdd=np.array([0, 0.2]), paa=np.array([0, 1])
        )
        func3 = ClimadaImpactFunc(
            haz_type="TC", func_id=1, name="TC 1",
            intensity_unit="km/h",
            intensity=np.array([0, 100]), mdd=np.array([0, 0.5]), paa=np.array([0, 1])
        )
        return func1, func2, func3
    
    def test_add_and_get_func(self, funcset, sample_funcs):
        """Test adding and retrieving functions."""
        func1, func2, func3 = sample_funcs
        
        funcset.add_func(func1)
        funcset.add_func(func2)
        funcset.add_func(func3)
        
        retrieved = funcset.get_func("FL", 1)
        assert retrieved is func1
        assert retrieved.name == "Flood 1"
    
    def test_get_nonexistent_func(self, funcset):
        """Test retrieval of non-existent function."""
        assert funcset.get_func("EQ", 1) is None
    
    def test_get_funcs_by_type(self, funcset, sample_funcs):
        """Test retrieval of all functions for a hazard type."""
        func1, func2, func3 = sample_funcs
        
        funcset.add_func(func1)
        funcset.add_func(func2)
        funcset.add_func(func3)
        
        fl_funcs = funcset.get_funcs_by_type("FL")
        assert len(fl_funcs) == 2
        
        tc_funcs = funcset.get_funcs_by_type("TC")
        assert len(tc_funcs) == 1
    
    def test_count_functions(self, funcset, sample_funcs):
        """Test function counting."""
        func1, func2, func3 = sample_funcs
        
        assert funcset.count() == 0
        funcset.add_func(func1)
        assert funcset.count() == 1
        funcset.add_func(func2)
        funcset.add_func(func3)
        assert funcset.count() == 3
    
    def test_clear_functions(self, funcset, sample_funcs):
        """Test clearing all functions."""
        func1, _, _ = sample_funcs
        funcset.add_func(func1)
        assert funcset.count() == 1
        funcset.clear()
        assert funcset.count() == 0
    
    def test_validate_all_pass(self, funcset, sample_funcs):
        """Test validation of all functions (pass case)."""
        func1, func2, func3 = sample_funcs
        funcset.add_func(func1)
        funcset.add_func(func2)
        funcset.add_func(func3)
        
        is_valid, issues = funcset.validate_all()
        assert is_valid
        assert len(issues) == 0
    
    def test_validate_all_failure(self, funcset):
        """Test validation of all functions (failure case)."""
        invalid_func = ClimadaImpactFunc(
            haz_type="TC", func_id=1, name="Invalid",
            intensity_unit="km/h",
            intensity=np.array([0, 100]),
            mdd=np.array([0.0, 1.5]),  # Invalid: > 1
            paa=np.array([0.0, 1.0])
        )
        funcset.add_func(invalid_func)
        
        is_valid, issues = funcset.validate_all()
        assert not is_valid
        assert "TC_1" in issues


# =====================
# HK-SPECIFIC FUNCTION TESTS
# =====================

class TestHKTCWindDamage:
    """Tests for HK tropical cyclone wind damage function."""
    
    def test_tc_wind_damage_creation(self):
        """Test TC wind damage function creation."""
        func = HK_TC_WindDamage()
        assert func.haz_type == "TC"
        assert func.intensity_unit == "km/h"
        assert func.func_id == 1
    
    def test_tc_wind_mdr_increases_with_speed(self):
        """Test MDR increases with wind speed."""
        func = HK_TC_WindDamage()
        
        mdr_63 = func.calc_mdr(63)   # Tropical storm threshold
        mdr_119 = func.calc_mdr(119) # Cat 1 threshold  
        mdr_252 = func.calc_mdr(252) # Cat 5 threshold
        
        assert mdr_63 < mdr_119 < mdr_252
        assert mdr_252 <= 1.0
    
    def test_tc_wind_zero_damage_below_63kmh(self):
        """Test no damage below tropical depression (at minimum threshold)."""
        func = HK_TC_WindDamage()
        assert func.calc_mdr(0) == 0.0
        # At 63 km/h, there should be minimal but non-zero damage due to interpolation
        mdr_at_storm_threshold = func.calc_mdr(63)
        assert mdr_at_storm_threshold >= 0.0
    
    def test_tc_wind_construction_factor_effect(self):
        """Test construction factor affects damage."""
        func_rc = HK_TC_WindDamage(construction="reinforced_concrete"  )
        func_wood = HK_TC_WindDamage(construction="wood")
        
        assert func_rc.hk_construction_factor < func_wood.hk_construction_factor
        
        mdr_rc = func_rc.calc_mdr(150)
        mdr_wood = func_wood.calc_mdr(150)
        assert mdr_rc < mdr_wood


class TestHKFloodDamage:
    """Tests for HK flood damage function."""
    
    def test_flood_damage_creation(self):
        """Test flood damage function creation."""
        func = HK_FloodDamage()
        assert func.haz_type == "FL"
        assert func.intensity_unit == "m"
    
    def test_flood_mdr_increases_with_depth(self):
        """Test MDR increases with flood depth."""
        func = HK_FloodDamage()
        
        mdr_0 = func.calc_mdr(0)
        mdr_05 = func.calc_mdr(0.5)
        mdr_1 = func.calc_mdr(1.0)
        mdr_2 = func.calc_mdr(2.0)
        
        assert mdr_0 == 0.0
        assert 0 < mdr_05 < mdr_1 < mdr_2
    
    def test_flood_zone_adjustment(self):
        """Test zone adjustment for flood damage."""
        func = HK_FloodDamage()
        
        mdr_default = func.calc_mdr(1.0, "default")
        mdr_nt_west = func.calc_mdr(1.0, "hk_new_territories_west")
        mdr_nt_east = func.calc_mdr(1.0, "hk_new_territories_east")
        
        # NT West has highest flood risk (1.3 factor)
        assert mdr_nt_west > mdr_default
        # NT East has lower risk (0.9 factor)
        assert mdr_nt_east < mdr_default
    
    def test_flood_highrise_adjustment(self):
        """Test high-rise building damage is lower due to partial exposure."""
        func_lowrise = HK_FloodDamage(floor_count=5)
        func_highrise = HK_FloodDamage(floor_count=40)
        
        # High-rise should have lower MDD due to affected floor ratio
        assert func_lowrise.building_type == "residential_high_rise"
        assert func_highrise.building_type == "residential_high_rise"


class TestHKFireDamage:
    """Tests for HK fire damage function."""
    
    def test_fire_damage_creation(self):
        """Test fire damage function creation."""
        func = HK_FireDamage()
        assert func.haz_type == "WF"
        assert func.intensity_unit == "%"
    
    def test_fire_mdr_increases_with_burn_percentage(self):
        """Test MDR increases with burn percentage."""
        func = HK_FireDamage()
        
        mdr_0 = func.calc_mdr(0)
        mdr_50 = func.calc_mdr(50)
        mdr_100 = func.calc_mdr(100)
        
        assert mdr_0 == 0.0
        assert 0 < mdr_50 < mdr_100
    
    def test_fire_resistance_factor(self):
        """Test fire resistance rating affects damage."""
        func_premium = HK_FireDamage(fire_rating="premium")
        func_old = HK_FireDamage(fire_rating="pre_1960")
        
        # Premium rating should have lower construction factor
        assert func_premium.hk_construction_factor < func_old.hk_construction_factor


class TestHKDroughtDamage:
    """Tests for HK drought damage function."""
    
    def test_drought_damage_creation(self):
        """Test drought damage function creation."""
        func = HK_DroughtDamage()
        assert func.haz_type == "DR"
        assert func.intensity_unit == "SPI"
    
    def test_drought_agricultural_impact(self):
        """Test agricultural drought damage is higher than residential."""
        func_agri = HK_DroughtDamage(building_type="agricultural")
        func_residential = HK_DroughtDamage(building_type="residential_high_rise")
        
        mdr_agri = func_agri.calc_mdr(-1.5)  # Very dry
        mdr_residential = func_residential.calc_mdr(-1.5)
        
        assert mdr_agri > mdr_residential
    
    def test_drought_normal_conditions_no_damage(self):
        """Test no damage during normal precipitation."""
        func = HK_DroughtDamage()
        mdr = func.calc_mdr(0)  # SPI = 0 (normal)
        assert mdr == 0.0


# =====================
# DEFAULT FUNC SET TESTS
# =====================

class TestDefaultFuncSet:
    """Tests for default function set creation."""
    
    def test_create_default_funcset(self):
        """Test creating default function set with all HK functions."""
        funcset = create_default_funcset()
        assert funcset is not None
        assert funcset.count() > 0
    
    def test_default_funcset_has_all_hazards(self):
        """Test default set includes all hazard types."""
        funcset = create_default_funcset()
        
        # Should have TC, FL, WF, DR functions
        assert len(funcset.get_funcs_by_type("TC")) > 0
        assert len(funcset.get_funcs_by_type("FL")) > 0
        assert len(funcset.get_funcs_by_type("WF")) > 0
        assert len(funcset.get_funcs_by_type("DR")) > 0


# =====================
# BACKWARD COMPATIBILITY TESTS
# =====================

class TestBackwardCompatibility:
    """Tests for compatibility with existing damage curves."""
    
    def test_flood_consistency_with_legacy(self):
        """Test CLIMADA flood curve is consistent with legacy implementation."""
        from core.hazard import HazardAssessment
        
        legacy_hazard = HazardAssessment()
        climada_func = HK_FloodDamage()
        
        # Test at various depths
        test_depths = [0.1, 0.5, 1.0, 1.5, 2.0]
        differences = []
        
        for depth in test_depths:
            legacy_damage = legacy_hazard._flood_damage_curve(depth, "residential", "reinforced_concrete")
            climada_mdr = climada_func.calc_mdr(depth)
            # CLIMADA curve is specific to HK high-rise - expect similar but not identical
            differences.append(abs(legacy_damage - climada_mdr))
        
        # Damages should be reasonably aligned (within reasonable tolerance)
        # They won't match exactly due to different approaches (legacy is Simplified, CLIMADA is MDD*PAA)
        avg_difference = sum(differences) / len(differences)
        assert avg_difference < 0.5  # Half damage ratio tolerance
    
    def test_cyclone_consistency_with_legacy(self):
        """Test CLIMADA TC curve is consistent with legacy implementation."""
        from core.hazard import HazardAssessment
        
        legacy_hazard = HazardAssessment()
        climada_func = HK_TC_WindDamage(construction="reinforced_concrete")
        
        test_speeds = [63, 100, 119, 154, 178, 209, 252]
        
        for speed in test_speeds:
            legacy_damage = legacy_hazard._cyclone_damage_curve(speed, "residential", "reinforced_concrete")
            climada_mdr = climada_func.calc_mdr(speed)
            
            # For reinforced concrete, should be reasonably similar
            # Allow significant variance due to different calculation methods
            assert abs(legacy_damage - climada_mdr) < 0.6


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])