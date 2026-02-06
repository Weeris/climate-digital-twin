"""
Monte Carlo Simulation Module

Portfolio-level risk simulation engine for climate risk assessment.

Features:
- Multi-factor Monte Carlo simulation
- Climate scenario projections
- VaR and Expected Shortfall calculations
- Portfolio value distribution analysis
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
import numpy as np
import pandas as pd


@dataclass
class PortfolioAsset:
    """Individual asset in portfolio."""
    asset_id: str
    value: float
    asset_type: str  # residential, commercial, industrial
    region: str
    base_pd: float = 0.02
    base_lgd: float = 0.4
    climate_beta: float = 0.5
    damage_ratio: float = 0.0  # Pre-calculated damage from hazard


@dataclass
class SimulationConfig:
    """Monte Carlo simulation configuration."""
    n_simulations: int = 10000
    time_horizon: int = 10  # years
    confidence_level: float = 0.95
    random_seed: int = 42
    correlation_factor: float = 0.3
    climate_correlation: float = 0.25


class MonteCarloEngine:
    """
    Monte Carlo simulation engine for portfolio risk assessment.
    
    Simulates portfolio value distributions under various
    climate scenarios, providing risk metrics and loss distributions.
    """
    
    def __init__(self, config: SimulationConfig = None):
        """
        Initialize Monte Carlo engine.
        
        Args:
            config: Simulation configuration
        """
        self.config = config or SimulationConfig()
        np.random.seed(self.config.random_seed)
    
    def run_simulation(
        self,
        assets: List[PortfolioAsset],
        climate_factor: float = 0.1,
        hazard_type: str = "flood"
    ) -> Dict:
        """
        Run Monte Carlo simulation for portfolio.
        
        Args:
            assets: List of portfolio assets
            climate_factor: Climate stress factor (0.0 to 1.0)
            hazard_type: Type of climate hazard
            
        Returns:
            Simulation results dictionary
        """
        n_assets = len(assets)
        n_steps = self.config.time_horizon * 252  # Daily steps
        
        # Initialize portfolio value paths
        portfolio_values = np.zeros((self.config.n_simulations, n_steps + 1))
        portfolio_values[:, 0] = self._get_total_value(assets)
        
        # Initialize individual asset paths
        asset_values = {}
        for asset in assets:
            asset_values[asset.asset_id] = np.zeros(
                (self.config.n_simulations, n_steps + 1)
            )
            asset_values[asset.asset_id][:, 0] = asset.value
        
        # Correlation matrix for multi-factor simulation
        corr_matrix = self._build_correlation_matrix(n_assets)
        
        try:
            L = np.linalg.cholesky(corr_matrix)
        except np.linalg.LinAlgError:
            # Fallback to identity if correlation matrix is singular
            L = np.eye(n_assets)
        
        # Generate random shocks
        dt = 1 / 252
        
        for step in range(1, n_steps + 1):
            # Generate correlated random shocks
            z = np.random.randn(self.config.n_simulations, n_assets)
            correlated_shocks = L @ z.T  # Shape: (n_assets, n_simulations)
            
            for i, asset in enumerate(assets):
                # Time factor (risk accumulates over time)
                time_factor = np.sqrt(step / n_steps)
                
                # Climate shock
                climate_shock = np.random.randn(self.config.n_simulations)
                climate_effect = (
                    climate_factor *
                    self.config.climate_correlation *
                    time_factor *
                    climate_shock
                )
                
                # Systematic market shock
                market_shock = (
                    correlated_shocks[i, :] *
                    np.sqrt(dt) *
                    0.1 *  # Market volatility
                    time_factor
                )
                
                # Idiosyncratic shock
                idiosyncratic_shock = (
                    correlated_shocks[i, :] *
                    np.sqrt(1 - self.config.correlation_factor) *
                    np.sqrt(dt) *
                    0.05 *
                    np.random.randn(self.config.n_simulations)
                )
                
                # Climate beta effect
                beta_effect = (
                    asset.climate_beta *
                    climate_factor *
                    time_factor *
                    climate_shock
                )
                
                # Total return shock
                total_shock = (
                    market_shock +
                    idiosyncratic_shock +
                    beta_effect -
                    (asset.damage_ratio * climate_factor * time_factor)
                )
                
                # Update asset values
                previous_values = asset_values[asset.asset_id][:, step-1]
                asset_values[asset.asset_id][:, step] = (
                    previous_values *
                    (1 + total_shock)
                )
            
            # Update portfolio values
            for sim in range(self.config.n_simulations):
                portfolio_values[sim, step] = sum(
                    asset_values[a.asset_id][sim, step]
                    for a in assets
                )
        
        # Calculate returns
        initial_values = portfolio_values[:, 0]
        final_values = portfolio_values[:, -1]
        returns = (final_values - initial_values) / initial_values
        
        # Calculate risk metrics
        metrics = self._calculate_risk_metrics(returns, initial_values)
        
        return {
            "simulation_config": {
                "n_simulations": self.config.n_simulations,
                "time_horizon": self.config.time_horizon,
                "confidence_level": self.config.confidence_level,
                "climate_factor": climate_factor,
                "hazard_type": hazard_type
            },
            "initial_value": float(np.mean(initial_values)),
            "final_distribution": {
                "mean": float(np.mean(final_values)),
                "std": float(np.std(final_values)),
                "min": float(np.min(final_values)),
                "max": float(np.max(final_values)),
                "percentile_5": float(np.percentile(final_values, 5)),
                "percentile_25": float(np.percentile(final_values, 25)),
                "percentile_50": float(np.percentile(final_values, 50)),
                "percentile_75": float(np.percentile(final_values, 75)),
                "percentile_95": float(np.percentile(final_values, 95))
            },
            "return_distribution": {
                "mean": float(np.mean(returns)),
                "std": float(np.std(returns)),
                "percentile_5": float(np.percentile(returns, 5)),
                "percentile_25": float(np.percentile(returns, 25)),
                "percentile_50": float(np.percentile(returns, 50)),
                "percentile_75": float(np.percentile(returns, 75)),
                "percentile_95": float(np.percentile(returns, 95))
            },
            "return_distribution_array": returns,  # Raw returns for plotting
            "risk_metrics": metrics,
            "portfolio_paths": portfolio_values,
            "asset_paths": asset_values,
            "n_successful_simulations": self.config.n_simulations
        }
    
    def run_scenario_comparison(
        self,
        assets: List[PortfolioAsset],
        scenarios: Dict[str, float]
    ) -> Dict:
        """
        Run simulation across multiple climate scenarios.
        
        Args:
            assets: List of portfolio assets
            scenarios: Dictionary of scenario_name -> climate_factor
            
        Returns:
            Comparison results for all scenarios
        """
        results = {}
        
        for scenario_name, climate_factor in scenarios.items():
            scenario_result = self.run_simulation(
                assets=assets,
                climate_factor=climate_factor,
                hazard_type=scenario_name
            )
            
            results[scenario_name] = {
                "climate_factor": climate_factor,
                "mean_return": scenario_result["return_distribution"]["mean"],
                "std_return": scenario_result["return_distribution"]["std"],
                "var_5": scenario_result["return_distribution"]["percentile_5"],
                "expected_shortfall": scenario_result["risk_metrics"]["expected_shortfall"],
                "probability_of_loss": scenario_result["risk_metrics"]["probability_of_loss"],
                "probability_of_50pct_loss": scenario_result["risk_metrics"]["probability_of_50pct_loss"],
                "mean_final_value": scenario_result["final_distribution"]["mean"],
                "worst_case_5pct": scenario_result["final_distribution"]["percentile_5"]
            }
        
        return results
    
    def _get_total_value(self, assets: List[PortfolioAsset]) -> float:
        """Calculate total portfolio value."""
        return sum(a.value for a in assets)
    
    def _build_correlation_matrix(self, n_assets: int) -> np.ndarray:
        """
        Build correlation matrix for simulation.
        
        Uses block correlation structure based on asset types.
        """
        if n_assets == 1:
            return np.array([[1.0]])
        
        # Base correlation
        base_corr = self.config.correlation_factor
        
        # Correlation matrix
        corr_matrix = np.ones((n_assets, n_assets)) * (1 - base_corr)
        np.fill_diagonal(corr_matrix, 1.0)
        
        return corr_matrix
    
    def _calculate_risk_metrics(
        self,
        returns: np.ndarray,
        initial_values: np.ndarray
    ) -> Dict:
        """
        Calculate risk metrics from return distribution.
        
        Args:
            returns: Array of portfolio returns
            initial_values: Initial portfolio values
            
        Returns:
            Dictionary of risk metrics
        """
        var_percentile = (1 - self.config.confidence_level) * 100
        es_percentile = 5  # Expected Shortfall at 5%
        
        sorted_returns = np.sort(returns)
        var_idx = int((var_percentile / 100) * len(sorted_returns))
        es_idx = int((es_percentile / 100) * len(sorted_returns))
        
        var_value = sorted_returns[var_idx]
        expected_shortfall = np.mean(sorted_returns[:es_idx])
        
        # Loss thresholds
        prob_loss = np.mean(returns < 0)
        prob_25pct_loss = np.mean(returns < -0.25)
        prob_50pct_loss = np.mean(returns < -0.50)
        prob_75pct_loss = np.mean(returns < -0.75)
        
        # Calculate dollar losses at VaR
        var_dollar = np.abs(var_value) * np.mean(initial_values)
        es_dollar = np.abs(expected_shortfall) * np.mean(initial_values)
        
        # Calculate skewness and kurtosis manually
        n = len(returns)
        mean_r = np.mean(returns)
        std_r = np.std(returns)
        
        if n > 2 and std_r > 0:
            skewness = np.mean(((returns - mean_r) / std_r) ** 3)
        else:
            skewness = 0
        
        if n > 3 and std_r > 0:
            kurtosis = np.mean(((returns - mean_r) / std_r) ** 4) - 3
        else:
            kurtosis = 0
        
        return {
            "value_at_risk": var_value,
            "value_at_risk_dollar": var_dollar,
            "expected_shortfall": expected_shortfall,
            "expected_shortfall_dollar": es_dollar,
            "probability_of_loss": float(prob_loss),
            "probability_of_25pct_loss": float(prob_25pct_loss),
            "probability_of_50pct_loss": float(prob_50pct_loss),
            "probability_of_75pct_loss": float(prob_75pct_loss),
            "confidence_level": self.config.confidence_level,
            "volatility_annualized": float(np.std(returns) * np.sqrt(252)),
            "skewness": float(skewness),
            "kurtosis": float(kurtosis)
        }


class ScenarioGenerator:
    """
    Climate scenario generator for Monte Carlo simulations.
    
    Provides standardized climate scenarios with intensity
    parameters for risk assessment.
    """
    
    # Scenario definitions
    SCENARIOS = {
        "baseline": {
            "name": "Baseline / Current Climate",
            "climate_factor": 0.0,
            "description": "Current climate conditions"
        },
        "moderate": {
            "name": "Moderate Climate Stress",
            "climate_factor": 0.1,
            "description": "Low-to-moderate physical risk impact"
        },
        "significant": {
            "name": "Significant Climate Stress",
            "climate_factor": 0.25,
            "description": "Moderate physical risk impact"
        },
        "severe": {
            "name": "Severe Climate Stress",
            "climate_factor": 0.5,
            "description": "High physical risk scenario"
        },
        "extreme": {
            "name": "Extreme Climate Stress",
            "climate_factor": 0.75,
            "description": "Very high physical risk scenario"
        },
        "catastrophic": {
            "name": "Catastrophic Climate Event",
            "climate_factor": 1.0,
            "description": "Maximum physical risk impact"
        }
    }
    
    def get_scenario(self, scenario_name: str) -> Dict:
        """
        Get climate scenario parameters.
        
        Args:
            scenario_name: Name of scenario
            
        Returns:
            Scenario parameters dictionary
        """
        return self.SCENARIOS.get(scenario_name, self.SCENARIOS["baseline"])
    
    def get_all_scenarios(self) -> Dict:
        """Get all defined scenarios."""
        return self.SCENARIOS
    
    def generate_custom_scenario(
        self,
        name: str,
        climate_factor: float,
        description: str = ""
    ) -> Dict:
        """
        Generate custom scenario.
        
        Args:
            name: Scenario name
            climate_factor: Climate stress factor (0.0 to 1.0)
            description: Scenario description
            
        Returns:
            Custom scenario dictionary
        """
        return {
            "name": name,
            "climate_factor": climate_factor,
            "description": description
        }
    
    def get_hazard_scenarios(self, hazard_type: str) -> Dict:
        """
        Get hazard-specific scenarios.
        
        Args:
            hazard_type: Type of hazard
            
        Returns:
            Dictionary of hazard-specific scenarios
        """
        hazard_scenarios = {
            "flood": {
                "minor": {"climate_factor": 0.05, "description": "Minor flooding"},
                "moderate": {"climate_factor": 0.15, "description": "Moderate flooding"},
                "severe": {"climate_factor": 0.30, "description": "Severe flooding"},
                "extreme": {"climate_factor": 0.50, "description": "100-year flood event"}
            },
            "wildfire": {
                "low": {"climate_factor": 0.05, "description": "Low wildfire risk"},
                "moderate": {"climate_factor": 0.15, "description": "Moderate wildfire season"},
                "high": {"climate_factor": 0.30, "description": "Severe wildfire conditions"},
                "extreme": {"climate_factor": 0.50, "description": "Catastrophic wildfire event"}
            },
            "cyclone": {
                "tropical": {"climate_factor": 0.10, "description": "Tropical storm"},
                "category1": {"climate_factor": 0.20, "description": "Category 1 cyclone"},
                "category3": {"climate_factor": 0.35, "description": "Category 3 cyclone"},
                "category5": {"climate_factor": 0.55, "description": "Category 5 cyclone"}
            },
            "drought": {
                "moderate": {"climate_factor": 0.05, "description": "Moderate drought"},
                "severe": {"climate_factor": 0.15, "description": "Severe drought"},
                "extreme": {"climate_factor": 0.30, "description": "Extreme drought conditions"}
            }
        }
        
        return hazard_scenarios.get(hazard_type, self.SCENARIOS)
