"""
HK Financial Risk Module

HK-specific financial parameters and calculations for climate risk modeling.
Provides HKD currency support, property tax calculations, mortgage parameters,
and HK insurance integration.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import json
from pathlib import Path


# Constants
DATA_DIR = Path(__file__).parent.parent / "data"
PARAMS_FILE = DATA_DIR / "hk_financial_params.json"


def load_hk_params() -> Dict:
    """Load HK financial parameters from JSON file."""
    if PARAMS_FILE.exists():
        with open(PARAMS_FILE, 'r') as f:
            return json.load(f)
    return {}


@dataclass
class HKCurrency:
    """HKD currency parameters."""
    code: str = "HKD"
    symbol: str = "$"
    exchange_rate_usd: float = 7.75
    exchange_rate_cny: float = 1.10
    
    def to_usd(self, hkd: float) -> float:
        """Convert HKD to USD."""
        return hkd / self.exchange_rate_usd
    
    def to_cny(self, hkd: float) -> float:
        """Convert HKD to CNY."""
        return hkd / self.exchange_rate_cny
    
    def format(self, amount: float) -> str:
        """Format amount with HKD symbol."""
        return f"{self.symbol}{amount:,.2f}"


@dataclass
class HKPropertyTax:
    """Hong Kong property tax parameters."""
    bsd_rate: float = 0.15  # Buyer Stamp Duty
    avd_tiers: List[Tuple[float, float]] = None
    stamp_duty_tiers: List[Tuple[float, float]] = None
    
    def __post_init__(self):
        if self.avd_tiers is None:
            self.avd_tiers = [
                (2000000, 0.15),
                (4500000, 0.20),
                (9000000, 0.25),
                (float('inf'), 0.30)
            ]
        if self.stamp_duty_tiers is None:
            self.stamp_duty_tiers = [
                (2000000, 0.01),
                (4500000, 0.02),
                (9000000, 0.03),
                (float('inf'), 0.04)
            ]
    
    def calculate_bsd(self, price: float, is_resident: bool = False) -> float:
        """
        Calculate Buyer Stamp Duty.
        
        Args:
            price: Property price in HKD
            is_resident: True if HK permanent resident
            
        Returns:
            BSD amount
        """
        if is_resident:
            return 0.0
        return price * self.bsd_rate
    
    def calculate_avd(self, price: float) -> float:
        """
        Calculate Additional Valuation Duty (progressive).
        
        Args:
            price: Property price in HKD
            
        Returns:
            AVD amount
        """
        avd = 0.0
        remaining = price
        
        thresholds = [0] + [t[0] for t in self.avd_tiers[:-1]]
        rates = [t[1] for t in self.avd_tiers]
        
        for i in range(len(thresholds)):
            tier_min = thresholds[i]
            tier_max = self.avd_tiers[i][0] if i < len(self.avd_tiers) else float('inf')
            rate = rates[i]
            
            if remaining <= 0:
                break
            
            tier_amount = min(remaining, tier_max - tier_min)
            avd += tier_amount * rate
            remaining -= tier_amount
        
        return avd
    
    def calculate_stamp_duty(self, price: float) -> float:
        """
        Calculate standard stamp duty (progressive).
        
        Args:
            price: Property price in HKD
            
        Returns:
            Stamp duty amount
        """
        duty = 0.0
        remaining = price
        
        thresholds = [0] + [t[0] for t in self.stamp_duty_tiers[:-1]]
        rates = [t[1] for t in self.stamp_duty_tiers]
        
        for i in range(len(thresholds)):
            tier_min = thresholds[i]
            tier_max = self.stamp_duty_tiers[i][0] if i < len(self.stamp_duty_tiers) else float('inf')
            rate = rates[i]
            
            if remaining <= 0:
                break
            
            tier_amount = min(remaining, tier_max - tier_min)
            duty += tier_amount * rate
            remaining -= tier_amount
        
        return duty


@dataclass
class HKMortgage:
    """Hong Kong mortgage parameters."""
    prime_rate: float = 0.05875
    ltv_max_residential: float = 0.70
    ltv_max_commercial: float = 0.60
    dsr_minimum: float = 0.50
    stress_test_add: float = 0.03
    
    def calculate_max_loan(self, property_value: float, 
                           property_type: str = "residential") -> float:
        """
        Calculate maximum mortgage loan amount.
        
        Args:
            property_value: Property value in HKD
            property_type: residential, commercial, industrial
            
        Returns:
            Maximum loan amount
        """
        ltv = {
            "residential": self.ltv_max_residential,
            "commercial": self.ltv_max_commercial,
            "industrial": self.ltv_max_commercial
        }.get(property_type, self.ltv_max_residential)
        
        return property_value * ltv
    
    def calculate_stress_rate(self) -> float:
        """Calculate stressed interest rate for stress testing."""
        return self.prime_rate + self.stress_test_add


@dataclass
class HKPropertyManagement:
    """HK property management fee parameters."""
    residential_rates: Dict[str, float] = None
    commercial_rates: Dict[str, float] = None
    
    def __post_init__(self):
        self.residential_rates = {
            "luxury": 5.00,
            "medium": 3.50,
            "basic": 2.50
        }
        self.commercial_rates = {
            "office_grade_a": 8.00,
            "office_grade_b": 6.00,
            "retail": 10.00
        }
    
    def calculate_monthly_fee(self, area_sqft: float, 
                              property_type: str,
                              grade: str = "medium") -> float:
        """
        Calculate monthly property management fee.
        
        Args:
            area_sqft: Property area in square feet
            property_type: residential, commercial
            grade: grade of property
            
        Returns:
            Monthly fee in HKD
        """
        if property_type == "residential":
            rate = self.residential_rates.get(grade, 3.50)
        else:
            rate = self.commercial_rates.get(grade, 6.00)
        
        return area_sqft * rate


class HKFinancialModel:
    """
    Main HK Financial Risk Model class.
    
    Integrates all HK-specific financial parameters for
    climate risk assessment.
    """
    
    def __init__(self, params_file: str = None):
        """
        Initialize HK Financial Model.
        
        Args:
            params_file: Optional path to parameters JSON file
        """
        self.currency = HKCurrency()
        self.tax = HKPropertyTax()
        self.mortgage = HKMortgage()
        self.management = HKPropertyManagement()
        
        # Load additional params if provided
        if params_file:
            with open(params_file, 'r') as f:
                params = json.load(f)
                if 'currency' in params:
                    self.currency = HKCurrency(**params['currency'])
    
    def calculate_total_acquisition_cost(
        self,
        price: float,
        is_resident: bool = True,
        property_type: str = "residential"
    ) -> Dict:
        """
        Calculate total property acquisition cost.
        
        Args:
            price: Property price in HKD
            is_resident: Buyer is HK permanent resident
            property_type: residential, commercial
            
        Returns:
            Dictionary with cost breakdown
        """
        bsd = self.tax.calculate_bsd(price, is_resident)
        avd = self.tax.calculate_avd(price)
        stamp_duty = self.tax.calculate_stamp_duty(price)
        total_tax = bsd + avd + stamp_duty
        
        return {
            "property_price": price,
            "bsd": bsd,
            "avd": avd,
            "stamp_duty": stamp_duty,
            "total_tax": total_tax,
            "total_acquisition_cost": price + total_tax
        }
    
    def calculate_mortgage_impact(
        self,
        property_value: float,
        damage_ratio: float,
        property_type: str = "residential"
    ) -> Dict:
        """
        Calculate impact of climate damage on mortgage.
        
        Args:
            property_value: Property value in HKD
            damage_ratio: Physical damage ratio
            property_type: residential, commercial
            
        Returns:
            Mortgage impact analysis
        """
        max_loan = self.mortgage.calculate_max_loan(property_value, property_type)
        ltv = max_loan / property_value if property_value > 0 else 0
        
        # Stressed LTV after damage
        damaged_value = property_value * (1 - damage_ratio)
        stressed_ltv = max_loan / damaged_value if damaged_value > 0 else 0
        
        return {
            "property_value": property_value,
            "max_loan": max_loan,
            "original_ltv": ltv,
            "damaged_value": damaged_value,
            "stressed_ltv": stressed_ltv,
            "ltv_change": stressed_ltv - ltv,
            "stress_rate": self.mortgage.calculate_stress_rate()
        }