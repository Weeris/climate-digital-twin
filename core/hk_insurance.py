"""
HK Insurance Loss Module

Insurance loss calculations for HK property portfolios.
Provides premium calculation, claims analysis, deductible structures,
and loss ratio estimation by hazard type.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import json
from pathlib import Path


# Constants
DATA_DIR = Path(__file__).parent.parent / "data"
PARAMS_FILE = DATA_DIR / "hk_financial_params.json"


def load_insurance_params() -> Dict:
    """Load insurance parameters from JSON file."""
    if PARAMS_FILE.exists():
        with open(PARAMS_FILE, 'r') as f:
            return json.load(f)
    return {}


@dataclass
class LossRatio:
    """Insurance loss ratio parameters by hazard type."""
    flood_min: float = 0.45
    flood_max: float = 0.65
    flood_typical: float = 0.55
    
    typhoon_min: float = 0.35
    typhoon_max: float = 0.55
    typhoon_typical: float = 0.45
    
    fire_min: float = 0.25
    fire_max: float = 0.45
    fire_typical: float = 0.35
    
    combined_min: float = 0.40
    combined_max: float = 0.60
    combined_typical: float = 0.50
    
    def get_ratio(self, hazard_type: str, severity: str = "typical") -> float:
        """Get loss ratio for a hazard type."""
        ratios = {
            "flood": (self.flood_min, self.flood_max, self.flood_typical),
            "typhoon": (self.typhoon_min, self.typhoon_max, self.typhoon_typical),
            "fire": (self.fire_min, self.fire_max, self.fire_typical),
            "combined": (self.combined_min, self.combined_max, self.combined_typical)
        }
        
        min_r, max_r, typ_r = ratios.get(hazard_type, (0.3, 0.6, 0.45))
        
        if severity == "min":
            return min_r
        elif severity == "max":
            return max_r
        else:
            return typ_r


@dataclass
class Deductible:
    """Deductible structure for HK policies."""
    standard_deductible_hkd: float = 5000
    percentage_deductible: float = 0.01
    typhoon_deductible_pct: float = 0.05
    flood_deductible_pct: float = 0.03
    
    def calculate(self, sum_insured: float, 
                  hazard_type: str = "standard") -> float:
        """Calculate deductible amount."""
        if hazard_type == "typhoon":
            pct = self.typhoon_deductible_pct
        elif hazard_type == "flood":
            pct = self.flood_deductible_pct
        else:
            pct = self.percentage_deductible
        
        pct_deductible = sum_insured * pct
        return max(self.standard_deductible_hkd, pct_deductible)


@dataclass
class CoverageLimit:
    """Coverage limit structure."""
    residential_apartment: float = 10000000
    residential_house: float = 50000000
    commercial_office: float = 200000000
    commercial_retail: float = 100000000
    industrial: float = 150000000
    
    def get_limit(self, property_type: str) -> float:
        """Get typical coverage limit for property type."""
        limits = {
            "residential_apartment": self.residential_apartment,
            "residential_house": self.residential_house,
            "commercial_office": self.commercial_office,
            "commercial_retail": self.commercial_retail,
            "industrial": self.industrial
        }
        return limits.get(property_type, 10000000)


@dataclass
class DistrictInsuranceRate:
    """District-level insurance rate parameters."""
    base_premium_rate: float = 0.0015
    typhoon_factor: float = 1.2
    flood_factor: float = 1.0
    fire_factor: float = 1.1


class HKInsuranceRates:
    """HK district-level insurance premium rates."""
    
    def __init__(self):
        self.rates = {
            "hong_kong_island": {
                "central": DistrictInsuranceRate(base_premium_rate=0.0015, typhoon_factor=1.2, flood_factor=1.0),
                "admiralty": DistrictInsuranceRate(base_premium_rate=0.0014, typhoon_factor=1.2, flood_factor=1.0),
                "wan_chai": DistrictInsuranceRate(base_premium_rate=0.0016, typhoon_factor=1.3, flood_factor=1.1),
                "causeway_bay": DistrictInsuranceRate(base_premium_rate=0.0017, typhoon_factor=1.3, flood_factor=1.1),
                "southern": DistrictInsuranceRate(base_premium_rate=0.0013, typhoon_factor=1.4, flood_factor=0.9)
            },
            "kowloon": {
                "tst": DistrictInsuranceRate(base_premium_rate=0.0018, typhoon_factor=1.4, flood_factor=1.3),
                "hung_hom": DistrictInsuranceRate(base_premium_rate=0.0017, typhoon_factor=1.3, flood_factor=1.4),
                "kowloon_tong": DistrictInsuranceRate(base_premium_rate=0.0015, typhoon_factor=1.2, flood_factor=1.1)
            },
            "new_territories": {
                "sha_tin": DistrictInsuranceRate(base_premium_rate=0.0014, typhoon_factor=1.1, flood_factor=1.2),
                "tuen_mun": DistrictInsuranceRate(base_premium_rate=0.0015, typhoon_factor=1.2, flood_factor=1.4),
                "yuen_long": DistrictInsuranceRate(base_premium_rate=0.0016, typhoon_factor=1.3, flood_factor=1.5)
            }
        }
    
    def get_rate(self, district: str) -> DistrictInsuranceRate:
        """Get insurance rate for a district."""
        district_lower = district.lower().replace(" ", "_")
        for region_data in self.rates.values():
            if district_lower in region_data:
                return region_data[district_lower]
        return DistrictInsuranceRate()


class HKInsuranceCalculator:
    """Main HK Insurance Loss Calculator."""
    
    def __init__(self):
        self.loss_ratios = LossRatio()
        self.deductible = Deductible()
        self.coverage_limits = CoverageLimit()
        self.rates = HKInsuranceRates()
    
    def calculate_premium(
        self,
        sum_insured: float,
        district: str,
        hazards: List[str] = None
    ) -> Dict:
        """Calculate insurance premium for a property."""
        if hazards is None:
            hazards = ["typhoon", "flood", "fire"]
        
        rate = self.rates.get_rate(district)
        base_premium = sum_insured * rate.base_premium_rate
        
        hazard_factors = {
            "typhoon": rate.typhoon_factor,
            "flood": rate.flood_factor,
            "fire": rate.fire_factor
        }
        
        hazard_premium = 0
        for hazard in hazards:
            factor = hazard_factors.get(hazard, 1.0)
            hazard_premium += base_premium * (factor - 1)
        
        total_premium = base_premium + hazard_premium
        
        return {
            "base_premium": base_premium,
            "hazard_premium": hazard_premium,
            "total_premium": total_premium,
            "premium_rate": total_premium / sum_insured,
            "district": district,
            "hazards_covered": hazards
        }
    
    def calculate_claim(
        self,
        damage_amount: float,
        sum_insured: float,
        hazard_type: str = "standard"
    ) -> Dict:
        """Calculate insurance claim after deductible."""
        deductible = self.deductible.calculate(sum_insured, hazard_type)
        claimable = max(0, damage_amount - deductible)
        actual_claim = min(claimable, sum_insured)
        
        return {
            "damage_amount": damage_amount,
            "deductible": deductible,
            "claim_before_limit": claimable,
            "actual_claim": actual_claim,
            "shortfall": max(0, damage_amount - actual_claim - deductible)
        }
    
    def calculate_expected_loss(
        self,
        damage_ratio: float,
        sum_insured: float,
        hazard_type: str
    ) -> Dict:
        """Calculate expected loss based on damage ratio."""
        loss_ratio = self.loss_ratios.get_ratio(hazard_type)
        expected_damage = sum_insured * damage_ratio * loss_ratio