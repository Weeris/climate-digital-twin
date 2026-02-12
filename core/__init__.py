"""
Core Module - Climate Digital Twin

Hazard, financial, and simulation components.
"""

from .hazard import HazardAssessment, RegionalHazardData
from .financial import (
    ClimateVasicek, 
    PortfolioRiskCalculator, 
    ClimateVasicekHK,
    HKD, USD, CNY,
    load_hk_financial_params
)
from .simulation import MonteCarloEngine, ScenarioGenerator, SimulationConfig, PortfolioAsset
from .scenarios import ScenarioFramework, get_framework
from .hk_regional_data import HKRegionalHazardData, HKHazardZone, HKFloodParameters, HKTyphoonParameters, HKWildfireParameters, HKDroughtParameters, get_hk_zone_for_location
from .hk_financial import HKFinancialModel, HKCurrency, HKPropertyTax, HKMortgage
from .hk_insurance import HKInsuranceCalculator, LossRatio, Deductible
from .hk_reports import HKReportGenerator, PortfolioAnalysis

__all__ = [
    # Hazard modules
    "HazardAssessment",
    "RegionalHazardData",
    "HKRegionalHazardData",
    "HKHazardZone",
    "HKFloodParameters",
    "HKTyphoonParameters",
    "HKWildfireParameters",
    "HKDroughtParameters",
    "get_hk_zone_for_location",
    
    # Financial modules
    "ClimateVasicek",
    "PortfolioRiskCalculator",
    "ClimateVasicekHK",
    "HKD",
    "USD",
    "CNY",
    "load_hk_financial_params",
    
    # HK Financial modules
    "HKFinancialModel",
    "HKCurrency",
    "HKPropertyTax",
    "HKMortgage",
    
    # Insurance modules
    "HKInsuranceCalculator",
    "LossRatio",
    "Deductible",
    
    # Report modules
    "HKReportGenerator",
    "PortfolioAnalysis",
    
    # Simulation modules
    "MonteCarloEngine",
    "ScenarioGenerator",
    "SimulationConfig",
    "PortfolioAsset",
    "ScenarioFramework",
    "get_framework"
]
