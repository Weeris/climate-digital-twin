"""
Data Processing Utilities

Helpers for data ingestion, transformation, and analysis.
"""

from typing import Dict, List, Any
import pandas as pd
import numpy as np


class DataProcessor:
    """Data processing utilities for climate risk analysis."""
    
    @staticmethod
    def load_portfolio_csv(filepath: str) -> pd.DataFrame:
        """
        Load portfolio data from CSV.
        
        Expected columns:
        - asset_id: Unique identifier
        - value: Asset value
        - asset_type: residential/commercial/industrial
        - region: Geographic region
        - base_pd: Probability of Default
        - base_lgd: Loss Given Default
        - damage_ratio: Physical damage ratio
        """
        df = pd.read_csv(filepath)
        
        # Validate required columns
        required = ["asset_id", "value", "asset_type", "region"]
        missing = [col for col in required if col not in df.columns]
        
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
        
        # Fill defaults
        if "base_pd" not in df.columns:
            df["base_pd"] = 0.02
        if "base_lgd" not in df.columns:
            df["base_lgd"] = 0.4
        if "damage_ratio" not in df.columns:
            df["damage_ratio"] = 0.0
        
        return df
    
    @staticmethod
    def aggregate_by_region(portfolio: pd.DataFrame) -> pd.DataFrame:
        """
        Aggregate portfolio values by region.
        
        Returns:
            DataFrame with regional totals
        """
        return portfolio.groupby("region").agg({
            "value": "sum",
            "asset_id": "count"
        }).reset_index().rename(columns={"asset_id": "asset_count"})
    
    @staticmethod
    def aggregate_by_type(portfolio: pd.DataFrame) -> pd.DataFrame:
        """
        Aggregate portfolio values by asset type.
        
        Returns:
            DataFrame with type totals
        """
        return portfolio.groupby("asset_type").agg({
            "value": "sum",
            "asset_id": "count"
        }).reset_index().rename(columns={"asset_id": "asset_count"})
    
    @staticmethod
    def calculate_weights(portfolio: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate portfolio weights.
        
        Adds weight column proportional to asset value.
        """
        total = portfolio["value"].sum()
        portfolio["weight"] = portfolio["value"] / total
        return portfolio
    
    @staticmethod
    def calculate_concentration_metrics(portfolio: pd.DataFrame) -> Dict:
        """
        Calculate portfolio concentration metrics.
        
        Returns:
            Dictionary with HHI and concentration metrics
        """
        weights = portfolio["value"] / portfolio["value"].sum()
        hhi = (weights ** 2).sum()
        
        max_weight = weights.max()
        
        return {
            "hhi": hhi,
            "max_weight": max_weight,
            "n_assets": len(portfolio),
            "concentration_level": "high" if hhi > 0.25 else "medium" if hhi > 0.15 else "low"
        }


class ReportGenerator:
    """Generate reports from simulation results."""
    
    @staticmethod
    def format_currency(value: float, currency: str = "USD") -> str:
        """Format value as currency."""
        if currency == "USD":
            return f"${value:,.0f}"
        elif currency == "THB":
            return f"฿{value:,.0f}"
        else:
            return f"{value:,.0f}"
    
    @staticmethod
    def format_percentage(value: float) -> str:
        """Format value as percentage."""
        return f"{value * 100:.2f}%"
    
    @staticmethod
    def summary_report(simulation_result: Dict, currency: str = "USD") -> str:
        """
        Generate text summary of simulation results.
        """
        config = simulation_result["simulation_config"]
        risk = simulation_result["risk_metrics"]
        returns = simulation_result["return_distribution"]
        final = simulation_result["final_distribution"]
        
        lines = [
            "=" * 60,
            "CLIMATE RISK SIMULATION SUMMARY",
            "=" * 60,
            "",
            f"Scenario: {config['hazard_type']}",
            f"Climate Factor: {config['climate_factor']:.2%}",
            f"Time Horizon: {config['time_horizon']} years",
            f"Simulations: {config['n_simulations']:,}",
            "",
            "-" * 60,
            "PORTFOLIO VALUES",
            "-" * 60,
            f"Initial Value: {ReportGenerator.format_currency(simulation_result['initial_value'], currency)}",
            f"Expected Final Value: {ReportGenerator.format_currency(final['mean'], currency)}",
            f"Median Final Value: {ReportGenerator.format_currency(final['percentile_50'], currency)}",
            f"5th Percentile (Worst 5%): {ReportGenerator.format_currency(final['percentile_5'], currency)}",
            "",
            "-" * 60,
            "RETURN DISTRIBUTION",
            "-" * 60,
            f"Mean Return: {ReportGenerator.format_percentage(returns['mean'])}",
            f"Std Deviation: {ReportGenerator.format_percentage(returns['std'])}",
            f"5th Percentile VaR: {ReportGenerator.format_percentage(risk['value_at_risk'])}",
            f"Expected Shortfall: {ReportGenerator.format_percentage(risk['expected_shortfall'])}",
            "",
            "-" * 60,
            "RISK METRICS",
            "-" * 60,
            f"Probability of Loss: {ReportGenerator.format_percentage(risk['probability_of_loss'])}",
            f"Probability of 25% Loss: {ReportGenerator.format_percentage(risk['probability_of_25pct_loss'])}",
            f"Probability of 50% Loss: {ReportGenerator.format_percentage(risk['probability_of_50pct_loss'])}",
            "",
            "=" * 60,
        ]
        
        return "\n".join(lines)
