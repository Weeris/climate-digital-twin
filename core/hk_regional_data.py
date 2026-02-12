"""
Hong Kong Regional Hazard Data Module

Provides climate hazard parameters specific to Hong Kong regions including:
- Flood zones (Victoria Harbour, Kowloon, New Territories)
- Cyclone/typhoon data (Signal 3, 8, 9, 10)
- Wildfire risk areas (country parks)
- Drought data (reservoir levels, SPI index)

Based on Hong Kong Observatory data and published climate studies.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class HKHazardZone(str, Enum):
    """Enum for Hong Kong hazard zones."""
    HK_CENTRAL = "hk_central"
    HK_KOWLOON = "hk_kowloon"
    HK_NEW_TERRITORIES_WEST = "hk_new_territories_west"
    HK_NEW_TERRITORIES_EAST = "hk_new_territories_east"
    HK_ISLANDS = "hk_islands"


class HKSignalStrength(str, Enum):
    """Hong Kong Tropical Cyclone Warning Signals."""
    SIGNAL_3 = "signal_3"      # Gale or storm forcing 3-sided cones
    SIGNAL_8 = "signal_8"      # Gale or storm forcing 8-sided cones
    SIGNAL_9 = "signal_9"      # Increasing gale or storm
    SIGNAL_10 = "signal_10"    # Hurricane


@dataclass
class HKFloodParameters:
    """Flood parameters for HK regions."""
    region: str
    risk_level: str
    avg_depth_10yr_m: float
    avg_depth_50yr_m: float
    avg_depth_100yr_m: float
    avg_depth_500yr_m: float
    storm_surge_risk: bool
    storm_surge_additional_m: float
    frequency_increase_rate: float


@dataclass
class HKTyphoonParameters:
    """Typhoon parameters for Hong Kong."""
    avg_annual_typhoon_days: float
    peak_months: List[str]
    signal_3_frequency_per_year: float
    signal_8_frequency_per_year: float
    signal_10_frequency_per_year: float
    avg_wind_speed_signal_8_kmh: float
    avg_wind_speed_signal_10_kmh: float


@dataclass
class HKWildfireParameters:
    """Wildfire risk parameters for HK country parks."""
    park_name: str
    fire_risk_season: str  # "dry" (Oct-Mar) or "wet" (Apr-Sep)
    avg_annual_fires: float
    fire_risk_index: float  # 0-5 scale
    historically_affected: bool


@dataclass
class HKDroughtParameters:
    """Drought parameters for Hong Kong."""
    reservoir_name: str
    capacity_million_cubic_m: float
    typical_fill_rate: float  # % by end of wet season
    min_historical_level: float  # % of capacity


class HKRegionalHazardData:
    """
    Regional hazard data provider for Hong Kong.
    
    Provides baseline hazard parameters for Hong Kong regions
    based on Hong Kong Observatory data and published studies.
    """
    
    # HK Flood Zones with flood depth by return period (meters)
    FLOOD_ZONES: Dict[str, HKFloodParameters] = {
        "hk_central": HKFloodParameters(
            region="hk_central",
            risk_level="high",
            avg_depth_10yr_m=0.5,
            avg_depth_50yr_m=1.0,
            avg_depth_100yr_m=1.5,
            avg_depth_500yr_m=2.5,
            storm_surge_risk=True,
            storm_surge_additional_m=0.8,
            frequency_increase_rate=0.025
        ),
        "hk_kowloon": HKFloodParameters(
            region="hk_kowloon",
            risk_level="high",
            avg_depth_10yr_m=0.4,
            avg_depth_50yr_m=0.9,
            avg_depth_100yr_m=1.4,
            avg_depth_500yr_m=2.3,
            storm_surge_risk=True,
            storm_surge_additional_m=0.7,
            frequency_increase_rate=0.025
        ),
        "hk_new_territories_west": HKFloodParameters(
            region="hk_new_territories_west",
            risk_level="very_high",
            avg_depth_10yr_m=0.6,
            avg_depth_50yr_m=1.2,
            avg_depth_100yr_m=1.8,
            avg_depth_500yr_m=3.0,
            storm_surge_risk=True,
            storm_surge_additional_m=1.0,
            frequency_increase_rate=0.035
        ),
        "hk_new_territories_east": HKFloodParameters(
            region="hk_new_territories_east",
            risk_level="medium",
            avg_depth_10yr_m=0.2,
            avg_depth_50yr_m=0.5,
            avg_depth_100yr_m=0.8,
            avg_depth_500yr_m=1.5,
            storm_surge_risk=False,
            storm_surge_additional_m=0.0,
            frequency_increase_rate=0.015
        ),
        "hk_islands": HKFloodParameters(
            region="hk_islands",
            risk_level="medium",
            avg_depth_10yr_m=0.3,
            avg_depth_50yr_m=0.6,
            avg_depth_100yr_m=1.0,
            avg_depth_500yr_m=2.0,
            storm_surge_risk=True,
            storm_surge_additional_m=0.9,
            frequency_increase_rate=0.020
        )
    }
    
    # Typhoon/Cyclone parameters for Hong Kong
    TYPHOON_DATA: HKTyphoonParameters = HKTyphoonParameters(
        avg_annual_typhoon_days=6.0,
        peak_months=["July", "August", "September"],
        signal_3_frequency_per_year=4.5,
        signal_8_frequency_per_year=1.8,
        signal_10_frequency_per_year=0.3,
        avg_wind_speed_signal_8_kmh=85.0,
        avg_wind_speed_signal_10_kmh=150.0
    )
    
    # Wildfire risk areas (country parks)
    WILDFIRE_AREAS: List[HKWildfireParameters] = [
        HKWildfireParameters(
            park_name="Lantau South",
            fire_risk_season="dry",
            avg_annual_fires=12.0,
            fire_risk_index=4.0,
            historically_affected=True
        ),
        HKWildfireParameters(
            park_name="Lantau North",
            fire_risk_season="dry",
            avg_annual_fires=8.0,
            fire_risk_index=3.5,
            historically_affected=True
        ),
        HKWildfireParameters(
            park_name="Sai Kung",
            fire_risk_season="dry",
            avg_annual_fires=6.0,
            fire_risk_index=3.0,
            historically_affected=False
        ),
        HKWildfireParameters(
            park_name="New Territories",
            fire_risk_season="dry",
            avg_annual_fires=15.0,
            fire_risk_index=4.2,
            historically_affected=True
        ),
        HKWildfireParameters(
            park_name="Hong Kong Island",
            fire_risk_season="dry",
            avg_annual_fires=5.0,
            fire_risk_index=2.8,
            historically_affected=False
        )
    ]
    
    # Major reservoirs
    RESERVOIRS: List[HKDroughtParameters] = [
        HKDroughtParameters(
            reservoir_name="Plover Cove",
            capacity_million_cubic_m=170.0,
            typical_fill_rate=0.85,
            min_historical_level=0.40
        ),
        HKDroughtParameters(
            reservoir_name="Shek Pik",
            capacity_million_cubic_m=24.4,
            typical_fill_rate=0.88,
            min_historical_level=0.45
        ),
        HKDroughtParameters(
            reservoir_name="Tai Lam Chung",
            capacity_million_cubic_m=70.0,
            typical_fill_rate=0.82,
            min_historical_level=0.38
        ),
        HKDroughtParameters(
            reservoir_name="High Island",
            capacity_million_cubic_m=273.0,
            typical_fill_rate=0.90,
            min_historical_level=0.50
        )
    ]
    
    # Seasonal drought patterns (SPI index by quarter)
    SEASONAL_SPI: Dict[str, float] = {
        "Q1_Jan_Mar": -0.8,    # Typically drier
        "Q2_Apr_Jun": 0.3,     # Pre-monsoon transition
        "Q3_Jul_Sep": 1.2,     # Wet season (monsoon)
        "Q4_Oct_Dec": -0.4     # Post-monsoon drying
    }
    
    def get_flood_parameters(self, zone: str) -> Optional[HKFloodParameters]:
        """
        Get flood parameters for a specific HK zone.
        
        Args:
            zone: Zone identifier (e.g., "hk_central", "hk_kowloon")
            
        Returns:
            HKFloodParameters or None if zone not found
        """
        return self.FLOOD_ZONES.get(zone)
    
    def get_typhoon_parameters(self) -> HKTyphoonParameters:
        """Get typhoon parameters for Hong Kong."""
        return self.TYPHOON_DATA
    
    def get_wildfire_areas(self) -> List[HKWildfireParameters]:
        """Get list of wildfire-prone areas in HK."""
        return self.WILDFIRE_AREAS
    
    def get_reservoirs(self) -> List[HKDroughtParameters]:
        """Get list of major reservoirs in HK."""
        return self.RESERVOIRS
    
    def get_spi_by_quarter(self, quarter: str) -> float:
        """
        Get typical SPI index by quarter.
        
        Args:
            quarter: Quarter string (e.g., "Q1_Jan_Mar")
            
        Returns:
            SPI index value
        """
        return self.SEASONAL_SPI.get(quarter, 0.0)
    
    def get_regional_flood_depth(
        self,
        zone: str,
        return_period: int,
        include_storm_surge: bool = False
    ) -> float:
        """
        Get flood depth for a zone and return period.
        
        Args:
            zone: Zone identifier
            return_period: Return period in years (10, 50, 100, 500)
            include_storm_surge: Whether to add storm surge depth
            
        Returns:
            Flood depth in meters
        """
        params = self.get_flood_parameters(zone)
        if params is None:
            return 0.0
        
        depth_key = f"avg_depth_{return_period}yr_m"
        depth = getattr(params, depth_key, params.avg_depth_100yr_m)
        
        if include_storm_surge and params.storm_surge_risk:
            depth += params.storm_surge_additional_m
        
        return depth


def get_hk_zone_for_location(location: str) -> str:
    """
    Map a location name to HK hazard zone.
    
    Args:
        location: Location name (e.g., "Central", "Tsim Sha Tsui")
        
        Zone identifier
    """
    location_map = {
        # Central HK
        "central": "hk_central",
        "wan_chai": "hk_central",
        "causeway_bay": "hk_central",
        "sheung_wan": "hk_central",
        
        # Kowloon
        "tsim_sha_tsui": "hk_kowloon",
        "hung_hom": "hk_kowloon",
        "kowloon_city": "hk_kowloon",
        "san_po_kong": "hk_kowloon",
        "mong_kok": "hk_kowloon",
        
        # New Territories West
        "yuen_long": "hk_new_territories_west",
        "lau_fau_shan": "hk_new_territories_west",
        "tin_shui_wai": "hk_new_territories_west",
        "tuen_mun": "hk_new_territories_west",
        
        # New Territories East
        "sai_kung": "hk_new_territories_east",
        "sha_tin": "hk_new_territories_east",
        "tai_wai": "hk_new_territories_east",
        "ma_on_shan": "hk_new_territories_east",
        
        # Islands
        "lantau": "hk_islands",
        "cheung_chau": "hk_islands",
        "peng_chau": "hk_islands",
        "discovery_bay": "hk_islands"
    }
    
    location_lower = location.lower().replace(" ", "_")
    return location_map.get(location_lower, "hk_central")