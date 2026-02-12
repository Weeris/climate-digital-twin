"""
Hazard Assessment Module

Provides physical climate risk assessment for:
- Flood
- Wildfire
- Cyclone
- Drought

Uses hazard-vulnerability-exposure framework for damage estimation.
"""

from typing import Dict, Callable, Tuple
import math


class HazardAssessment:
    """
    Physical climate hazard assessment for financial risk modeling.
    
    Implements damage functions for various climate hazards
    with focus on real estate portfolio impact.
    """
    
    def __init__(self):
        """Initialize hazard assessment module."""
        self.damage_functions = self._initialize_damage_functions()
    
    def _initialize_damage_functions(self) -> Dict[str, Callable]:
        """Initialize damage functions for each hazard type."""
        return {
            "flood": self._flood_damage_curve,
            "wildfire": self._wildfire_damage_curve,
            "cyclone": self._cyclone_damage_curve,
            "drought": self._drought_damage_curve
        }
    
    def assess_hazard(
        self,
        hazard_type: str,
        intensity: float,
        asset_value: float,
        asset_type: str = "residential",
        construction_type: str = "reinforced_concrete"
    ) -> Dict:
        """
        Assess physical damage from a climate hazard.
        
        Args:
            hazard_type: Type of hazard (flood, wildfire, cyclone, drought)
            intensity: Hazard intensity (depends on hazard type)
            asset_value: Value of the asset
            asset_type: Type of asset (residential, commercial, industrial)
            construction_type: Building construction type
            
        Returns:
            Dictionary with damage assessment results
        """
        if hazard_type not in self.damage_functions:
            raise ValueError(f"Unknown hazard type: {hazard_type}")
        
        damage_func = self.damage_functions[hazard_type]
        
        # Calculate damage ratio
        damage_ratio = damage_func(intensity, asset_type, construction_type)
        
        # Calculate physical damage
        physical_damage = asset_value * damage_ratio
        
        # Estimate downtime
        downtime = self._estimate_downtime(
            hazard_type, intensity, asset_type
        )
        
        # Calculate residual value
        residual_value = asset_value - physical_damage
        
        return {
            "hazard_type": hazard_type,
            "intensity": intensity,
            "damage_ratio": damage_ratio,
            "physical_damage": physical_damage,
            "residual_value": residual_value,
            "downtime_days": downtime,
            "asset_value": asset_value,
            "asset_type": asset_type,
            "construction_type": construction_type
        }
    
    def assess_flood_risk(
        self,
        depth_m: float,
        asset_value: float,
        asset_type: str = "residential",
        duration_hours: float = 24.0
    ) -> Dict:
        """
        Assess flood risk for an asset.
        
        Args:
            depth_m: Flood water depth in meters
            asset_value: Value of the asset
            asset_type: Type of asset
            duration_hours: Duration of flooding in hours
            
        Returns:
            Flood risk assessment results
        """
        damage_ratio = self._flood_damage_curve(depth_m, asset_type)
        physical_damage = asset_value * damage_ratio
        
        # Downtime increases with depth and duration
        downtime_base = self._flood_downtime_base(depth_m)
        duration_factor = 1 + (duration_hours - 24) / 72  # +1 day per 72 extra hours
        downtime = downtime_base * duration_factor
        
        return {
            "hazard_type": "flood",
            "depth_m": depth_m,
            "duration_hours": duration_hours,
            "damage_ratio": damage_ratio,
            "physical_damage": physical_damage,
            "residual_value": asset_value - physical_damage,
            "downtime_days": downtime,
            "repair_cost_estimate": physical_damage * 1.15,  # +15% contingency
            "temporary_accommodation_cost": downtime * 500 if asset_type == "residential" else 0
        }
    
    def _flood_damage_curve(
        self,
        depth_m: float,
        asset_type: str = "residential",
        construction_type: str = "reinforced_concrete"
    ) -> float:
        """
        Depth-damage curve for flood events.

        Based on typical insurance damage functions:
        - 0-0.3m: Minor damage (5-15%)
        - 0.3-1.0m: Moderate damage (15-40%)
        - 1.0-2.0m: Severe damage (40-70%)
        - >2.0m: Major damage (70-100%)

        Args:
            depth_m: Flood water depth in meters
            asset_type: Type of asset
            construction_type: Building construction type

        Returns:
            Damage ratio as float (0.0 to 1.0)
        """
        # Construction type resilience
        resilience_factors = {
            "reinforced_concrete": 0.8,
            "masonry": 1.0,
            "wood": 1.4,
            "steel": 0.9,
            "traditional": 1.3
        }

        # Base damage curve
        if depth_m <= 0:
            base_damage = 0.0
        elif depth_m <= 0.3:
            base_damage = 0.05 + 0.10 * (depth_m / 0.3)
        elif depth_m <= 1.0:
            base_damage = 0.15 + 0.25 * ((depth_m - 0.3) / 0.7)
        elif depth_m <= 2.0:
            base_damage = 0.40 + 0.30 * ((depth_m - 1.0) / 1.0)
        else:
            base_damage = min(1.0, 0.70 + 0.15 * min(1.0, (depth_m - 2.0) / 3.0))

        # Apply construction resilience
        resilience = resilience_factors.get(construction_type, 1.0)
        return min(1.0, base_damage * resilience)
    
    def _flood_downtime_base(self, depth_m: float) -> int:
        """
        Estimate base downtime for flood recovery.
        
        Args:
            depth_m: Flood water depth
            
        Returns:
            Estimated downtime in days
        """
        if depth_m <= 0.3:
            return 7
        elif depth_m <= 1.0:
            return 21
        elif depth_m <= 2.0:
            return 45
        else:
            return 90
    
    def _wildfire_damage_curve(
        self,
        burn_percentage: float,
        asset_type: str = "residential",
        construction_type: str = "reinforced_concrete"
    ) -> float:
        """
        Damage curve for wildfire events.
        
        Args:
            burn_percentage: Percentage of asset burned (0-100)
            asset_type: Type of asset
            construction_type: Building construction type
            
        Returns:
            Damage ratio
        """
        # Construction type resilience
        resilience_factors = {
            "reinforced_concrete": 0.8,
            "masonry": 1.0,
            "wood": 1.3,
            "steel": 0.9
        }
        
        resilience = resilience_factors.get(construction_type, 1.0)
        
        # Base damage from burn percentage
        burn_ratio = burn_percentage / 100.0
        base_damage = burn_ratio * resilience
        
        return min(1.0, base_damage)
    
    def _cyclone_damage_curve(
        self,
        wind_speed_kmh: float,
        asset_type: str = "residential",
        construction_type: str = "reinforced_concrete"
    ) -> float:
        """
        Wind damage curve for cyclone events.
        
        Based on Saffir-Simpson equivalent:
        - Tropical Depression (<63 km/h): Minimal
        - Tropical Storm (63-118 km/h): Some damage
        - Category 1 (119-153 km/h): Dangerous winds
        - Category 2 (154-177 km/h): Extremely dangerous
        - Category 3 (178-208 km/h): Devastating
        - Category 4 (209-251 km/h): Catastrophic
        - Category 5 (>252 km/h): Unprecedented
        
        Args:
            wind_speed_kmh: Maximum sustained wind speed
            asset_type: Type of asset
            construction_type: Building construction type
            
        Returns:
            Damage ratio
        """
        # Base damage by wind speed
        if wind_speed_kmh < 63:
            return 0.0
        elif wind_speed_kmh < 119:
            base_damage = 0.05 + 0.10 * ((wind_speed_kmh - 63) / 56)
        elif wind_speed_kmh < 154:
            base_damage = 0.15 + 0.15 * ((wind_speed_kmh - 119) / 35)
        elif wind_speed_kmh < 178:
            base_damage = 0.30 + 0.20 * ((wind_speed_kmh - 154) / 24)
        elif wind_speed_kmh < 209:
            base_damage = 0.50 + 0.20 * ((wind_speed_kmh - 178) / 31)
        elif wind_speed_kmh < 252:
            base_damage = 0.70 + 0.20 * ((wind_speed_kmh - 209) / 43)
        else:
            base_damage = min(1.0, 0.90 + 0.05 * ((wind_speed_kmh - 252) / 50))
        
        # Construction resilience adjustment
        resilience_factors = {
            "reinforced_concrete": 0.7,
            "masonry": 0.9,
            "wood": 1.2,
            "steel": 0.8
        }
        
        resilience = resilience_factors.get(construction_type, 1.0)
        return min(1.0, base_damage * resilience)
    
    def _drought_damage_curve(
        self,
        spi_index: float,
        asset_type: str = "residential"
    ) -> float:
        """
        Damage curve for drought events.
        
        Uses Standardized Precipitation Index (SPI):
        - Normal (-0.5 to 0.5): Minimal impact
        - Dry (-1.0 to -0.5): Some stress
        - Very Dry (-1.5 to -1.0): Significant impact
        - Extremely Dry (< -1.5): Severe
        
        Primarily affects:
        - Agricultural assets
        - Water-dependent industries
        - Property value in drought-prone areas
        
        Args:
            spi_index: Standardized Precipitation Index
            asset_type: Type of asset
            
        Returns:
            Damage ratio
        """
        if asset_type in ["agricultural", "farm"]:
            # Agricultural assets most affected
            if spi_index >= -0.5:
                return 0.0
            elif spi_index >= -1.0:
                return 0.10 + 0.15 * abs(spi_index + 0.5) / 0.5
            elif spi_index >= -1.5:
                return 0.25 + 0.25 * abs(spi_index + 1.0) / 0.5
            else:
                return min(1.0, 0.50 + 0.25 * abs(spi_index + 1.5) / 1.0)
        else:
            # Residential/commercial less directly affected
            # Secondary effects through water prices, ecosystem
            if spi_index >= -0.5:
                return 0.0
            elif spi_index >= -1.0:
                return 0.02 + 0.03 * abs(spi_index + 0.5) / 0.5
            elif spi_index >= -1.5:
                return 0.05 + 0.05 * abs(spi_index + 1.0) / 0.5
            else:
                return min(1.0, 0.10 + 0.05 * abs(spi_index + 1.5) / 1.0)
    
    def _estimate_downtime(
        self,
        hazard_type: str,
        intensity: float,
        asset_type: str = "residential"
    ) -> int:
        """
        Estimate recovery downtime after a climate event.
        
        Args:
            hazard_type: Type of hazard
            intensity: Hazard intensity
            asset_type: Type of asset
            
        Returns:
            Estimated downtime in days
        """
        base_downtime_map = {
            "flood": 21,
            "wildfire": 60,
            "cyclone": 30,
            "drought": 7
        }
        
        base = base_downtime_map.get(hazard_type, 14)
        
        # Intensity factor
        intensity_factor = 1.0
        if hazard_type == "flood":
            intensity_factor = 1 + intensity / 2
        elif hazard_type == "cyclone":
            intensity_factor = intensity / 150  # Normalize to ~150 km/h
        
        # Asset type factor
        asset_factor_map = {
            "residential": 1.0,
            "commercial": 1.2,
            "industrial": 1.5
        }
        asset_factor = asset_factor_map.get(asset_type, 1.0)
        
        return int(base * intensity_factor * asset_factor)


class RegionalHazardData:
    """
    Regional hazard data provider.
    
    Provides baseline hazard parameters for different regions.
    Supports both Bangkok/Thailand regions and Hong Kong zones.
    """
    
    # Example data structure for regional flood parameters
    FLOOD_ZONES = {
        # Bangkok/Thailand regions
        "bangkok_central": {
            "flood_risk_level": "high",
            "avg_depth_10yr_m": 0.3,
            "avg_depth_50yr_m": 0.7,
            "avg_depth_100yr_m": 1.2,
            "avg_depth_500yr_m": 2.0,
            "frequency_increase_rate": 0.02  # 2% per year
        },
        "bangkok_peripheral": {
            "flood_risk_level": "medium",
            "avg_depth_10yr_m": 0.2,
            "avg_depth_50yr_m": 0.5,
            "avg_depth_100yr_m": 0.8,
            "avg_depth_500yr_m": 1.5,
            "frequency_increase_rate": 0.015
        },
        "ayutthaya_industrial": {
            "flood_risk_level": "very_high",
            "avg_depth_10yr_m": 0.8,
            "avg_depth_50yr_m": 1.5,
            "avg_depth_100yr_m": 2.5,
            "avg_depth_500yr_m": 3.5,
            "frequency_increase_rate": 0.03
        },
        
        # Hong Kong Zones
        "hk_central": {
            "flood_risk_level": "high",
            "avg_depth_10yr_m": 0.5,
            "avg_depth_50yr_m": 1.0,
            "avg_depth_100yr_m": 1.5,
            "avg_depth_500yr_m": 2.5,
            "storm_surge_risk": True,
            "storm_surge_additional_m": 0.8,
            "frequency_increase_rate": 0.025
        },
        "hk_kowloon": {
            "flood_risk_level": "high",
            "avg_depth_10yr_m": 0.4,
            "avg_depth_50yr_m": 0.9,
            "avg_depth_100yr_m": 1.4,
            "avg_depth_500yr_m": 2.3,
            "storm_surge_risk": True,
            "storm_surge_additional_m": 0.7,
            "frequency_increase_rate": 0.025
        },
        "hk_new_territories_west": {
            "flood_risk_level": "very_high",
            "avg_depth_10yr_m": 0.6,
            "avg_depth_50yr_m": 1.2,
            "avg_depth_100yr_m": 1.8,
            "avg_depth_500yr_m": 3.0,
            "storm_surge_risk": True,
            "storm_surge_additional_m": 1.0,
            "frequency_increase_rate": 0.035
        },
        "hk_new_territories_east": {
            "flood_risk_level": "medium",
            "avg_depth_10yr_m": 0.2,
            "avg_depth_50yr_m": 0.5,
            "avg_depth_100yr_m": 0.8,
            "avg_depth_500yr_m": 1.5,
            "storm_surge_risk": False,
            "storm_surge_additional_m": 0.0,
            "frequency_increase_rate": 0.015
        },
        "hk_islands": {
            "flood_risk_level": "medium",
            "avg_depth_10yr_m": 0.3,
            "avg_depth_50yr_m": 0.6,
            "avg_depth_100yr_m": 1.0,
            "avg_depth_500yr_m": 2.0,
            "storm_surge_risk": True,
            "storm_surge_additional_m": 0.9,
            "frequency_increase_rate": 0.020
        }
    }
    
    def get_regional_hazard_params(
        self,
        region: str,
        hazard_type: str,
        return_period: int = 100,
        include_storm_surge: bool = False
    ) -> Dict:
        """
        Get baseline hazard parameters for a region.
        
        Args:
            region: Region identifier
            hazard_type: Type of hazard
            return_period: Return period in years
            include_storm_surge: Include storm surge depth for coastal zones
            
        Returns:
            Dictionary with hazard parameters
        """
        if hazard_type == "flood":
            zone_data = self.FLOOD_ZONES.get(region, self.FLOOD_ZONES["bangkok_peripheral"])
            
            depth_key = f"avg_depth_{return_period}yr_m"
            base_depth = zone_data.get(depth_key, zone_data["avg_depth_100yr_m"])
            
            result = {
                "region": region,
                "hazard_type": hazard_type,
                "risk_level": zone_data["flood_risk_level"],
                "base_depth_m": base_depth,
                "frequency_increase_rate": zone_data["frequency_increase_rate"]
            }
            
            # Add storm surge parameters for HK zones
            if "storm_surge_risk" in zone_data:
                result["storm_surge_risk"] = zone_data["storm_surge_risk"]
                if include_storm_surge and zone_data.get("storm_surge_risk"):
                    result["base_depth_m"] += zone_data.get("storm_surge_additional_m", 0)
                    result["storm_surge_additional_m"] = zone_data.get("storm_surge_additional_m", 0)
            
            return result
        
        return {
            "region": region,
            "hazard_type": hazard_type,
            "risk_level": "unknown"
        }


# =====================
# HK-SPECIFIC METHODS
# =====================

class HKHazardAssessment:
    """
    Hong Kong-specific hazard assessment methods.
    
    Extends the base HazardAssessment with HK-specific damage functions
    for high-rise buildings, MTR infrastructure, and local building types.
    """
    
    # HK building types for asset classification
    HK_BUILDING_TYPES = [
        "residential_high_rise",
        "residential_walkup",
        "commercial_office",
        "commercial_mall",
        "commercial_hotel",
        "industrial_factory",
        "industrial_warehouse",
        "infrastructure_mtr",
        "infrastructure_tunnel",
        "infrastructure_bridge",
    ]
    
    def __init__(self):
        """Initialize HK hazard assessment."""
        self.base_assessment = HazardAssessment()
    
    def assess_hk_flood_risk(
        self,
        district: str,
        building_type: str,
        flood_depth_m: float,
        building_value_hkd: float,
        num_floors: int = 30,
        has_basement: bool = False,
        flood_duration_hours: float = 24.0,
        include_storm_surge: bool = True
    ) -> Dict:
        """
        Assess flood risk for HK property.
        
        Args:
            district: HK district (e.g., "central", "kowloon", "tuen_mun")
            building_type: Type of building
            flood_depth_m: Flood water depth in meters
            building_value_hkd: Building value in HKD
            num_floors: Number of floors (for high-rise adjustment)
            has_basement: Has basement carpark
            flood_duration_hours: Duration of flooding
            include_storm_surge: Include storm surge if coastal
            
        Returns:
            Dictionary with flood risk assessment
        """
        # Storm surge adjustment for coastal districts
        surge_addition = 0.0
        coastal_districts = ["central", "wan_chai", "causeway_bay", "tsim_sha_tsui", "hung_hom", "islands"]
        if include_storm_surge and district.lower() in coastal_districts:
            surge_addition = 0.7  # Average storm surge for HK
        
        adjusted_depth = flood_depth_m + surge_addition
        
        # High-rise adjustment (flood affects lower floors only)
        if building_type == "residential_high_rise" and num_floors > 10:
            affected_floors_ratio = min(0.25, 5 / num_floors)  # Max 5 floors affected
            value_multiplier = affected_floors_ratio * 0.8  # Lower floors worth less
        elif has_basement:
            value_multiplier = 0.20  # Basement damage
        else:
            value_multiplier = min(1.0, (flood_depth_m / 2.0))
        
        # Damage calculation
        damage_ratio = self._hk_flood_damage_curve(adjusted_depth, building_type)
        physical_damage = building_value_hkd * damage_ratio * value_multiplier
        
        # Downtime estimation
        downtime = self._hk_flood_downtime(building_type, adjusted_depth)
        
        return {
            "hazard_type": "flood",
            "district": district,
            "building_type": building_type,
            "flood_depth_m": flood_depth_m,
            "storm_surge_addition_m": surge_addition if include_storm_surge else 0,
            "adjusted_depth_m": adjusted_depth,
            "damage_ratio": damage_ratio,
            "value_multiplier": value_multiplier,
            "physical_damage_hkd": physical_damage,
            "downtime_days": downtime,
            "flood_risk_level": self._get_flood_risk_level(district),
        }
    
    def assess_hk_typhoon_risk(
        self,
        building_type: str,
        wind_speed_kmh: float,
        building_value_hkd: float,
        construction: str = "reinforced_concrete",
        has_glass_curtain: bool = False,
        facade_area_sqm: float = 1000.0,
        num_windows: int = 100
    ) -> Dict:
        """
        Assess typhoon risk for HK property.
        
        Args:
            building_type: Type of building
            wind_speed_kmh: Maximum sustained wind speed
            building_value_hkd: Building value in HKD
            construction: Construction type
            has_glass_curtain: Has glass curtain wall
            facade_area_sqm: Facade area
            num_windows: Number of windows
            
        Returns:
            Dictionary with typhoon risk assessment
        """
        # Window damage
        window_damage = self._hk_window_breakage(wind_speed_kmh)
        window_cost = num_windows * window_damage * 5000  # HKD 5,000 per window
        
        # Facade damage (glass curtain walls common in HK)
        facade_damage = 0.0
        if has_glass_curtain:
            facade_damage = self._hk_facade_damage(wind_speed_kmh)
            facade_cost = facade_area_sqm * facade_damage * 8000
        else:
            facade_cost = 0.0
        
        # Structural damage
        structural_damage = self._hk_typhoon_structural(wind_speed_kmh, construction)
        
        # Signage and ancillary damage
        ancillary_damage = 0.0
        if wind_speed_kmh > 100:
            ancillary_damage = 30000  # Signage, AC units
        
        total_damage = window_cost + facade_cost + ancillary_damage
        damage_ratio = min(1.0, total_damage / building_value_hkd)
        
        return {
            "hazard_type": "typhoon",
            "building_type": building_type,
            "wind_speed_kmh": wind_speed_kmh,
            "signal_equivalent": self._wind_to_signal(wind_speed_kmh),
            "window_damage_ratio": window_damage,
            "window_replacement_cost": window_cost,
            "facade_damage_ratio": facade_damage,
            "facade_repair_cost": facade_cost,
            "structural_damage_ratio": structural_damage,
            "ancillary_damage_cost": ancillary_damage,
            "total_damage_hkd": total_damage,
            "damage_ratio": damage_ratio,
            "downtime_days": self._hk_typhoon_downtime(wind_speed_kmh),
        }
    
    def get_hk_zone_for_location(self, location: str) -> str:
        """Map location to HK hazard zone."""
        location_map = {
            "central": "hk_central", "admiralty": "hk_central",
            "wan_chai": "hk_central", "causeway_bay": "hk_central",
            "tsim_sha tsui": "hk_kowloon", "tst": "hk_kowloon",
            "hung hom": "hk_kowloon", "mong kok": "hk_kowloon",
            "tuen mun": "hk_new_territories_west", "yuen long": "hk_new_territories_west",
            "tin shui wai": "hk_new_territories_west",
            "sha tin": "hk_new_territories_east", "sai kung": "hk_new_territories_east",
            "lantau": "hk_islands", "cheung chau": "hk_islands",
        }
        return location_map.get(location.lower(), "hk_central")
    
    def _hk_flood_damage_curve(self, depth_m: float, building_type: str) -> float:
        """HK-specific flood damage curve."""
        if depth_m <= 0:
            return 0.0
        elif depth_m <= 0.3:
            return 0.08 + 0.12 * (depth_m / 0.3)
        elif depth_m <= 1.0:
            return 0.20 + 0.30 * ((depth_m - 0.3) / 0.7)
        elif depth_m <= 2.0:
            return 0.50 + 0.30 * ((depth_m - 1.0) / 1.0)
        else:
            return min(1.0, 0.80 + 0.10 * min(1.0, (depth_m - 2.0) / 3.0))
    
    def _hk_window_breakage(self, wind_speed: float) -> float:
        """Window breakage probability by wind speed."""
        if wind_speed < 80:
            return 0.0
        elif wind_speed < 120:
            return 0.15 + 0.20 * ((wind_speed - 80) / 40)
        elif wind_speed < 180:
            return 0.35 + 0.40 * ((wind_speed - 120) / 60)
        else:
            return min(1.0, 0.75 + 0.15 * min(1.0, (wind_speed - 180) / 70))
    
    def _hk_facade_damage(self, wind_speed: float) -> float:
        """Glass curtain wall facade damage."""
        if wind_speed < 100:
            return 0.0
        elif wind_speed < 150:
            return 0.10 + 0.25 * ((wind_speed - 100) / 50)
        elif wind_speed < 200:
            return 0.35 + 0.35 * ((wind_speed - 150) / 50)
        else:
            return min(1.0, 0.70 + 0.20 * min(1.0, (wind_speed - 200) / 50))
    
    def _hk_typhoon_structural(self, wind_speed: float, construction: str) -> float:
        """Structural damage from typhoon."""
        thresholds = {
            "reinforced_concrete": 119,
            "steel_frame": 130,
            "glass_curtain_wall": 100,
            "masonry": 140,
        }
        threshold = thresholds.get(construction, 120)
        
        if wind_speed < threshold:
            return 0.0
        elif wind_speed < 180:
            return 0.10 + 0.40 * ((wind_speed - threshold) / (180 - threshold))
        else:
            return min(1.0, 0.50 + 0.30 * min(1.0, (wind_speed - 180) / 70))
    
    def _wind_to_signal(self, wind_speed: float) -> str:
        """Convert wind speed to HK signal."""
        if wind_speed < 41:
            return "Signal 1"
        elif wind_speed < 63:
            return "Signal 3"
        elif wind_speed < 118:
            return "Signal 8"
        elif wind_speed < 150:
            return "Signal 9"
        else:
            return "Signal 10"
    
    def _hk_flood_downtime(self, building_type: str, depth_m: float) -> int:
        """Estimate HK flood recovery time."""
        base_days = {
            "residential_high_rise": 45,
            "residential_walkup": 30,
            "commercial_office": 60,
            "commercial_mall": 75,
            "commercial_hotel": 90,
            "industrial_factory": 45,
            "industrial_warehouse": 30,
            "infrastructure_mtr": 120,
            "infrastructure_tunnel": 180,
            "infrastructure_bridge": 90,
        }.get(building_type, 30)
        
        depth_factor = 1.0 + max(0, (depth_m - 1.0) * 0.15)
        return int(base_days * depth_factor)
    
    def _hk_typhoon_downtime(self, wind_speed: float) -> int:
        """Estimate typhoon recovery time."""
        if wind_speed < 100:
            return 3
        elif wind_speed < 150:
            return 7
        elif wind_speed < 200:
            return 14
        else:
            return 30
    
    def _get_flood_risk_level(self, district: str) -> str:
        """Get flood risk level for district."""
        risk_levels = {
            "central": "high", "wan_chai": "high", "causeway_bay": "high",
            "tsim_sha_tsui": "high", "kowloon": "high",
            "hung_hom": "medium", "mong_kok": "medium",
            "tuen_mun": "very_high", "yuen_long": "very_high", "tin_shui_wai": "very_high",
            "sha_tin": "medium", "sai_kung": "medium",
            "lantau": "medium", "islands": "medium",
        }
        return risk_levels.get(district.lower(), "medium")

