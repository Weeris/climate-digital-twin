"""
Climate Digital Twin - Streamlit Dashboard

Interactive dashboard for climate risk assessment and visualization.

Features:
- Real-time hazard assessment
- Portfolio risk analysis
- Monte Carlo simulation
- Scenario comparison
"""

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, List

# Import core modules
from core.hazard import HazardAssessment, RegionalHazardData
from core.financial import ClimateVasicek, PortfolioRiskCalculator
from core.simulation import MonteCarloEngine, ScenarioGenerator, PortfolioAsset, SimulationConfig
from core.scenarios import ScenarioFramework
from utils.data_processing import DataProcessor, ReportGenerator


# Page configuration
st.set_page_config(
    page_title="Climate Digital Twin",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        font-weight: bold;
        color: #1E88E5;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.25rem;
        font-weight: bold;
        color: #424242;
        margin-bottom: 0.5rem;
    }
    .metric-card {
        background-color: #f5f5f5;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .stMetric {
        background-color: #f0f2f6;
        border-radius: 5px;
        padding: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)


def main():
    """Main dashboard application."""
    
    # Header
    st.markdown('<div class="main-header">🌍 Climate Digital Twin</div>', unsafe_allow_html=True)
    st.markdown("Digital framework for quantifying physical climate-related financial risks")
    st.markdown("---")
    
    # Sidebar - Navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Go to",
        ["Hazard Assessment", "Portfolio Risk", "Monte Carlo Simulation", "Scenario Analysis"]
    )
    
    # Sidebar - Settings
    st.sidebar.markdown("---")
    st.sidebar.title("Settings")
    currency = st.sidebar.selectbox("Currency", ["USD", "THB", "EUR", "GBP"])
    
    if page == "Hazard Assessment":
        show_hazard_assessment(currency)
    elif page == "Portfolio Risk":
        show_portfolio_risk(currency)
    elif page == "Monte Carlo Simulation":
        show_monte_carlo(currency)
    elif page == "Scenario Analysis":
        show_scenario_analysis(currency)


def show_hazard_assessment(currency: str):
    """Hazard assessment page."""
    st.markdown('<div class="sub-header">🌊 Hazard Assessment</div>', unsafe_allow_html=True)
    st.markdown("Assess physical damage from climate hazards")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### Hazard Parameters")
        hazard_type = st.selectbox(
            "Hazard Type",
            ["flood", "wildfire", "cyclone", "drought"]
        )
        
        if hazard_type == "flood":
            intensity = st.slider("Flood Depth (meters)", 0.0, 5.0, 0.5, 0.1)
        elif hazard_type == "wildfire":
            intensity = st.slider("Burn Area (%)", 0, 100, 20, 5)
        elif hazard_type == "cyclone":
            intensity = st.slider("Wind Speed (km/h)", 50, 300, 120, 10)
        else:
            intensity = st.slider("SPI Index", -3.0, 0.0, -1.0, 0.1)
        
        asset_value = st.number_input(f"Asset Value ({currency})", 100000, 100000000, 10000000, 100000)
        asset_type = st.selectbox("Asset Type", ["residential", "commercial", "industrial"])
        
        if st.button("Calculate Damage"):
            hazard = HazardAssessment()
            
            if hazard_type == "flood":
                result = hazard.assess_flood_risk(
                    depth_m=intensity,
                    asset_value=asset_value,
                    asset_type=asset_type
                )
            else:
                result = hazard.assess_hazard(
                    hazard_type=hazard_type,
                    intensity=intensity,
                    asset_value=asset_value,
                    asset_type=asset_type
                )
            
            st.session_state.hazard_result = result
    
    with col2:
        if "hazard_result" in st.session_state:
            result = st.session_state.hazard_result
            
            # Display metrics
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Damage Ratio", f"{result['damage_ratio']*100:.1f}%")
            m2.metric("Physical Damage", f"{result['physical_damage']:,.0f} {currency}")
            m3.metric("Residual Value", f"{result['residual_value']:,.0f} {currency}")
            m4.metric("Downtime", f"{result.get('downtime_days', 'N/A')}")
            
            # Damage curve visualization
            fig, ax = plt.subplots(figsize=(10, 4))
            
            if hazard_type == "flood":
                depths = np.linspace(0, 3, 100)
                damages = [hazard._flood_damage_curve(d, asset_type) for d in depths]
                ax.plot(depths, damages, 'b-', linewidth=2)
                ax.axvline(x=intensity, color='r', linestyle='--', label=f'Current: {intensity}m')
                ax.fill_between(depths, damages, alpha=0.3)
                ax.set_xlabel('Flood Depth (m)')
            else:
                intensities = np.linspace(0, intensity * 1.5, 100)
                ax.plot(intensities, np.linspace(0, 1, 100), 'r-', linewidth=2)
                ax.axvline(x=intensity, color='b', linestyle='--', label=f'Current: {intensity}')
                ax.set_xlabel('Hazard Intensity')
            
            ax.set_ylabel('Damage Ratio')
            ax.set_title(f'{hazard_type.title()} Damage Function')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            st.pyplot(fig)


def show_portfolio_risk(currency: str):
    """Portfolio risk analysis page."""
    st.markdown('<div class="sub-header">📊 Portfolio Risk Analysis</div>', unsafe_allow_html=True)
    st.markdown("Analyze climate risk across portfolio exposures")
    
    # Sample portfolio data
    sample_portfolio = pd.DataFrame({
        "id": ["A001", "A002", "A003", "A004", "A005"],
        "asset_type": ["residential", "residential", "commercial", "industrial", "industrial"],
        "region": ["Bangkok", "Bangkok", "Chonburi", "Ayutthaya", "Rayong"],
        "value": [50000000, 30000000, 80000000, 120000000, 60000000],
        "damage_ratio": [0.15, 0.10, 0.20, 0.35, 0.25],
        "pd": [0.02, 0.015, 0.03, 0.04, 0.035]
    })
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### Portfolio Input")
        
        use_sample = st.checkbox("Use Sample Portfolio", value=True)
        
        if use_sample:
            portfolio = sample_portfolio.copy()
            st.dataframe(portfolio, hide_index=True)
        else:
            uploaded = st.file_uploader("Upload Portfolio CSV", type=["csv"])
            if uploaded:
                portfolio = DataProcessor.load_portfolio_csv(uploaded)
                st.dataframe(portfolio.head(), hide_index=True)
            else:
                portfolio = sample_portfolio.copy()
        
        climate_factor = st.slider("Climate Factor", 0.0, 1.0, 0.2, 0.05)
        
        if st.button("Analyze Portfolio"):
            assets = [
                PortfolioAsset(
                    asset_id=row["id"],
                    value=row["value"],
                    asset_type=row["asset_type"],
                    region=row["region"],
                    damage_ratio=row.get("damage_ratio", 0.1)
                )
                for _, row in portfolio.iterrows()
            ]
            
            calculator = PortfolioRiskCalculator()
            result = calculator.calculate_portfolio_risk(assets)
            st.session_state.portfolio_result = result
    
    with col2:
        if "portfolio_result" in st.session_state:
            result = st.session_state.portfolio_result
            
            # Key metrics
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Total Exposure", f"{result['total_exposure']:,.0f} {currency}")
            m2.metric("Expected Loss", f"{result['expected_loss']:,.0f} {currency}")
            m3.metric("Unexpected Loss", f"{result['unexpected_loss']:,.0f} {currency}")
            m4.metric("Capital Impact", f"{result['capital_impact']:,.0f} {currency}")
            
            # Concentration chart
            st.subheader("Portfolio Concentration")
            conc = result["concentration"]
            st.write(f"Concentration Level: {conc['concentration_level']}")
            st.progress(min(conc['hhi'] * 4, 1.0))
            
            # Asset breakdown
            st.subheader("Individual Risk Contributions")
            risk_df = pd.DataFrame(result["individual_risks"])
            st.dataframe(risk_df, hide_index=True)


def show_monte_carlo(currency: str):
    """Monte Carlo simulation page."""
    st.markdown('<div class="sub-header">🎲 Monte Carlo Simulation</div>', unsafe_allow_html=True)
    st.markdown("Run portfolio-level Monte Carlo simulations for risk distribution")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### Simulation Parameters")
        
        n_simulations = st.number_input("Number of Simulations", 1000, 50000, 10000, 1000)
        time_horizon = st.slider("Time Horizon (years)", 1, 30, 10, 1)
        confidence = st.selectbox("Confidence Level", [0.90, 0.95, 0.99, 0.999])
        
        climate_factor = st.slider("Climate Factor", 0.0, 1.0, 0.2, 0.05)
        hazard_type = st.selectbox("Hazard Type", ["flood", "wildfire", "cyclone", "drought"])
        
        # Sample portfolio
        portfolio = [
            PortfolioAsset(
                asset_id=f"Asset_{i}",
                value=50000000,
                asset_type="residential",
                region="Bangkok",
                climate_beta=0.5
            )
            for i in range(10)
        ]
        
        if st.button("Run Simulation"):
            config = SimulationConfig(
                n_simulations=n_simulations,
                time_horizon=time_horizon,
                confidence_level=confidence,
                random_seed=42
            )
            
            engine = MonteCarloEngine(config)
            result = engine.run_simulation(
                assets=portfolio,
                climate_factor=climate_factor,
                hazard_type=hazard_type
            )
            st.session_state.mc_result = result
    
    with col2:
        if "mc_result" in st.session_state:
            result = st.session_state.mc_result
            
            # Risk metrics
            m1, m2, m3, m4 = st.columns(4)
            risk = result["risk_metrics"]
            m1.metric("Mean Return", f"{risk['mean']*100:.1f}%")
            m2.metric("Value at Risk (5%)", f"{risk['value_at_risk']*100:.1f}%")
            m3.metric("Expected Shortfall", f"{risk['expected_shortfall']*100:.1f}%")
            m4.metric("Probability of Loss", f"{risk['probability_of_loss']*100:.1f}%")
            
            # Return distribution
            fig, axes = plt.subplots(1, 2, figsize=(14, 4))
            
            # Histogram
            axes[0].hist(
                result["return_distribution_array"]() * 100,
                bins=50,
                edgecolor='black',
                alpha=0.7
            )
            axes[0].axvline(x=risk['value_at_risk'] * 100, color='r', linestyle='--', label='VaR 5%')
            axes[0].axvline(x=risk['expected_shortfall'] * 100, color='orange', linestyle='--', label='ES')
            axes[0].set_xlabel('Return (%)')
            axes[0].set_ylabel('Frequency')
            axes[0].set_title('Return Distribution')
            axes[0].legend()
            
            # Portfolio paths
            paths = result["portfolio_paths"]
            sample_indices = np.random.choice(len(paths), min(100, len(paths)), replace=False)
            for idx in sample_indices:
                axes[1].plot(paths[idx] / paths[idx, 0], alpha=0.1, color='blue')
            axes[1].axhline(y=1.0, color='black', linestyle='-', linewidth=1)
            axes[1].set_xlabel('Time (days)')
            axes[1].set_ylabel('Relative Value')
            axes[1].set_title('Portfolio Value Paths (sample)')
            
            st.pyplot(fig)


def show_scenario_analysis(currency: str):
    """Scenario analysis page."""
    st.markdown('<div class="sub-header">🎭 Scenario Analysis</div>', unsafe_allow_html=True)
    st.markdown("Compare risk across different climate scenarios")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### Scenario Selection")
        
        framework = ScenarioFramework()
        scenarios = framework.get_all_scenarios()
        
        selected_scenarios = st.multiselect(
            "Select Scenarios",
            list(scenarios.keys()),
            default=["orderly_below_2c", "hot_house_ndc"]
        )
        
        time_horizon = st.slider("Time Horizon (years)", 5, 50, 10, 5)
        
        # Sample portfolio for analysis
        portfolio = [
            PortfolioAsset(
                asset_id=f"Asset_{i}",
                value=50000000,
                asset_type="residential",
                region="Bangkok",
                climate_beta=0.5
            )
            for i in range(10)
        ]
        
        if st.button("Compare Scenarios"):
            config = SimulationConfig(
                n_simulations=5000,
                time_horizon=time_horizon,
                random_seed=42
            )
            engine = MonteCarloEngine(config)
            
            results = {}
            for scen in selected_scenarios:
                scenario_def = scenarios[scen]
                results[scen] = engine.run_simulation(
                    assets=portfolio,
                    climate_factor=scenario_def.climate_factor,
                    hazard_type=scen
                )
            
            st.session_state.scenario_results = results
            st.session_state.framework = framework
    
    with col2:
        if "scenario_results" in st.session_state:
            results = st.session_state.scenario_results
            framework = st.session_state.framework
            
            # Comparison table
            comparison_data = []
            for scen, result in results.items():
                scen_def = framework.get_scenario(scen)
                risk = result["risk_metrics"]
                comparison_data.append({
                    "Scenario": scen_def.name,
                    "Category": scen_def.category,
                    "Climate Factor": f"{scen_def.climate_factor:.0%}",
                    "Mean Return": f"{risk['mean']*100:.1f}%",
                    "VaR (5%)": f"{risk['value_at_risk']*100:.1f}%",
                    "Prob. Loss": f"{risk['probability_of_loss']*100:.1f}%"
                })
            
            comparison_df = pd.DataFrame(comparison_data)
            st.table(comparison_df)
            
            # Comparison chart
            fig, ax = plt.subplots(figsize=(10, 5))
            
            x = np.arange(len(results))
            means = [results[s]["risk_metrics"]["mean"] * 100 for s in results]
            var5s = [results[s]["risk_metrics"]["value_at_risk"] * 100 for s in results]
            
            width = 0.35
            bars1 = ax.bar(x - width/2, means, width, label='Mean Return', color='steelblue')
            bars2 = ax.bar(x + width/2, var5s, width, label='VaR 5%', color='coral')
            
            ax.set_ylabel('Return (%)')
            ax.set_title('Scenario Comparison: Mean Return vs VaR')
            ax.set_xticks(x)
            ax.set_xticklabels([s.replace('_', '\n') for s in results.keys()], fontsize=8)
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            st.pyplot(fig)


if __name__ == "__main__":
    main()
