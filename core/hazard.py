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
        asset_type: str = "residential"
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
            
        Returns:
            Damage ratio as float (0.0 to 1.0)
        """
        # Base damage curve
        if depth_m <= 0:
            return 0.0
        elif depth_m <= 0.3:
            return 0.05 + 0.10 * (depth_m / 0.3)
        elif depth_m <= 1.0:
            return 0.15 + 0.25 * ((depth_m - 0.3) / 0.7)
        elif depth_m <= 2.0:
            return 0.40 + 0.30 * ((depth_m - 1.0) / 1.0)
        else:
            return min(1.0, 0.70 + 0.15 * min(1.0, (depth_m - 2.0) / 3.0))
    
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
    """
    
    # Example data structure for regional flood parameters
    FLOOD_ZONES = {
        "bangkok_central": {
            "flood_risk_level": "high",
            "avg_depth_10yr_m": 0.3,
            "avg_depth_100yr_m": 1.2,
            "avg_depth_500yr_m": 2.0,
            "frequency_increase_rate": 0.02  # 2% per year
        },
        "bangkok_peripheral": {
            "flood_risk_level": "medium",
            "avg_depth_10yr_m": 0.2,
            "avg_depth_100yr_m": 0.8,
            "avg_depth_500yr_m": 1.5,
            "frequency_increase_rate": 0.015
        },
        "ayutthaya_industrial": {
            "flood_risk_level": "very_high",
            "avg_depth_10yr_m": 0.8,
            "avg_depth_100yr_m": 2.5,
            "avg_depth_500yr_m": 3.5,
            "frequency_increase_rate": 0.03
        }
    }
    
    def get_regional_hazard_params(
        self,
        region: str,
        hazard_type: str,
        return_period: int = 100
    ) -> Dict:
        """
        Get baseline hazard parameters for a region.
        
        Args:
            region: Region identifier
            hazard_type: Type of hazard
            return_period: Return period in years
            
        Returns:
            Dictionary with hazard parameters
        """
        if hazard_type == "flood":
            zone_data = self.FLOOD_ZONES.get(region, self.FLOOD_ZONES["bangkok_peripheral"])
            
            depth_key = f"avg_depth_{return_period}yr_m"
            base_depth = zone_data.get(depth_key, zone_data["avg_depth_100yr_m"])
            
            return {
                "region": region,
                "hazard_type": hazard_type,
                "risk_level": zone_data["flood_risk_level"],
                "base_depth_m": base_depth,
                "frequency_increase_rate": zone_data["frequency_increase_rate"]
            }
        
        return {
            "region": region,
            "hazard_type": hazard_type,
            "risk_level": "unknown"
        }
