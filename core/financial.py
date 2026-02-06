"""
Financial Risk Module

Provides credit risk calculations with climate risk adjustments:
- Extended Vasicek model implementation
- Expected Loss (EL) calculations
- Unexpected Loss (UL) calculations
- Capital adequacy assessment
"""

from typing import Dict, Tuple
import numpy as np
from dataclasses import dataclass


@dataclass
class CreditRiskInput:
    """Input parameters for credit risk calculation."""
    exposure: float                    # EAD (Exposure at Default)
    base_pd: float                     # Probability of Default (baseline)
    base_lgd: float                    # Loss Given Default (baseline)
    maturity: int = 5                  # Years to maturity
    correlation: float = 0.3           # Asset correlation


@dataclass
class ClimateRiskAdjustment:
    """Climate risk adjustment parameters."""
    climate_factor: float              # Physical damage ratio
    climate_beta: float = 0.5          # Climate sensitivity coefficient
    pd_multiplier: float = 1.0         # Custom PD multiplier
    lgd_multiplier: float = 1.0       # Custom LGD multiplier


class ClimateVasicek:
    """
    Extended Vasicek Model for Climate-Adjusted Credit Risk.
    
    Implements an extended version of the one-factor Vasicek model
    commonly used in internal credit risk models (Basel IRB).
    
    Climate Risk Extension:
    - Physical risk manifests as an additional stochastic factor
    - Adjusts Probability of Default (PD) based on climate exposure
    - Adjusts Loss Given Default (LGD) based on collateral damage
    
    Model Equation:
        PD_climate = PD_base × (1 + β_climate × ClimateFactor × Z)
    
    Where:
        - β_climate: Climate sensitivity coefficient
        - ClimateFactor: Physical damage ratio from hazard
        - Z: Climate shock (standard normal)
    """
    
    def __init__(
        self,
        base_pd: float = 0.02,
        base_lgd: float = 0.4,
        climate_beta: float = 0.5,
        correlation: float = 0.3,
        recovery_rate: float = None
    ):
        """
        Initialize Extended Vasicek model.
        
        Args:
            base_pd: Baseline Probability of Default
            base_lgd: Baseline Loss Given Default
            climate_beta: Climate sensitivity coefficient (0.0 to 1.0)
            correlation: Asset correlation (Basel default: 0.3)
            recovery_rate: Recovery rate (derived from LGD if not provided)
        """
        self.base_pd = base_pd
        self.base_lgd = base_lgd
        self.climate_beta = climate_beta
        self.correlation = correlation
        self.recovery_rate = recovery_rate or (1.0 - base_lgd)
        
        # Vasicek model parameters
        self.speed_of_mean_reversion = 0.05  # κ (kappa)
        self.long_run_mean = base_pd         # θ (theta)
        self.volatility = 0.12              # σ (sigma for PD)
        
        # Correlation between systematic and climate factors
        self.climate_correlation = 0.25
    
    def calculate_climate_adjustment(
        self,
        physical_damage_ratio: float,
        pd_increase_cap: float = 3.0,
        lgd_increase_cap: float = 1.5
    ) -> Dict:
        """
        Calculate climate risk adjustments.
        
        Args:
            physical_damage_ratio: Ratio of physical damage (0.0 to 1.0)
            pd_increase_cap: Maximum PD multiplier
            lgd_increase_cap: Maximum LGD multiplier
            
        Returns:
            Dictionary with adjustment factors
        """
        # PD increases with physical damage
        # Using climate_beta as sensitivity
        pd_multiplier = 1.0 + self.climate_beta * physical_damage_ratio
        pd_multiplier = min(pd_increase_cap, pd_multiplier)
        
        # LGD increases as collateral is damaged
        lgd_multiplier = 1.0 + 0.5 * physical_damage_ratio
        lgd_multiplier = min(lgd_increase_cap, lgd_multiplier)
        
        # Climate factor for use in simulations
        climate_factor = self.climate_beta * physical_damage_ratio
        
        return {
            "pd_multiplier": pd_multiplier,
            "lgd_multiplier": lgd_multiplier,
            "climate_factor": climate_factor,
            "adjusted_pd": self.base_pd * pd_multiplier,
            "adjusted_lgd": min(1.0, self.base_lgd * lgd_multiplier)
        }
    
    def calculate_adjusted_pd_monte_carlo(
        self,
        time_horizon: int,
        climate_factor: float,
        n_simulations: int = 10000,
        random_seed: int = 42
    ) -> Dict:
        """
        Calculate climate-adjusted PD distribution using Monte Carlo.
        
        Simulates future PD paths under climate stress conditions.
        
        Args:
            time_horizon: Analysis horizon in years
            climate_factor: Climate impact factor
            n_simulations: Number of Monte Carlo paths
            random_seed: Random seed for reproducibility
            
        Returns:
            Dictionary with PD distribution statistics
        """
        np.random.seed(random_seed)
        
        dt = 1 / 252  # Daily time step
        n_steps = time_horizon * 252
        
        # Correlation matrix between systematic and climate factors
        corr_matrix = np.array([
            [1.0, self.climate_correlation],
            [self.climate_correlation, 1.0]
        ])
        L = np.linalg.cholesky(corr_matrix)
        
        # Initialize arrays
        pd_paths = np.zeros((n_simulations, n_steps + 1))
        pd_paths[:, 0] = self.base_pd
        
        # Cholesky decomposition for correlated Brownian motions
        climate_shocks = np.zeros((n_simulations, n_steps + 1))
        
        # Simulate paths
        for t in range(1, n_steps + 1):
            # Generate correlated random shocks
            z = np.random.randn(n_simulations, 2)
            w = L @ z.T  # Shape: (2, n_simulations)
            
            # Climate factor evolution (mean-reverting)
            climate_shocks[:, t] = (
                climate_shocks[:, t-1] +
                self.speed_of_mean_reversion *
                (0 - climate_shocks[:, t-1]) * dt +
                np.sqrt(dt) * w[1, :]
            )
            
            # Climate effect on PD
            climate_effect = self.climate_beta * (
                climate_factor + climate_shocks[:, t]
            )
            
            # Vasicek dynamics with climate adjustment
            pd_paths[:, t] = (
                pd_paths[:, t-1] +
                self.speed_of_mean_reversion *
                (self.long_run_mean - pd_paths[:, t-1]) * dt +
                np.sqrt(dt) * self.volatility * w[0, :] +
                climate_effect
            )
            
            # Ensure PD stays within bounds
            pd_paths[:, t] = np.clip(pd_paths[:, t], 0.0001, 0.9999)
        
        # Final PD values
        final_pd = pd_paths[:, -1]
        
        return {
            "base_pd": self.base_pd,
            "adjusted_pd_distribution": final_pd,
            "mean": float(np.mean(final_pd)),
            "std": float(np.std(final_pd)),
            "percentile_5": float(np.percentile(final_pd, 5)),
            "percentile_25": float(np.percentile(final_pd, 25)),
            "percentile_50": float(np.percentile(final_pd, 50)),
            "percentile_75": float(np.percentile(final_pd, 75)),
            "percentile_95": float(np.percentile(final_pd, 95)),
            "percentile_99": float(np.percentile(final_pd, 99)),
            "stressed_pd": float(np.percentile(final_pd, 99)),  # 99th percentile
            "monte_carlo_paths": pd_paths,
            "n_simulations": n_simulations,
            "time_horizon": time_horizon
        }
    
    def calculate_expected_loss(
        self,
        exposure: float,
        pd: float,
        lgd: float
    ) -> float:
        """
        Calculate Expected Loss (EL).
        
        EL = EAD × PD × LGD
        
        Args:
            exposure: Exposure at Default (EAD)
            pd: Probability of Default
            lgd: Loss Given Default
            
        Returns:
            Expected Loss amount
        """
        return exposure * pd * lgd
    
    def calculate_unexpected_loss(
        self,
        exposure: float,
        pd: float,
        lgd: float,
        correlation: float = None
    ) -> float:
        """
        Calculate Unexpected Loss (UL) using Basel formula.
        
        UL = EAD × √(PD × LGD² × (1 - PD)) × √(correlation)
        
        Args:
            exposure: Exposure at Default
            pd: Probability of Default
            lgd: Loss Given Default
            correlation: Asset correlation
            
        Returns:
            Unexpected Loss amount
        """
        corr = correlation if correlation is not None else self.correlation
        
        # Basel IRB unexpected loss approximation
        ul_component = np.sqrt(
            pd * (lgd ** 2) * (1 - pd)
        )
        
        return exposure * ul_component * np.sqrt(corr)
    
    def calculate_capital_requirement(
        self,
        unexpected_loss: float,
        confidence_level: float = 0.999,
        capital_ratio: float = 0.08
    ) -> Dict:
        """
        Calculate capital requirement for unexpected losses.
        
        Args:
            unexpected_loss: Unexpected Loss amount
            confidence_level: Confidence level for capital (default: 99.9%)
            capital_ratio: Minimum capital ratio (default: 8%)
            
        Returns:
            Dictionary with capital calculations
        """
        # Adjust capital for confidence level
        z_score = {
            0.90: 1.28,
            0.95: 1.645,
            0.99: 2.33,
            0.999: 3.09
        }.get(confidence_level, 3.09)
        
        base_capital = unexpected_loss * capital_ratio
        adjusted_capital = unexpected_loss * capital_ratio * z_score / 3.09
        
        return {
            "unexpected_loss": unexpected_loss,
            "base_capital": base_capital,
            "adjusted_capital": adjusted_capital,
            "confidence_level": confidence_level,
            "z_score": z_score,
            "capital_ratio": capital_ratio
        }
    
    def run_full_analysis(
        self,
        exposure: float,
        time_horizon: int,
        physical_damage_ratio: float,
        n_simulations: int = 10000
    ) -> Dict:
        """
        Run complete climate credit risk analysis.
        
        Args:
            exposure: Exposure at Default
            time_horizon: Analysis horizon in years
            physical_damage_ratio: Ratio of physical damage
            n_simulations: Number of Monte Carlo simulations
            
        Returns:
            Complete analysis results
        """
        # Calculate climate adjustments
        adjustment = self.calculate_climate_adjustment(physical_damage_ratio)
        
        # Monte Carlo for stressed PD
        pd_result = self.calculate_adjusted_pd_monte_carlo(
            time_horizon=time_horizon,
            climate_factor=adjustment["climate_factor"],
            n_simulations=n_simulations
        )
        
        # Expected Loss calculations
        base_el = self.calculate_expected_loss(
            exposure, self.base_pd, self.base_lgd
        )
        stressed_el = self.calculate_expected_loss(
            exposure, pd_result["stressed_pd"], adjustment["adjusted_lgd"]
        )
        
        # Unexpected Loss calculations
        base_ul = self.calculate_unexpected_loss(
            exposure, self.base_pd, self.base_lgd
        )
        stressed_ul = self.calculate_unexpected_loss(
            exposure, pd_result["stressed_pd"], adjustment["adjusted_lgd"]
        )
        
        # Capital requirements
        base_capital = self.calculate_capitalrequirement(base_ul)
        stressed_capital = self.calculate_capital_requirement(stressed_ul)
        
        return {
            "input": {
                "exposure": exposure,
                "time_horizon": time_horizon,
                "physical_damage_ratio": physical_damage_ratio,
                "base_pd": self.base_pd,
                "base_lgd": self.base_lgd
            },
            "climate_adjustment": adjustment,
            "pd_analysis": {
                "base_pd": self.base_pd,
                "stressed_pd": pd_result["stressed_pd"],
                "pd_increase_factor": pd_result["stressed_pd"] / self.base_pd,
                "pd_distribution": pd_result
            },
            "expected_loss": {
                "base": base_el,
                "stressed": stressed_el,
                "additional": stressed_el - base_el,
                "increase_percentage": (stressed_el - base_el) / base_el * 100 if base_el > 0 else 0
            },
            "unexpected_loss": {
                "base": base_ul,
                "stressed": stressed_ul,
                "additional": stressed_ul - base_ul,
                "increase_percentage": (stressed_ul - base_ul) / base_ul * 100 if base_ul > 0 else 0
            },
            "capital": {
                "base": base_capital["base_capital"],
                "stressed": stressed_capital["adjusted_capital"],
                "additional": stressed_capital["adjusted_capital"] - base_capital["base_capital"],
                "climate_buffer": stressed_capital["adjusted_capital"] * 0.15  # 15% climate buffer
            },
            "summary": {
                "pd_multiplier": adjustment["pd_multiplier"],
                "lgd_multiplier": adjustment["lgd_multiplier"],
                "total_impact": stressed_el - base_el + stressed_ul - base_ul,
                "capital_increase": stressed_capital["adjusted_capital"] - base_capital["base_capital"]
            }
        }


class PortfolioRiskCalculator:
    """
    Portfolio-level climate risk calculator.
    
    Aggregates risk across multiple exposures with
    diversification benefits.
    """
    
    def __init__(self, correlations: Dict[Tuple[str, str], float] = None):
        """
        Initialize portfolio calculator.
        
        Args:
            correlations: Custom correlation matrix
        """
        self.correlations = correlations or {}
        self.default_correlations = {
            ("residential", "commercial"): 0.6,
            ("residential", "industrial"): 0.4,
            ("commercial", "industrial"): 0.5,
            ("same_sector", "same_region"): 0.7
        }
    
    def calculate_portfolio_risk(
        self,
        exposures: list,
        climate_scenario: Dict = None
    ) -> Dict:
        """
        Calculate portfolio-level risk.
        
        Args:
            exposures: List of PortfolioAsset objects or dictionaries
            climate_scenario: Optional climate scenario parameters
            
        Returns:
            Portfolio risk metrics
        """
        # Handle both PortfolioAsset objects and dictionaries
        total_exposure = sum(e.value if hasattr(e, 'value') else e["value"] for e in exposures)
        
        # Calculate individual risks
        individual_risks = []
        for i, exp in enumerate(exposures):
            # Extract values based on type
            if hasattr(exp, 'value'):
                # PortfolioAsset object
                exp_value = exp.value
                exp_pd = getattr(exp, 'base_pd', 0.02)
                exp_lgd = getattr(exp, 'base_lgd', 0.4)
                exp_beta = getattr(exp, 'climate_beta', 0.5)
                exp_damage = getattr(exp, 'damage_ratio', 0)
                exp_id = getattr(exp, 'asset_id', f"exp_{i}")
            else:
                # Dictionary
                exp_value = exp["value"]
                exp_pd = exp.get("pd", exp.get("base_pd", 0.02))
                exp_lgd = exp.get("lgd", exp.get("base_lgd", 0.4))
                exp_beta = exp.get("climate_beta", 0.5)
                exp_damage = exp.get("damage_ratio", 0)
                exp_id = exp.get("id", exp.get("asset_id", f"exp_{i}"))
            
            vasicek = ClimateVasicek(
                base_pd=exp_pd,
                base_lgd=exp_lgd,
                climate_beta=exp_beta
            )
            
            analysis = vasicek.run_full_analysis(
                exposure=exp_value,
                time_horizon=10,
                physical_damage_ratio=exp_damage
            )
            
            individual_risks.append({
                "exposure_id": exp_id,
                "value": exp_value,
                "weight": exp_value / total_exposure,
                "expected_loss": analysis["expected_loss"]["additional"],
                "unexpected_loss": analysis["unexpected_loss"]["additional"],
                "capital_impact": analysis["capital"]["additional"]
            })
        
        # Diversified risk calculation
        if len(exposures) > 1:
            # Simplified diversification: apply correlation discount
            avg_correlation = 0.3  # Portfolio diversification benefit
            diversification_factor = np.sqrt(
                1 / len(exposures) +
                (len(exposures) - 1) / len(exposures) * avg_correlation
            )
        else:
            diversification_factor = 1.0
        
        # Aggregate risks
        total_el = sum(r["expected_loss"] for r in individual_risks)
        total_ul = sum(r["unexpected_loss"] for r in individual_risks) * diversification_factor
        total_capital = sum(r["capital_impact"] for r in individual_risks)
        
        return {
            "total_exposure": total_exposure,
            "num_exposures": len(exposures),
            "diversification_factor": diversification_factor,
            "expected_loss": total_el,
            "unexpected_loss": total_ul,
            "capital_impact": total_capital,
            "individual_risks": individual_risks,
            "concentration": self._calculate_concentration(individual_risks)
        }
    
    def _calculate_concentration(self, risks: list) -> Dict:
        """Calculate portfolio concentration metrics."""
        if not risks:
            return {}
        
        weights = [r["weight"] for r in risks]
        max_weight = max(weights)
        hhi = sum(w ** 2 for w in weights)  # Herfindahl-Hirschman Index
        
        return {
            "max_weight": max_weight,
            "hhi": hhi,
            "concentration_level": "high" if hhi > 0.25 else "medium" if hhi > 0.15 else "low"
        }
