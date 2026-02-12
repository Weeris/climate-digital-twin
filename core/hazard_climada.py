"""
CLIMADA-compatible Impact Functions for climate risk assessment.
Uses CLIMADA's ImpactFunc pattern with HK-specific calibrations.

This module provides:
- Standardized hazard type codes (HazardType enum)
- CLIMADA-compatible impact function classes (ClimadaImpactFunc)
- HK-calibrated impact functions (HKClimadaImpactFunc)
- Collection management (ImpactFuncSet)
- Pre-built HK-specific damage functions

Based on CLIMADA's intensity-MDD-PAA (Mean Damage Degree, Partial Affected Area) pattern.
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Union
from enum import Enum
import warnings


class HazardType(Enum):
    """Standardized hazard type codes matching CLIMADA standards."""
    TC = "TC"  # Tropical Cyclone
    FL = "FL"  # Flood
    WF = "WF"  # Wildfire
    DR = "DR"  # Drought
    LS = "LS"  # Landslide
    EQ = "EQ"  # Earthquake
    WS = "WS"  # Wind Storm


@dataclass
class ClimadaImpactFunc:
    """
    CLIMADA-compatible impact function.
    
    Uses intensity-MDD-PAA (Mean Damage Degree, Partial Affected Area) pattern
    for calculating damage from climate hazards.
    """
    haz_type: str
    func_id: int
    name: str
    intensity_unit: str
    intensity: np.ndarray
    mdd: np.ndarray
    paa: np.ndarray
    
    def __post_init__(self):
        """Validate arrays after initialization."""
        self._validate_arrays()
    
    def _validate_arrays(self):
        """Validate that arrays have matching shapes and valid values."""
        if len(self.intensity) != len(self.mdd) or len(self.intensity) != len(self.paa):
            raise ValueError(
                f"Array length mismatch: intensity={len(self.intensity)}, "
                f"mdd={len(self.mdd)}, paa={len(self.paa)}"
            )
        
        if np.any(self.mdd < 0) or np.any(self.mdd > 1):
            warnings.warn("MDD values should be in range [0, 1]")
        
        if np.any(self.paa < 0) or np.any(self.paa > 1):
            warnings.warn("PAA values should be in range [0, 1]")
        
        if not np.all(np.diff(self.intensity) >= 0):
            warnings.warn("Intensity values should be monotonically increasing")
    
    def calc_mdr(self, intensity_value: float) -> float:
        """
        Calculate Mean Damage Ratio (MDR) at given intensity.
        
        MDR = MDD × PAA (Mean Damage Degree × Partial Affected Area)
        """
        if intensity_value <= self.intensity[0]:
            return 0.0
        
        if intensity_value >= self.intensity[-1]:
            return self.mdd[-1] * self.paa[-1]
        
        idx = np.searchsorted(self.intensity, intensity_value) - 1
        idx = max(0, idx)
        
        i0, i1 = self.intensity[idx], self.intensity[idx + 1]
        m0, m1 = self.mdd[idx] * self.paa[idx], self.mdd[idx + 1] * self.paa[idx + 1]
        
        if i1 - i0 == 0:
            return m0
        
        t = (intensity_value - i0) / (i1 - i0)
        return m0 + t * (m1 - m0)
    
    def calc_impact(self, intensity_value: float, asset_value: float) -> float:
        """Calculate damage in monetary terms."""
        mdr = self.calc_mdr(intensity_value)
        return mdr * asset_value
    
    def validate(self) -> Tuple[bool, List[str]]:
        """Check function validity."""
        issues = []
        
        if not np.all(np.diff(self.mdd) >= -0.001):
            issues.append("MDD should be non-decreasing")
        
        if not np.all(np.diff(self.paa) >= -0.001):
            issues.append("PAA should be non-decreasing")
        
        if not np.all(np.diff(self.intensity) > 0):
            issues.append("Intensity should be strictly increasing")
        
        if np.any(self.mdd < 0) or np.any(self.mdd > 1.001):
            issues.append("MDD values out of bounds [0, 1]")
        
        if np.any(self.paa < 0) or np.any(self.paa > 1.001):
            issues.append("PAA values out of bounds [0, 1]")
        
        return len(issues) == 0, issues
    
    def get_mdr_curve(self) -> Tuple[np.ndarray, np.ndarray]:
        """Get the full MDR curve."""
        mdr = self.mdd * self.paa
        return self.intensity, mdr


@dataclass
class HKClimadaImpactFunc(ClimadaImpactFunc):
    """
    HK-calibrated impact function extending CLIMADA pattern.
    """
    hk_construction_factor: float = 1.0
    hk_zone_adjustment: Dict[str, float] = field(default_factory=dict)
    building_type: str = "residential_high_rise"
    damage_category: str = "standard"
    
    _DEFAULT_ZONE_ADJUSTMENTS = {
        "hk_central": 1.2,
        "hk_kowloon": 1.1,
        "hk_new_territories_west": 1.3,
        "hk_new_territories_east": 0.9,
        "hk_islands": 1.0,
        "default": 1.0,
    }
    
    def __post_init__(self):
        """Initialize with defaults."""
        super().__post_init__()
        if not self.hk_zone_adjustment:
            self.hk_zone_adjustment = self._DEFAULT_ZONE_ADJUSTMENTS.copy()
    
    def calc_mdr(self, intensity_value: float, zone: str = "default") -> float:
        """Calculate MDR with HK zone adjustment."""
        base_mdr = super().calc_mdr(intensity_value)
        adjusted = base_mdr * self.hk_construction_factor
        zone_factor = self.hk_zone_adjustment.get(zone, 1.0)
        adjusted *= zone_factor
        return min(1.0, adjusted)
    
    def calc_impact(self, intensity_value: float, asset_value: float, zone: str = "default") -> float:
        """Calculate damage with HK zone adjustment."""
        mdr = self.calc_mdr(intensity_value, zone)
        return mdr * asset_value
    
    def get_zone_factor(self, zone: str) -> float:
        """Get adjustment factor for a zone."""
        return self.hk_zone_adjustment.get(zone, 1.0)


@dataclass
class ImpactFuncSet:
    """Collection of impact functions by hazard type."""
    functions: Dict[str, Dict[int, ClimadaImpactFunc]] = field(default_factory=dict)
    
    def add_func(self, func: ClimadaImpactFunc) -> None:
        """Add an impact function to the collection."""
        if func.haz_type not in self.functions:
            self.functions[func.haz_type] = {}
        self.functions[func.haz_type][func.func_id] = func
    
    def get_func(self, haz_type: str, func_id: int) -> Optional[ClimadaImpactFunc]:
        """Get an impact function by hazard type and ID."""
        return self.functions.get(haz_type, {}).get(func_id)
    
    def get_funcs_by_type(self, haz_type: str) -> List[ClimadaImpactFunc]:
        """Get all functions for a hazard type."""
        return list(self.functions.get(haz_type, {}).values())
    
    def validate_all(self) -> Tuple[bool, Dict[str, List[str]]]:
        """Validate all functions in the set."""
        issues = {}
        all_valid = True
        
        for haz_type, funcs in self.functions.items():
            for func_id, func in funcs.items():
                is_valid, func_issues = func.validate()
                if not is_valid:
                    all_valid = False
                    key = f"{haz_type}_{func_id}"
                    issues[key] = func_issues
        
        return all_valid, issues
    
    def count(self) -> int:
        """Total number of functions in the set."""
        return sum(len(funcs) for funcs in self.functions.values())
    
    def clear(self) -> None:
        """Remove all functions."""
        self.functions.clear()


# =====================
# HK-SPECIFIC FUNCTIONS
# =====================

def HK_TC_WindDamage(
    building_type: str = "residential_high_rise",
    construction: str = "reinforced_concrete"
) -> HKClimadaImpactFunc:
    """
    Tropical cyclone wind damage function for HK buildings.
    
    Based on Saffir-Simpson scale
    
    Intensity: Wind speed in km/h
    
    Args:
        building_type: Type of HK building
        construction: Construction material/type
        
    Returns:
        HKClimadaImpactFunc for tropical cyclone wind damage
    """
    # Construction factors (lower = more resilient)
    construction_factors = {
        "reinforced_concrete": 0.8,
        "steel_frame": 0.85,
        "glass_curtain_wall": 1.3,
        "masonry": 1.0,
        "composite": 1.1,
        "wood": 1.3,
    }
    
    # Wind speed intensity points (km/h)
    intensity = np.array([0, 63, 100, 119, 154, 178, 209, 252, 300])
    
    # Mean Damage Degree - damage as proportion of exposed items
    mdd = np.array([0.0, 0.05, 0.15, 0.25, 0.40, 0.55, 0.70, 0.85, 0.95])
    
    # Partial Affected Area - proportion of structure exposed
    paa = np.array([0.0, 0.1, 0.25, 0.40, 0.60, 0.75, 0.90, 1.0, 1.0])
    
    # Adjust for construction type
    cf = construction_factors.get(construction, 1.0)
    mdd = np.minimum(1.0, mdd * cf)
    
    return HKClimadaImpactFunc(
        haz_type="TC",
        func_id=1,
        name=f"TC Wind Damage - HK {building_type}",
        intensity_unit="km/h",
        intensity=intensity,
        mdd=mdd,
        paa=paa,
        hk_construction_factor=construction_factors.get(construction, 1.0),
        building_type=building_type,
        damage_category="structural"
    )


def HK_FloodDamage(
    building_type: str = "residential_high_rise",
    floor_count: int = 30
) -> HKClimadaImpactFunc:
    """
    Flood depth-damage function for HK properties.
    
    Accounts for high-rise buildings common in HK where only
    lower floors (under 5) are affected by flooding.
    
    Intensity: Flood depth in meters
    
    Args:
        building_type: Type of HK building
        floor_count: Total number of floors (for high-rise adjustment)
        
    Returns:
        HKClimadaImpactFunc for flood depth-damage
    """
    # Building type factors
    bldg_factors = {
        "residential_high_rise": 0.85,
        "residential_walkup": 1.0,
        "commercial_office": 0.9,
        "commercial_mall": 1.1,
        "commercial_hotel": 0.95,
        "industrial_factory": 1.2,
        "industrial_warehouse": 1.15,
        "infrastructure_mtr": 1.3,
        "infrastructure_tunnel": 1.4,
        "infrastructure_bridge": 1.1,
    }
    
    # High-rise: only lower floors worth 25-30% of building affected
    affected_ratio = min(0.3, 5.0 / floor_count) if floor_count > 5 else 1.0
    
    # Depth intensity points (meters)
    intensity = np.array([0, 0.1, 0.3, 0.5, 1.0, 1.5, 2.0, 3.0, 5.0])
    
    # Mean Damage Degree
    mdd = np.array([0.0, 0.08, 0.20, 0.30, 0.50, 0.65, 0.75, 0.90, 1.0])
    
    # Partial Affected Area - flood affects exposed area
    paa = np.array([0.0, 0.25, 0.45, 0.60, 0.75, 0.85, 0.95, 1.0, 1.0])
    
    # Apply building type factor and high-rise adjustment
    factor = bldg_factors.get(building_type, 1.0)
    mdd = np.minimum(1.0, mdd * factor * affected_ratio)
    
    zone_adjustments = {
        "hk_central": 1.2,
        "hk_kowloon": 1.1,
        "hk_new_territories_west": 1.35,
        "hk_new_territories_east": 0.9,
        "hk_islands": 1.05,
        "default": 1.0,
    }
    
    return HKClimadaImpactFunc(
        haz_type="FL",
        func_id=1,
        name=f"Flood Depth-Damage - HK {building_type}",
        intensity_unit="m",
        intensity=intensity,
        mdd=mdd,
        paa=paa,
        hk_construction_factor=factor,
        hk_zone_adjustment=zone_adjustments,
        building_type=building_type,
        damage_category="water"
    )


def HK_FireDamage(
    building_type: str = "residential_high_rise",
    fire_rating: str = "standard"
) -> HKClimadaImpactFunc:
    """
    Wildfire/fire damage function for HK buildings.
    
    Accounts for fire spread potential and building density
    common in Hong Kong's dense urban environment.
    
    Intensity: Percentage of structure burned (0-100%)
    
    Args:
        building_type: Type of HK building
        fire_rating: Fire resistance rating
        
    Returns:
        HKClimadaImpactFunc for fire damage
    """
    # Fire resistance factors (lower = better resistance)
    resistance_factors = {
        "pre_1960": 1.3,
        "1960_1980": 1.15,
        "1980_2000": 1.0,
        "post_2000": 0.9,
        "premium": 0.8,
        "standard": 1.0,
    }
    
    # Building spread factors (higher in dense areas)
    spread_factors = {
        "residential_high_rise": 0.8,
        "residential_walkup": 1.2,
        "commercial_office": 0.7,
        "commercial_mall": 0.9,
        "commercial_hotel": 0.85,
        "industrial_factory": 1.0,
        "industrial_warehouse": 1.1,
    }
    
    # Burn percentage intensity points (0-100%)
    intensity = np.array([0, 10, 25, 50, 75, 100])
    
    # Mean Damage Degree - structural damage increases with burn
    mdd = np.array([0.0, 0.10, 0.30, 0.60, 0.85, 1.0])
    
    # Partial Affected Area - smoke affects more than burn
    paa = np.array([0.0, 0.30, 0.55, 0.80, 0.95, 1.0])
    
    # Apply factors
    rf = resistance_factors.get(fire_rating, 1.0)
    sf = spread_factors.get(building_type, 1.0)
    
    # Dense urban environment - spread risk higher
    hk_urban_factor = 1.15
    
    mdd = np.minimum(1.0, mdd * rf * sf * hk_urban_factor)
    
    return HKClimadaImpactFunc(
        haz_type="WF",
        func_id=1,
        name=f"Fire Damage - HK {building_type}",
        intensity_unit="%",
        intensity=intensity,
        mdd=mdd,
        paa=paa,
        hk_construction_factor=rf * hk_urban_factor,
        building_type=building_type,
        damage_category="fire"
    )


def HK_DroughtDamage(
    building_type: str = "agricultural"
) -> HKClimadaImpactFunc:
    """
    Drought impact function for HK (primarily agricultural).
    
    Hong Kong has limited agriculture but the New Territories
    have farming that can be affected by drought.
    
    Intensity: Soil Moisture Deficit (SMD) in % deviation from normal,
    or alternatively Standardized Precipitation Index (SPI)
    
    Args:
        building_type: Type of land use (agricultural affected most)
        
    Returns:
        HKClimadaImpactFunc for drought damage
    """
    # Drought intensity - SPI index (negative = dry)
    # -0.5 to 0.5 = normal, -1.0 to -0.5 = dry, -1.5 to -1.0 = very dry, <-1.5 = extreme
    intensity = np.array([-2.0, -1.5, -1.0, -0.5, 0.0])
    
    # For agricultural: high impact
    if building_type in ["agricultural", "farm", "nursery"]:
        mdd = np.array([0.80, 0.60, 0.35, 0.15, 0.0])
    # For residential/commercial: low impact (utility costs, ecosystem)
    elif building_type in ["residential_high_rise", "commercial_office"]:
        mdd = np.array([0.15, 0.10, 0.05, 0.02, 0.0])
    # Other
    else:
        mdd = np.array([0.40, 0.30, 0.15, 0.05, 0.0])
    
    # Affected area - drought impacts entire zone/district
    paa = np.array([1.0, 1.0, 0.75, 0.50, 0.0])
    
    zone_adjustments = {
        "hk_new_territories_west": 1.2,  # More farming here
        "hk_new_territories_east": 1.0,
        "hk_islands": 0.8,
        "hk_kowloon": 0.5,  # Minimal agriculture
        "hk_central": 0.3,
        "default": 0.7,
    }
    
    return HKClimadaImpactFunc(
        haz_type="DR",
        func_id=1,
        name=f"Drought Impact - HK {building_type}",
        intensity_unit="SPI",
        intensity=intensity,
        mdd=mdd,
        paa=paa,
        hk_construction_factor=1.0,
        hk_zone_adjustment=zone_adjustments,
        building_type=building_type,
        damage_category="agricultural"
    )


# =====================
# FACTORY FUNCTIONS
# =====================

def create_default_funcset() -> ImpactFuncSet:
    """
    Create a default ImpactFuncSet with HK-standard functions.
    
    Returns:
        ImpactFuncSet with all standard HK hazard functions
    """
    funcset = ImpactFuncSet()
    
    # Add TC functions for different building types
    for bldg_type in ["residential_high_rise", "commercial_office", "industrial_factory"]:
        funcset.add_func(HK_TC_WindDamage(building_type=bldg_type))
    
    # Add flood functions
    for bldg_type in ["residential_high_rise", "residential_walkup", "commercial_office", "infrastructure_mtr"]:
        funcset.add_func(HK_FloodDamage(building_type=bldg_type))
    
    # Add fire functions
    funcset.add_func(HK_FireDamage(building_type="residential_high_rise"))
    funcset.add_func(HK_FireDamage(building_type="residential_walkup"))
    
    # Add drought functions for agricultural areas
    funcset.add_func(HK_DroughtDamage(building_type="agricultural"))
    funcset.add_func(HK_DroughtDamage(building_type="residential_high_rise"))
    
    return funcset