"""
HK Property Values Module

Provides Hong Kong property value baselines for financial risk assessment.
Includes:
- District-level property values (HKD per sqft)
- Building type adjustments
- Floor and view premiums
- Development age adjustments

Based on HK property market data and trends.
"""

from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class HKDistrict(str, Enum):
    """Hong Kong districts."""
    CENTRAL = "central"
    ADMIRALTY = "admiralty"
    WAN_CHAI = "wan_chai"
    CAUSEWAY_BAY = "causeway_bay"
    TST = "tsim_sha_tsui"
    HUNG_HOM = "hung_hom"
    KWUN_TONG = "kwun_tong"
    SHA_TIN = "sha_tin"
    TUEN_MUN = "tuen_mun"
    YUEN_LONG = "yuen_long"
    TIN_SHUI_WAI = "tin_shui_wai"
    LANTAU = "lantau"
    CHEUNG_CHAU = "cheung_chau"


class HKBuildingType(str, Enum):
    """Property building types."""
    RESIDENTIAL_APARTMENT = "residential_apartment"
    RESIDENTIAL_TOWNHOUSE = "residential_townhouse"
    COMMERCIAL_OFFICE = "commercial_office"
    COMMERCIAL_RETAIL = "commercial_retail"
    COMMERCIAL_HOTEL = "commercial_hotel"
    INDUSTRIAL_FACTORY = "industrial_factory"
    INDUSTRIAL_WAREHOUSE = "industrial_warehouse"


@dataclass
class HKPropertyValue:
    """HK property value baseline."""
    district: str
    building_type: HKBuildingType
    base_price_hkd_sqft: float
    price_range_low: float
    price_range_high: float
    risk_level: str


class HKPropertyValues:
    """
    HK property value baseline provider for financial risk assessment.
    
    Provides district-level property values adjusted for building type,
    floor level, view, and development age.
    """
    
    # Baseline property values by district (HKD per sqft)
    BASELINE_VALUES: Dict[str, Dict[str, HKPropertyValue]] = {
        # Hong Kong Island - Core Central
        "central": {
            "residential_apartment": HKPropertyValue(
                district="central", building_type="residential_apartment",
                base_price_hkd_sqft=28000, price_range_low=22000, price_range_high=35000, risk_level="high"
            ),
            "commercial_office": HKPropertyValue(
                district="central", building_type="commercial_office",
                base_price_hkd_sqft=40000, price_range_low=30000, price_range_high=50000, risk_level="high"
            ),
            "commercial_retail": HKPropertyValue(
                district="central", building_type="commercial_retail",
                base_price_hkd_sqft=45000, price_range_low=35000, price_range_high=60000, risk_level="high"
            ),
        },
        "admiralty": {
            "residential_apartment": HKPropertyValue(
                district="admiralty", building_type="residential_apartment",
                base_price_hkd_sqft=26000, price_range_low=20000, price_range_high=32000, risk_level="high"
            ),
            "commercial_office": HKPropertyValue(
                district="admiralty", building_type="commercial_office",
                base_price_hkd_sqft=38000, price_range_low=28000, price_range_high=48000, risk_level="high"
            ),
        },
        "wan_chai": {
            "residential_apartment": HKPropertyValue(
                district="wan_chai", building_type="residential_apartment",
                base_price_hkd_sqft=24000, price_range_low=18000, price_range_high=30000, risk_level="high"
            ),
            "commercial_office": HKPropertyValue(
                district="wan_chai", building_type="commercial_office",
                base_price_hkd_sqft=35000, price_range_low=25000, price_range_high=45000, risk_level="high"
            ),
        },
        "causeway_bay": {
            "residential_apartment": HKPropertyValue(
                district="causeway_bay", building_type="residential_apartment",
                base_price_hkd_sqft=25000, price_range_low=19000, price_range_high=31000, risk_level="high"
            ),
            "commercial_retail": HKPropertyValue(
                district="causeway_bay", building_type="commercial_retail",
                base_price_hkd_sqft=42000, price_range_low=30000, price_range_high=55000, risk_level="high"
            ),
        },
        # Kowloon
        "tsim_sha_tsui": {
            "residential_apartment": HKPropertyValue(
                district="tsim_sha_tsui", building_type="residential_apartment",
                base_price_hkd_sqft=22000, price_range_low=16000, price_range_high=28000, risk_level="high"
            ),
            "commercial_office": HKPropertyValue(
                district="tsim_sha_tsui", building_type="commercial_office",
                base_price_hkd_sqft=30000, price_range_low=22000, price_range_high=40000, risk_level="high"
            ),
            "commercial_retail": HKPropertyValue(
                district="tsim_sha_tsui", building_type="commercial_retail",
                base_price_hkd_sqft=38000, price_range_low=28000, price_range_high=50000, risk_level="high"
            ),
        },
        "hung_hom": {
            "residential_apartment": HKPropertyValue(
                district="hung_hom", building_type="residential_apartment",
                base_price_hkd_sqft=18000, price_range_low=14000, price_range_high=23000, risk_level="medium"
            ),
            "commercial_hotel": HKPropertyValue(
                district="hung_hom", building_type="commercial_hotel",
                base_price_hkd_sqft=25000, price_range_low=20000, price_range_high=32000, risk_level="medium"
            ),
        },
        "kwun_tong": {
            "residential_apartment": HKPropertyValue(
                district="kwun_tong", building_type="residential_apartment",
                base_price_hkd_sqft=16000, price_range_low=12000, price_range_high=20000, risk_level="medium"
            ),
            "industrial_warehouse": HKPropertyValue(
                district="kwun_tong", building_type="industrial_warehouse",
                base_price_hkd_sqft=10000, price_range_low=7000, price_range_high=13000, risk_level="medium"
            ),
        },
        # New Territories
        "sha_tin": {
            "residential_apartment": HKPropertyValue(
                district="sha_tin", building_type="residential_apartment",
                base_price_hkd_sqft=17000, price_range_low=13000, price_range_high=22000, risk_level="medium"
            ),
        },
        "tuen_mun": {
            "residential_apartment": HKPropertyValue(
                district="tuen_mun", building_type="residential_apartment",
                base_price_hkd_sqft=14000, price_range_low=11000, price_range_high=18000, risk_level="medium"
            ),
            "industrial_factory": HKPropertyValue(
                district="tuen_mun", building_type="industrial_factory",
                base_price_hkd_sqft=9000, price_range_low=6500, price_range_high=12000, risk_level="medium"
            ),
            "industrial_warehouse": HKPropertyValue(
                district="tuen_mun", building_type="industrial_warehouse",
                base_price_hkd_sqft=8500, price_range_low=6000, price_range_high=11000, risk_level="medium"
            ),
        },
        "yuen_long": {
            "residential_apartment": HKPropertyValue(
                district="yuen_long", building_type="residential_apartment",
                base_price_hkd_sqft=13000, price_range_low=10000, price_range_high=17000, risk_level="medium"
            ),
            "industrial_warehouse": HKPropertyValue(
                district="yuen_long", building_type="industrial_warehouse",
                base_price_hkd_sqft=8000, price_range_low=5500, price_range_high=10000, risk_level="medium"
            ),
        },
        "tin_shui_wai": {
            "residential_apartment": HKPropertyValue(
                district="tin_shui_wai", building_type="residential_apartment",
                base_price_hkd_sqft=12000, price_range_low=9000, price_range_high=16000, risk_level="high"
            ),
        },
        # Islands
        "lantau": {
            "residential_apartment": HKPropertyValue(
                district="lantau", building_type="residential_apartment",
                base_price_hkd_sqft=15000, price_range_low=11000, price_range_high=20000, risk_level="medium"
            ),
        },
        "cheung_chau": {
            "residential_apartment": HKPropertyValue(
                district="cheung_chau", building_type="residential_apartment",
                base_price_hkd_sqft=12000, price_range_low=9000, price_range_high=16000, risk_level="low"
            ),
        },
    }
    
    # Floor premium factors (per floor above 10)
    FLOOR_PREMIUM = 0.015  # 1.5% per floor
    
    # View premium factors
    VIEW_PREMIUMS = {
        "sea": 0.20,      # Sea view premium
        "mountain": 0.10,  # Mountain view premium
        "city": 0.05,      # City view premium
        "park": 0.08,      # Park view premium
        "none": 0.0,        # No view premium
    }
    
    # Development age adjustment (annual depreciation)
    AGE_DEPRECIATION_RATE = 0.002  # 0.2% per year
    
    def __init__(self):
        """Initialize HK property values module."""
        pass
    
    def get_baseline_value(
        self,
        district: str,
        building_type: str
    ) -> Optional[HKPropertyValue]:
        """Get baseline property value for district and building type."""
        district_data = self.BASELINE_VALUES.get(district.lower())
        if district_data:
            return district_data.get(building_type.lower())
        return None
    
    def calculate_property_value(
        self,
        district: str,
        building_type: str,
        area_sqft: float,
        floor: int = 10,
        view: str = "city",
        building_age_years: int = 10,
    ) -> Dict:
        """
        Calculate adjusted property value.
        
        Args:
            district: Property district
            building_type: Type of building
            area_sqft: Property area in sqft
            floor: Floor number
            view: View type
            building_age_years: Age of building in years
            
        Returns:
            Dictionary with property value breakdown
        """
        baseline = self.get_baseline_value(district, building_type)
        if not baseline:
            return {"error": f"Unknown district or building type: {district}, {building_type}"}
        
        base_price = baseline.base_price_hkd_sqft
        
        # Floor premium (floors 11+)
        floor_premium = 1.0
        if floor > 10:
            floor_premium += (floor - 10) * self.FLOOR_PREMIUM
        
        # View premium
        view_premium = 1.0 + self.VIEW_PREMIUMS.get(view, 0.0)
        
        # Age depreciation
        age_factor = max(0.7, 1.0 - (building_age_years * self.AGE_DEPRECIATION_RATE))
        
        # Calculate final price per sqft
        final_price_sqft = base_price * floor_premium * view_premium * age_factor
        
        # Calculate total value
        total_value = final_price_sqft * area_sqft
        
        return {
            "district": district,
            "building_type": building_type,
            "area_sqft": area_sqft,
            "floor": floor,
            "view": view,
            "building_age_years": building_age_years,
            "base_price_sqft_hkd": base_price,
            "floor_premium_factor": floor_premium,
            "view_premium_factor": view_premium,
            "age_depreciation_factor": age_factor,
            "final_price_sqft_hkd": round(final_price_sqft, 0),
            "total_value_hkd": round(total_value, 0),
            "price_range_low_hkd": baseline.price_range_low * area_sqft * age_factor,
            "price_range_high_hkd": baseline.price_range_high * area_sqft * age_factor,
        }
    
    def get_district_list(self) -> list:
        """Get list of available districts."""
        return list(self.BASELINE_VALUES.keys())
    
    def get_building_types_for_district(self, district: str) -> list:
        """Get available building types for a district."""
        district_data = self.BASELINE_VALUES.get(district.lower())
        if district_data:
            return list(district_data.keys())
        return []
