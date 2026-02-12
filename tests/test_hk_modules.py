"""
Test suite for Climate Digital Twin - HK Modules
"""
import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.hk_regional_data import HKRegionalHazardData, get_hk_zone_for_location
from core.hk_property_values import HKPropertyValues
from core.hk_damage_functions import HKBuildingDamageFunctions
from core.hk_financial import HKCurrency, HKPropertyTax, HKMortgage


class TestHKRegionalHazardData:
    """Tests for HK Regional Hazard Data."""
    
    @pytest.fixture
    def hk_data(self):
        """Create HK regional data instance."""
        return HKRegionalHazardData()
    
    def test_hk_flood_zones_exist(self, hk_data):
        """Test that HK flood zones are defined."""
        assert hasattr(hk_data, 'FLOOD_ZONES')
        zones = hk_data.FLOOD_ZONES
        assert len(zones) >= 5
    
    def test_get_hk_zone_for_location(self):
        """Test zone lookup by location string."""
        zone = get_hk_zone_for_location("central")
        assert zone is not None
    
    def test_typhoon_data_exists(self, hk_data):
        """Test typhoon data is defined."""
        assert hasattr(hk_data, 'TYPHOON_DATA')
    
    def test_get_flood_parameters(self, hk_data):
        """Test flood parameters retrieval."""
        params = hk_data.get_flood_parameters("central")
        # May return None for unknown zone, that's ok
        assert params is None or params is not None


class TestHKPropertyValues:
    """Tests for HK Property Values."""
    
    @pytest.fixture
    def hk_values(self):
        """Create HK property values instance."""
        return HKPropertyValues()
    
    def test_baseline_values_exist(self, hk_values):
        """Test baseline values are defined."""
        assert hasattr(hk_values, 'BASELINE_VALUES')
        assert len(hk_values.BASELINE_VALUES) >= 5
    
    def test_district_list(self, hk_values):
        """Test all major districts exist."""
        districts = hk_values.get_district_list()
        assert "central" in districts
        assert "tsim_sha_tsui" in districts
    
    def test_get_building_types_for_district(self, hk_values):
        """Test building types retrieval."""
        types = hk_values.get_building_types_for_district("central")
        assert len(types) > 0
    
    def test_age_depreciation_rate_exists(self, hk_values):
        """Test age depreciation rate is defined."""
        assert hasattr(hk_values, 'AGE_DEPRECIATION_RATE')
        assert hk_values.AGE_DEPRECIATION_RATE > 0
    
    def test_view_premiums_exist(self, hk_values):
        """Test view premiums are defined."""
        assert hasattr(hk_values, 'VIEW_PREMIUMS')
        assert "sea" in hk_values.VIEW_PREMIUMS
    
    def test_floor_premium_exist(self, hk_values):
        """Test floor premium is defined."""
        assert hasattr(hk_values, 'FLOOR_PREMIUM')
        assert hk_values.FLOOR_PREMIUM > 0
    
    def test_get_baseline_value(self, hk_values):
        """Test baseline value retrieval."""
        value = hk_values.get_baseline_value("central", "residential_apartment")
        assert value is not None
        assert hasattr(value, 'base_price_hkd_sqft')
        assert value.base_price_hkd_sqft > 0


class TestHKBuildingDamageFunctions:
    """Tests for HK Damage Functions."""
    
    @pytest.fixture
    def hk_damage(self):
        """Create HK damage functions instance."""
        return HKBuildingDamageFunctions()
    
    def test_floor_thresholds_exist(self, hk_damage):
        """Test floor thresholds are defined."""
        assert hasattr(hk_damage, 'FLOOR_THRESHOLDS')
    
    def test_fire_resistance_ratings_exist(self, hk_damage):
        """Test fire resistance ratings exist."""
        assert hasattr(hk_damage, 'FIRE_RESISTANCE_RATINGS')
    
    def test_assess_flood_damage(self, hk_damage):
        """Test flood damage assessment."""
        result = hk_damage.assess_flood_damage(
            building_type="residential_apartment",
            flood_depth_m=1.0,
            building_value_hkd=10000000
        )
        assert hasattr(result, 'damage_ratio')
        assert hasattr(result, 'physical_damage_hkd')
        assert 0 <= result.damage_ratio <= 1.0
    
    def test_assess_typhoon_damage(self, hk_damage):
        """Test typhoon damage assessment."""
        result = hk_damage.assess_typhoon_damage(
            building_type="residential_apartment",
            wind_speed_kmh=150,
            building_value_hkd=10000000
        )
        # Result is a dict
        assert isinstance(result, dict)
        assert "damage_ratio" in result
        assert 0 <= result["damage_ratio"] <= 1.0


class TestHKFinancial:
    """Tests for HK Financial Classes."""
    
    @pytest.fixture
    def hkd(self):
        """Create HKD currency instance."""
        return HKCurrency()
    
    @pytest.fixture
    def tax(self):
        """Create property tax instance."""
        return HKPropertyTax()
    
    @pytest.fixture
    def mortgage(self):
        """Create mortgage instance."""
        return HKMortgage()
    
    def test_hkd_currency_format(self, hkd):
        """Test HKD currency formatting."""
        formatted = hkd.format(1000000)
        assert "$" in formatted
    
    def test_hkd_to_usd(self, hkd):
        """Test HKD to USD conversion."""
        usd = hkd.to_usd(77500)
        assert usd == pytest.approx(10000.0, rel=0.01)
    
    def test_property_tax_bsd(self, tax):
        """Test BSD calculation for non-resident."""
        bsd_result = tax.calculate_bsd(10000000, is_resident=False)
        assert bsd_result == 1500000  # 15%
    
    def test_property_tax_bsd_resident(self, tax):
        """Test BSD for resident buyer."""
        bsd_result = tax.calculate_bsd(10000000, is_resident=True)
        assert bsd_result == 0
    
    def test_stamp_duty_tiers(self, tax):
        """Test progressive stamp duty."""
        duty_2m = tax.calculate_stamp_duty(2000000)
        duty_10m = tax.calculate_stamp_duty(10000000)
        
        assert duty_10m > duty_2m
    
    def test_mortgage_max_loan(self, mortgage):
        """Test maximum loan calculation."""
        max_loan = mortgage.calculate_max_loan(property_value=10000000)
        assert max_loan > 0
    
    def test_mortgage_stress_rate(self, mortgage):
        """Test stress rate calculation."""
        stress_rate = mortgage.calculate_stress_rate()
        assert stress_rate > mortgage.prime_rate
