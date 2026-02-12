"""
Test suite for Climate Digital Twin - Financial Module
"""
import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.financial import (
    ClimateVasicek, ClimateRiskAdjustment, CreditRiskInput,
    PortfolioRiskCalculator
)


class TestClimateVasicek:
    """Tests for ClimateVasicek model class."""
    
    @pytest.fixture
    def vasicek(self):
        """Create ClimateVasicek instance."""
        return ClimateVasicek(
            base_pd=0.02,
            base_lgd=0.4,
            climate_beta=0.5
        )
    
    def test_initialization(self, vasicek):
        """Test model initialization."""
        assert vasicek.base_pd == 0.02
        assert vasicek.base_lgd == 0.4
        assert vasicek.climate_beta == 0.5
        assert vasicek.correlation == 0.3
    
    def test_calculate_climate_adjustment_zero_damage(self, vasicek):
        """Test climate adjustment with zero physical damage."""
        adjustment = vasicek.calculate_climate_adjustment(physical_damage_ratio=0.0)
        
        assert adjustment["pd_multiplier"] == 1.0
        assert adjustment["lgd_multiplier"] == 1.0
        assert adjustment["climate_factor"] == 0.0
    
    def test_calculate_climate_adjustment_partial_damage(self, vasicek):
        """Test climate adjustment with partial physical damage."""
        adjustment = vasicek.calculate_climate_adjustment(physical_damage_ratio=0.3)
        
        assert adjustment["pd_multiplier"] == pytest.approx(1.15, rel=0.01)
        assert adjustment["lgd_multiplier"] == pytest.approx(1.15, rel=0.01)
    
    def test_calculate_expected_loss(self, vasicek):
        """Test expected loss calculation."""
        el = vasicek.calculate_expected_loss(
            exposure=1000000,
            pd=0.02,
            lgd=0.4
        )
        
        expected = 1000000 * 0.02 * 0.4
        assert el == expected
    
    def test_calculate_unexpected_loss(self, vasicek):
        """Test unexpected loss calculation."""
        ul = vasicek.calculate_unexpected_loss(
            exposure=1000000,
            pd=0.02,
            lgd=0.4,
            correlation=0.3
        )
        
        assert ul > 0
    
    def test_calculate_capital_requirement(self, vasicek):
        """Test capital requirement calculation."""
        capital = vasicek.calculate_capital_requirement(
            unexpected_loss=100000,
            confidence_level=0.999
        )
        
        assert "base_capital" in capital
        assert capital["base_capital"] == 8000
    
    def test_monte_carlo_returns_statistics(self, vasicek):
        """Test Monte Carlo returns required statistics."""
        result = vasicek.calculate_adjusted_pd_monte_carlo(
            time_horizon=10,
            climate_factor=0.1,
            n_simulations=500,
            random_seed=42
        )
        
        assert "mean" in result
        assert "percentile_5" in result
        assert "percentile_50" in result
        assert "percentile_95" in result
    
    def test_run_full_analysis_structure(self, vasicek):
        """Test complete analysis structure."""
        result = vasicek.run_full_analysis(
            exposure=10000000,
            time_horizon=10,
            physical_damage_ratio=0.2,
            n_simulations=500
        )
        
        assert "input" in result
        assert "climate_adjustment" in result
        assert "pd_analysis" in result
        assert "expected_loss" in result
        assert "capital" in result


class TestPortfolioRiskCalculator:
    """Tests for PortfolioRiskCalculator class."""
    
    @pytest.fixture
    def calculator(self):
        """Create portfolio calculator instance."""
        return PortfolioRiskCalculator()
    
    def test_calculate_portfolio_risk_single_exposure(self, calculator):
        """Test portfolio risk with single exposure."""
        exposures = [
            {"value": 10000000, "pd": 0.02, "lgd": 0.4, "damage_ratio": 0.1}
        ]
        
        result = calculator.calculate_portfolio_risk(exposures)
        
        assert result["total_exposure"] == 10000000
        assert result["num_exposures"] == 1
    
    def test_calculate_portfolio_risk_multiple_exposures(self, calculator):
        """Test portfolio risk with multiple exposures."""
        exposures = [
            {"value": 10000000, "pd": 0.02, "lgd": 0.4, "damage_ratio": 0.1},
            {"value": 5000000, "pd": 0.015, "lgd": 0.35, "damage_ratio": 0.2},
        ]
        
        result = calculator.calculate_portfolio_risk(exposures)
        
        assert result["total_exposure"] == 15000000
        assert result["num_exposures"] == 2
        assert len(result["individual_risks"]) == 2
