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

__all__ = [
    # Hazard modules
    "HazardAssessment",
    "RegionalHazardData",
    
    # Financial modules
    "ClimateVasicek",
    "PortfolioRiskCalculator",
    "ClimateVasicekHK",
    "HKD",
    "USD",
    "CNY",
    "load_hk_financial_params",
    
    # Simulation modules
    "MonteCarloEngine",
    "ScenarioGenerator",
    "SimulationConfig",
    "PortfolioAsset",
    "ScenarioFramework",
    "get_framework"
]
