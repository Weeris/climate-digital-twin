"""
HK Building Damage Functions Module

Provides Hong Kong-specific damage functions for physical climate risk assessment.
Includes damage curves for:
- Flood damage (ground floor, high-rise, subway, basement)
- Typhoon/cyclone damage (windows, facades, structural)
- Fire damage (building spread, fire resistance)
- Downtime estimates for HK buildings

Based on HK building characteristics and historical incident data.
"""

from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class HKBuildingType(str, Enum):
    """Hong Kong building types."""
    RESIDENTIAL_HIGH_RISE = "residential_high_rise"
    RESIDENTIAL_WALKUP = "residential_walkup"
    COMMERCIAL_OFFICE = "commercial_office"
    COMMERCIAL_MALL = "commercial_mall"
    COMMERCIAL_HOTEL = "commercial_hotel"
    INDUSTRIAL_FACTORY = "industrial_factory"
    INDUSTRIAL_WAREHOUSE = "industrial_warehouse"
    INFRASTRUCTURE_MTR = "infrastructure_mtr"
    INFRASTRUCTURE_TUNNEL = "infrastructure_tunnel"
    INFRASTRUCTURE_BRIDGE = "infrastructure_bridge"


class HKConstructionType(str, Enum):
    """Construction types common in HK."""
    REINFORCED_CONCRETE = "reinforced_concrete"
    STEEL_FRAME = "steel_frame"
    GLASS_CURTAIN_WALL = "glass_curtain_wall"
    MASONRY = "masonry"
    COMPOSITE = "composite"


@dataclass
class HKBuildingDamageResult:
    """Result of HK building damage assessment."""
    damage_ratio: float
    physical_damage_hkd: float
    repair_cost_hkd: float
    downtime_days: int
    relocation_cost_hkd: float
    business_interruption_hkd: float
    affected_floors: int
    damage_breakdown: Dict[str, float]


class HKBuildingDamageFunctions:
    """
    HK-specific building damage functions for climate risk assessment.
    
    Implements damage curves tailored to Hong Kong's unique building
    characteristics including high-rise residential towers, mixed-use
    developments, and critical infrastructure.
    """
    
    # Floor damage thresholds by building type
    FLOOR_THRESHOLDS: Dict[HKBuildingType, Tuple[int, int]] = {
        HKBuildingType.RESIDENTIAL_HIGH_RISE: (0, 5),
        HKBuildingType.RESIDENTIAL_WALKUP: (0, 3),
        HKBuildingType.COMMERCIAL_OFFICE: (0, 3),
        HKBuildingType.COMMERCIAL_MALL: (0, 2),
        HKBuildingType.COMMERCIAL_HOTEL: (0, 4),
        HKBuildingType.INDUSTRIAL_FACTORY: (0, 1),
        HKBuildingType.INDUSTRIAL_WAREHOUSE: (0, 1),
        HKBuildingType.INFRASTRUCTURE_MTR: (0, 0),
        HKBuildingType.INFRASTRUCTURE_TUNNEL: (0, 0),
        HKBuildingType.INFRASTRUCTURE_BRIDGE: (0, 0),
    }
    
    # Window breakage thresholds (wind speed km/h)
    WINDOW_BREAKAGE_THRESHOLDS: Dict[str, Tuple[float, float]] = {
        "standard_single": (80, 120),
        "standard_double": (100, 150),
        "impact_resistant": (150, 200),
        "hurricane_rated": (200, 250),
    }
    
    # Fire resistance ratings (hours)
    FIRE_RESISTANCE_RATINGS: Dict[str, int] = {
        "pre_1960": 0.5,
        "1960_1980": 1.0,
        "1980_2000": 1.5,
        "post_2000": 2.0,
        "premium": 3.0,
    }
    
    def __init__(self):
        """Initialize HK building damage functions."""
        pass
    
    def assess_flood_damage(
        self,
        building_type: HKBuildingType,
        flood_depth_m: float,
        building_value_hkd: float,
        construction_type: HKConstructionType = HKConstructionType.REINFORCED_CONCRETE,
        num_floors: int = 30,
        flood_duration_hours: float = 24.0,
        has_basement: bool = False,
    ) -> HKBuildingDamageResult:
        """
        Assess flood damage for HK building.
        
        Args:
            building_type: Type of HK building
            flood_depth_m: Flood water depth in meters
            building_value_hkd: Total building value
            construction_type: Construction type
            num_floors: Total number of floors
            flood_duration_hours: Duration of flooding
            has_basement: Whether building has basement carpark
            
        Returns:
            HKBuildingDamageResult with damage assessment
        """
        if flood_depth_m <= 0:
            return HKBuildingDamageResult(
                damage_ratio=0.0,
                physical_damage_hkd=0.0,
                repair_cost_hkd=0.0,
                downtime_days=0,
                relocation_cost_hkd=0.0,
                business_interruption_hkd=0.0,
                affected_floors=0,
                damage_breakdown={}
            )
        
        floor_thresholds = self.FLOOR_THRESHOLDS.get(building_type, (0, 2))
        
        # High-rise: flood affects lower floors only
        if building_type == HKBuildingType.RESIDENTIAL_HIGH_RISE:
            floor_coverage = min(
                floor_thresholds[1],
                max(1, int((flood_depth_m - 3.5) / 3.0)) + 1
            )
            affected_floors = floor_coverage
        else:
            affected_floors = min(
                5, max(floor_thresholds[0], int(flood_depth_m / 3.0) + 1)
            )
        
        # Calculate damage ratio
        if building_type == HKBuildingType.RESIDENTIAL_HIGH_RISE:
            affected_value_ratio = max(0.1, (affected_floors / num_floors) * 0.7)
        elif has_basement:
            affected_value_ratio = 0.15 + (affected_floors * 0.05)
        else:
            affected_value_ratio = min(1.0, affected_floors * 0.15)
        
        # Damage curves
        ground_damage = self._ground_floor_damage_curve(flood_depth_m)
        upper_damage = self._upper_floor_damage_curve(flood_depth_m)
        basement_damage = self._basement_damage_curve(flood_depth_m) if has_basement else 0.0
        
        total_damage_ratio = (
            ground_damage * 0.3 +
            upper_damage * affected_value_ratio * 0.5 +
            basement_damage * 0.2
        )
        
        # Duration factor
        duration_factor = 1.0 + max(0, (flood_duration_hours - 24) / 72)
        total_damage_ratio *= duration_factor
        total_damage_ratio = min(1.0, total_damage_ratio)
        
        physical_damage = building_value_hkd * total_damage_ratio
        repair_cost = physical_damage * 1.15
        
        downtime = self._hk_flood_downtime(building_type, flood_depth_m)
        relocation = self._hk_relocation_cost(building_type, affected_floors, building_value_hkd)
        business_interruption = self._hk_business_interruption(building_type, downtime, building_value_hkd)
        
        return HKBuildingDamageResult(
            damage_ratio=total_damage_ratio,
            physical_damage_hkd=physical_damage,
            repair_cost_hkd=repair_cost,
            downtime_days=downtime,
            relocation_cost_hkd=relocation,
            business_interruption_hkd=business_interruption,
            affected_floors=affected_floors,
            damage_breakdown={
                "ground_floor": ground_damage,
                "upper_floors": upper_damage,
                "basement": basement_damage,
                "duration_factor": duration_factor,
            }
        )
    
    def assess_typhoon_damage(
        self,
        building_type: HKBuildingType,
        wind_speed_kmh: float,
        building_value_hkd: float,
        construction_type: HKConstructionType = HKConstructionType.REINFORCED_CONCRETE,
        facade_area_sqm: float = 1000.0,
        window_type: str = "standard_double",
        num_windows: int = 100,
        has_signage: bool = True,
        has_ac_units: bool = True,
    ) -> Dict:
        """
        Assess typhoon damage for HK building.
        
        Args:
            building_type: Type of HK building
            wind_speed_kmh: Maximum sustained wind speed
            building_value_hkd: Total building value
            construction_type: Construction type
            facade_area_sqm: Facade/curtain wall area
            window_type: Window type
            num_windows: Number of windows
            has_signage: Has external signage
            has_ac_units: Has external AC units
            
        Returns:
            Dictionary with typhoon damage assessment
        """
        if wind_speed_kmh < 63:  # Below tropical storm
            return {
                "damage_ratio": 0.0,
                "physical_damage_hkd": 0.0,
                "window_damage_ratio": 0.0,
                "facade_damage_ratio": 0.0,
                "structural_damage_ratio": 0.0,
                "downtime_days": 0,
            }
        
        # Window breakage
        window_thresh = self.WINDOW_BREAKAGE_THRESHOLDS.get(window_type, (100, 150))
        window_damage = self._window_breakage_curve(wind_speed_kmh, window_thresh)
        window_cost = num_windows * window_damage * 5000
        
        # Facade damage
        facade_damage = self._facade_damage_curve(wind_speed_kmh, construction_type)
        facade_cost = facade_area_sqm * facade_damage * 8000
        
        # Structural damage
        structural_damage = self._typhoon_structural_damage(wind_speed_kmh, construction_type)
        
        # Signage/AC damage
        ancillary_damage = 0.0
        if has_signage:
            ancillary_damage += 50000 if wind_speed_kmh > 100 else 20000
        if has_ac_units:
            num_ac = min(20, num_windows // 10)
            ancillary_damage += num_ac * 8000
        
        total_damage = window_cost + facade_cost + ancillary_damage
        damage_ratio = min(1.0, total_damage / building_value_hkd)
        
        return {
            "damage_ratio": damage_ratio,
            "physical_damage_hkd": total_damage,
            "window_damage_ratio": window_damage,
            "facade_damage_ratio": facade_damage,
            "structural_damage_ratio": structural_damage,
            "window_replacement_cost": window_cost,
            "facade_repair_cost": facade_cost,
            "ancillary_damage_cost": ancillary_damage,
            "downtime_days": self._typhoon_downtime(building_type, wind_speed_kmh),
        }
    
    def assess_fire_damage(
        self,
        building_type: HKBuildingType,
        burn_percentage: float,
        building_value_hkd: float,
        building_age: str = "1980_2000",
        adjacent_fire: bool = False,
        fire_resistance_rating: str = None,
    ) -> Dict:
        """
        Assess fire damage for HK building.
        
        Args:
            building_type: Type of HK building
            burn_percentage: Percentage of building burned
            building_value_hkd: Total building value
            building_age: Age category
            adjacent_fire: Fire spread from adjacent building
            fire_resistance_rating: Fire resistance rating
            
        Returns:
            Dictionary with fire damage assessment
        """
        if burn_percentage <= 0 and not adjacent_fire:
            return {
                "damage_ratio": 0.0,
                "physical_damage_hkd": 0.0,
                "structural_damage_ratio": 0.0,
                "content_damage_ratio": 0.0,
                "smoke_damage_ratio": 0.0,
                "downtime_days": 0,
            }
        
        rating = fire_resistance_rating or building_age
        fr_rating = self.FIRE_RESISTANCE_RATINGS.get(rating, 1.0)
        resistance_factor = max(0.5, 1.0 - (fr_rating / 4.0))
        separation_factor = 0.8 if adjacent_fire else 1.0
        
        burn_ratio = burn_percentage / 100.0
        structural_damage = burn_ratio * resistance_factor * separation_factor
        content_damage = burn_ratio * 1.2 * resistance_factor
        smoke_damage = 0.15 * separation_factor
        
        total_damage_ratio = min(1.0, structural_damage + content_damage * 0.3 + smoke_damage)
        
        historical_factor = {
            "pre_1960": 1.3, "1960_1980": 1.15, "1980_2000": 1.0,
            "post_2000": 0.9, "premium": 0.8,
        }.get(building_age, 1.0)
        
        total_damage_ratio *= historical_factor
        
        return {
            "damage_ratio": total_damage_ratio,
            "physical_damage_hkd": building_value_hkd * total_damage_ratio,
            "structural_damage_ratio": structural_damage,
            "content_damage_ratio": content_damage,
            "smoke_damage_ratio": smoke_damage,
            "fire_resistance_hours": fr_rating,
            "downtime_days": self._fire_downtime(building_type, burn_percentage),
        }
    
    # ===== INTERNAL CURVES =====
    
    def _ground_floor_damage_curve(self, depth_m: float) -> float:
        """Ground floor damage curve."""
        if depth_m <= 0:
            return 0.0
        elif depth_m <= 0.3:
            return 0.10 + 0.17 * (depth_m / 0.3)
        elif depth_m <= 1.0:
            return 0.27 + 0.33 * ((depth_m - 0.3) / 0.7)
        elif depth_m <= 2.0:
            return 0.60 + 0.25 * ((depth_m - 1.0) / 1.0)
        else:
            return min(1.0, 0.85 + 0.10 * min(1.0, (depth_m - 2.0) / 3.0))
    
    def _upper_floor_damage_curve(self, depth_m: float) -> float:
        """Upper floor damage curve."""
        if depth_m <= 0:
            return 0.0
        elif depth_m <= 0.3:
            return 0.05 + 0.08 * (depth_m / 0.3)
        elif depth_m <= 1.0:
            return 0.13 + 0.17 * ((depth_m - 0.3) / 0.7)
        elif depth_m <= 2.0:
            return 0.30 + 0.20 * ((depth_m - 1.0) / 1.0)
        else:
            return min(1.0, 0.50 + 0.10 * min(1.0, (depth_m - 2.0) / 3.0))
    
    def _basement_damage_curve(self, depth_m: float) -> float:
        """Basement damage curve (more severe)."""
        if depth_m <= 0:
            return 0.0
        elif depth_m <= 0.5:
            return 0.15 + 0.25 * (depth_m / 0.5)
        elif depth_m <= 2.0:
            return 0.40 + 0.35 * ((depth_m - 0.5) / 1.5)
        else:
            return min(1.0, 0.75 + 0.15 * min(1.0, (depth_m - 2.0) / 3.0))
    
    def _window_breakage_curve(self, wind_speed: float, thresholds: Tuple[float, float]) -> float:
        """Window breakage probability curve."""
        init_thresh, fifty_thresh = thresholds
        if wind_speed <= init_thresh:
            return 0.0
        elif wind_speed <= fifty_thresh:
            return 0.3 * ((wind_speed - init_thresh) / (fifty_thresh - init_thresh))
        else:
            return min(1.0, 0.30 + 0.70 * ((wind_speed - fifty_thresh) / (fifty_thresh + 50)))
    
    def _facade_damage_curve(self, wind_speed: float, construction: HKConstructionType) -> float:
        """Facade damage curve for curtain walls."""
        base_thresh = {
            HKConstructionType.GLASS_CURTAIN_WALL: 100,
            HKConstructionType.REINFORCED_CONCRETE: 150,
            HKConstructionType.STEEL_FRAME: 130,
            HKConstructionType.MASONRY: 160,
            HKConstructionType.COMPOSITE: 140,
        }.get(construction, 140)
        
        if wind_speed <= base_thresh:
            return 0.0
        elif wind_speed <= base_thresh + 50:
            return 0.20 * ((wind_speed - base_thresh) / 50)
        elif wind_speed <= base_thresh + 100:
            return 0.20 + 0.40 * ((wind_speed - base_thresh - 50) / 50)
        else:
            return min(1.0, 0.60 + 0.20 * min(1.0, (wind_speed - base_thresh - 100) / 50))
    
    def _typhoon_structural_damage(self, wind_speed: float, construction: HKConstructionType) -> float:
        """Structural damage from typhoon winds."""
        if wind_speed < 119:
            return 0.0
        elif wind_speed < 154:
            return 0.05 + 0.10 * ((wind_speed - 119) / 35)
        elif wind_speed < 178:
            return 0.15 + 0.15 * ((wind_speed - 154) / 24)
        elif wind_speed < 209:
            return 0.30 + 0.15 * ((wind_speed - 178) / 31)
        elif wind_speed < 252:
            return 0.45 + 0.25 * ((wind_speed - 209) / 43)
        else:
            return min(1.0, 0.70 + 0.15 * min(1.0, (wind_speed - 252) / 50))
    
    def _hk_flood_downtime(self, building_type: HKBuildingType, depth_m: float) -> int:
        """Estimate HK flood recovery downtime in days."""
        base_days = {
            HKBuildingType.RESIDENTIAL_HIGH_RISE: 45,
            HKBuildingType.RESIDENTIAL_WALKUP: 30,
            HKBuildingType.COMMERCIAL_OFFICE: 60,
            HKBuildingType.COMMERCIAL_MALL: 75,
            HKBuildingType.COMMERCIAL_HOTEL: 90,
            HKBuildingType.INDUSTRIAL_FACTORY: 45,
            HKBuildingType.INDUSTRIAL_WAREHOUSE: 30,
            HKBuildingType.INFRASTRUCTURE_MTR: 120,
            HKBuildingType.INFRASTRUCTURE_TUNNEL: 180,
            HKBuildingType.INFRASTRUCTURE_BRIDGE: 90,
        }.get(building_type, 30)
        
        depth_factor = 1.0 + (depth_m - 1.0) * 0.2 if depth_m > 1 else 1.0
        return int(base_days * depth_factor)
    
    def _typhoon_downtime(self, building_type: HKBuildingType, wind_speed: float) -> int:
        """Estimate typhoon recovery downtime."""
        if wind_speed < 100:
            return 3
        elif wind_speed < 150:
            return 7
        elif wind_speed < 200:
            return 14
        else:
            return 30
    
    def _fire_downtime(self, building_type: HKBuildingType, burn_pct: float) -> int:
        """Estimate fire recovery downtime."""
        base = {
            HKBuildingType.RESIDENTIAL_HIGH_RISE: 120,
            HKBuildingType.RESIDENTIAL_WALKUP: 90,
            HKBuildingType.COMMERCIAL_OFFICE: 180,
            HKBuildingType.COMMERCIAL_MALL: 240,
            HKBuildingType.COMMERCIAL_HOTEL: 200,
            HKBuildingType.INDUSTRIAL_FACTORY: 150,
            HKBuildingType.INDUSTRIAL_WAREHOUSE: 120,
        }.get(building_type, 90)
        
        burn_factor = 0.5 + (burn_pct / 100)
        return int(base * burn_factor)
    
    def _hk_relocation_cost(self, building_type: HKBuildingType, affected_floors: int, value_hkd: float) -> float:
        """Estimate temporary relocation costs."""
        if building_type not in [HKBuildingType.RESIDENTIAL_HIGH_RISE, HKBuildingType.RESIDENTIAL_WALKUP]:
            return 0.0
        
        monthly_rate = 0.005  # 0.5% of value per month
        months = max(1, affected_floors // 2)
        return value_hkd * monthly_rate * months
    
    def _hk_business_interruption(self, building_type: HKBuildingType, downtime_days: int, value_hkd: float) -> float:
        """Estimate business interruption costs."""
        daily_rate = {
            HKBuildingType.RESIDENTIAL_HIGH_RISE: 0.0003,
            HKBuildingType.COMMERCIAL_OFFICE: 0.001,
            HKBuildingType.COMMERCIAL_MALL: 0.002,
            HKBuildingType.COMMERCIAL_HOTEL: 0.003,
            HKBuildingType.INDUSTRIAL_FACTORY: 0.0015,
            HKBuildingType.INDUSTRIAL_WAREHOUSE: 0.001,
        }.get(building_type, 0.0005)
        
        return value_hkd * daily_rate * downtime_days

