"""
Climate Digital Twin - Enhanced Streamlit Dashboard

Multi-page dashboard for climate risk assessment workflow:
1. Home/Demo - Overview and workflow visualization
2. Data Input - Portfolio and hazard data input
3. Hazard Assessment - Physical damage analysis
4. Financial Impact - Credit risk calculations
5. Monte Carlo - Portfolio simulation
6. Scenario Analysis - Multi-scenario comparison
7. Reports - Summary reports and exports
"""

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, List, Optional
from dataclasses import dataclass

# Import core modules
from core.hazard import HazardAssessment, RegionalHazardData
from core.financial import ClimateVasicek, PortfolioRiskCalculator
from core.simulation import MonteCarloEngine, PortfolioAsset, SimulationConfig
from core.scenarios import ScenarioFramework
from utils.data_processing import DataProcessor


# Page configuration
st.set_page_config(
    page_title="Climate Digital Twin",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)


@dataclass
class WorkflowState:
    """Track workflow state across pages."""
    portfolio_data: Optional[pd.DataFrame] = None
    hazard_result: Optional[Dict] = None
    financial_result: Optional[Dict] = None
    simulation_result: Optional[Dict] = None
    scenario_results: Optional[Dict] = None


def get_workflow_state() -> WorkflowState:
    """Get or create workflow state."""
    if "workflow" not in st.session_state:
        st.session_state.workflow = WorkflowState()
    return st.session_state.workflow


def show_sidebar():
    """Show sidebar navigation."""
    st.sidebar.title("🌍 Climate Digital Twin")
    st.sidebar.markdown("---")
    
    workflow = get_workflow_state()
    
    steps = [
        ("🏠 Home", "home"),
        ("📥 Data Input", "data"),
        ("🌊 Hazard Assessment", "hazard"),
        ("💰 Financial Impact", "financial"),
        ("🎲 Monte Carlo", "monte_carlo"),
        ("🎭 Scenario Analysis", "scenario"),
        ("🗺️ HK Risk Map", "hk_map"),
        ("📄 Reports", "reports")
    ]
    
    step_status = {
        "home": True,
        "data": workflow.portfolio_data is not None,
        "hazard": workflow.hazard_result is not None,
        "financial": workflow.financial_result is not None,
        "monte_carlo": workflow.simulation_result is not None,
        "scenario": workflow.scenario_results is not None,
    }
    
    for name, key in steps:
        if st.sidebar.button(f"{name}", key=f"nav_{key}"):
            st.session_state.nav_page = key
            st.rerun()
    
    st.sidebar.markdown("---")
    st.sidebar.title("Settings")
    currency = st.sidebar.selectbox("Currency", ["USD", "THB", "EUR", "GBP", "HKD"], index=4)
    
    if st.sidebar.button("🔄 Reset"):
        st.session_state.workflow = WorkflowState()
        st.rerun()
    
    return currency


def show_home_page(currency: str = "HKD"):
    """Home page with workflow overview."""
    st.markdown("""
    <div style="text-align: center; font-size: 2.5rem; font-weight: bold; color: #1E88E5; margin-bottom: 1rem;">
        🌍 Climate Digital Twin
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; font-size: 1.2rem; color: #666; margin-bottom: 2rem;">
        Digital framework for quantifying physical climate-related financial risks
    </div>
    """, unsafe_allow_html=True)
    
    # Infographic - Workflow Overview
    st.markdown("### How It Works")
    
    col1, col2, col3, col4 = st.columns(4)
    
    steps = [
        ("1", "Upload", "Portfolio & Hazard Data", "📁", "#667eea"),
        ("2", "Analyze", "Flood & Typhoon Risk", "🌊", "#e74c3c"),
        ("3", "Calculate", "Financial Impact", "💰", "#27ae60"),
        ("4", "Report", "Risk Metrics", "📈", "#8e44ad"),
    ]
    
    for col, (num, title, desc, icon, color) in zip([col1, col2, col3, col4], steps):
        with col:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, {color} 0%, {color}dd 100%); color: white; 
                        padding: 1.5rem; border-radius: 12px; text-align: center;">
                <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">{icon}</div>
                <strong style="font-size: 1.2rem;">{title}</strong>
                <div style="font-size: 0.85rem; margin-top: 0.5rem; opacity: 0.9;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # What it does
    st.markdown("""
    ### What This Application Does
    
    1. **Hazard Assessment**: Evaluate physical damage from floods, wildfires, cyclones, and droughts
    2. **Credit Risk Analysis**: Adjust probability of default (PD) and loss given default (LGD)
    3. **Portfolio Simulation**: Run Monte Carlo simulations for risk distributions
    4. **Scenario Analysis**: Compare risks across orderly, disorderly, and hot house scenarios
    
    ### Key Features
    
    - 🔬 **Extended Vasicek Model**: Credit risk model with climate factors
    - 🎲 **Monte Carlo Simulation**: 10,000+ portfolio paths
    - 📊 **Multiple Hazards**: Flood, wildfire, cyclone, drought
    - 🌍 **Scenario Framework**: Standardized climate scenarios
    """)
    
    if st.button("▶️ Start Assessment →"):
        st.session_state.nav_page = "data"
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 🎬 Run Sample Analysis")
    
    if st.button("Run Demo"):
        sample_portfolio = pd.DataFrame({
            "asset_id": ["HK001", "HK002", "HK003", "HK004", "HK005"],
            "asset_type": ["residential_high_rise", "residential_high_rise", "commercial_office", "industrial_warehouse", "commercial_retail"],
            "district": ["central", "wan_chai", "tst", "kwun_tong", "causeway_bay"],
            "value": [50000000, 30000000, 80000000, 120000000, 60000000],
            "base_pd": [0.015, 0.018, 0.025, 0.035, 0.02],
            "base_lgd": [0.35, 0.38, 0.42, 0.45, 0.4],
            "damage_ratio": [0.12, 0.15, 0.18, 0.28, 0.14],
            "floor": [35, 22, 45, 8, 12],
            "building_age": [8, 15, 5, 20, 25]
        })
        
        hazard = HazardAssessment()
        hazard_result = hazard.assess_flood_risk(depth_m=1.0, asset_value=100000000, asset_type="residential")
        
        vasicek = ClimateVasicek(base_pd=0.02, base_lgd=0.4, climate_beta=0.5)
        financial_result = vasicek.run_full_analysis(exposure=100000000, time_horizon=10, physical_damage_ratio=0.25)
        
        workflow = get_workflow_state()
        workflow.portfolio_data = sample_portfolio
        workflow.hazard_result = hazard_result
        workflow.financial_result = financial_result
        
        st.success("Demo complete! Navigate through the sidebar to see results.")


def show_data_input_page(currency: str):
    """Data input page."""
    st.markdown("## 📥 Data Input")
    st.markdown("Upload or create portfolio and hazard data")
    
    workflow = get_workflow_state()
    
    tab1, tab2 = st.tabs(["📊 Portfolio Data", "🗺️ Regional Hazard Data"])
    
    with tab1:
        input_method = st.radio("Choose input method", ["Use Sample Portfolio", "Upload CSV", "Manual Entry"])
        
        if input_method == "Use Sample Portfolio":
            portfolio = pd.DataFrame({
                "asset_id": ["HK001", "HK002", "HK003", "HK004", "HK005"],
                "asset_type": ["residential_high_rise", "residential_high_rise", "commercial_office", "industrial_warehouse", "commercial_retail"],
                "district": ["central", "wan_chai", "tst", "kwun_tong", "causeway_bay"],
                "value": [50000000, 30000000, 80000000, 120000000, 60000000],
                "base_pd": [0.015, 0.018, 0.025, 0.035, 0.02],
                "base_lgd": [0.35, 0.38, 0.42, 0.45, 0.4],
                "damage_ratio": [0.12, 0.15, 0.18, 0.28, 0.14],
                "floor": [35, 22, 45, 8, 12],
                "building_age": [8, 15, 5, 20, 25]
            })
            st.dataframe(portfolio, use_container_width=True)
            
        elif input_method == "Upload CSV":
            uploaded = st.file_uploader("Upload Portfolio CSV", type=["csv"])
            if uploaded:
                portfolio = DataProcessor.load_portfolio_csv(uploaded)
                st.dataframe(portfolio, use_container_width=True)
            else:
                st.info("Expected columns: asset_id, value, asset_type, region, base_pd, base_lgd, damage_ratio")
        
        elif input_method == "Manual Entry":
            with st.form("portfolio_entry"):
                n_assets = st.number_input("Number of assets", 1, 100, 5)
                submitted = st.form_submit_button("Create Portfolio")
                
                if submitted:
                    assets = []
                    for i in range(n_assets):
                        c1, c2, c3, c4 = st.columns(4)
                        with c1:
                            asset_id = st.text_input(f"Asset {i+1} ID", f"RE{i+1:03d}")
                        with c2:
                            asset_type = st.selectbox(f"Type", ["residential", "commercial", "industrial"])
                        with c3:
                            region = st.selectbox(f"Region", ["central", "wan_chai", "tst", "kwun_tong", "causeway_bay", "sha_tin", "tuen_mun"])
                        with c4:
                            value = st.number_input(f"Value", 100000, 100000000, 10000000, 100000)
                        assets.append({"asset_id": asset_id, "asset_type": asset_type, "region": region, "value": value, "base_pd": 0.02, "base_lgd": 0.4, "damage_ratio": 0.1})
                    portfolio = pd.DataFrame(assets)
                    st.dataframe(portfolio, use_container_width=True)
        
        if 'portfolio' in dir():
            workflow.portfolio_data = portfolio
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Total Value", f"{portfolio['value'].sum():,.0f} {currency}")
            m2.metric("Number of Assets", len(portfolio))
            m3.metric("Avg PD", f"{portfolio['base_pd'].mean():.2%}")
            m4.metric("Avg LGD", f"{portfolio['base_lgd'].mean():.0%}")
            
            region_summary = portfolio.groupby("district")["value"].sum()
            st.bar_chart(region_summary)
    
    with tab2:
        st.markdown("#### HK Regional Hazard Data")
        region_data = RegionalHazardData()
        selected_region = st.selectbox("Select Region", ["central", "wan_chai", "tst", "kwun_tong", "causeway_bay", "sha_tin", "tuen_mun"])
        
        if st.button("Load Regional Data"):
            hazard_params = region_data.get_regional_hazard_params(region=selected_region, hazard_type="flood", return_period=100)
            st.json(hazard_params)


def show_hazard_page(currency: str):
    """Hazard assessment page."""
    st.markdown("## 🌊 Hazard Assessment")
    st.markdown("Analyze physical damage from climate hazards")
    
    workflow = get_workflow_state()
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("#### Hazard Parameters")
        
        hazard_type = st.selectbox("Hazard Type", ["flood", "wildfire", "cyclone", "drought"])
        
        if hazard_type == "flood":
            intensity = st.slider("Flood Depth (meters)", 0.0, 5.0, 1.0, 0.1)
        elif hazard_type == "wildfire":
            intensity = st.slider("Burn Area (%)", 0, 100, 30, 5)
        elif hazard_type == "cyclone":
            intensity = st.slider("Wind Speed (km/h)", 50, 300, 150, 10)
        else:
            intensity = st.slider("SPI Index", -3.0, 0.0, -1.5, 0.1)
        
        if workflow.portfolio_data is not None:
            selected_asset = st.selectbox("Select Asset", workflow.portfolio_data["asset_id"].tolist())
            asset_data = workflow.portfolio_data[workflow.portfolio_data["asset_id"] == selected_asset].iloc[0]
            asset_value = asset_data["value"]
            asset_type = asset_data["asset_type"]
        else:
            asset_value = st.number_input(f"Asset Value ({currency})", 100000, 100000000, 10000000, 100000)
            asset_type = st.selectbox("Asset Type", ["residential", "commercial", "industrial"])
        
        if hazard_type == "flood":
            duration = st.slider("Flood Duration (hours)", 6, 168, 24, 6)
        else:
            duration = None
        
        if st.button("Calculate Damage"):
            hazard = HazardAssessment()
            if hazard_type == "flood":
                result = hazard.assess_flood_risk(depth_m=intensity, asset_value=asset_value, asset_type=asset_type, duration_hours=duration)
            else:
                result = hazard.assess_hazard(hazard_type=hazard_type, intensity=intensity, asset_value=asset_value, asset_type=asset_type)
            
            workflow.hazard_result = result
            st.success("Damage assessment complete!")
    
    with col2:
        if workflow.hazard_result is not None:
            result = workflow.hazard_result
            
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Damage Ratio", f"{result['damage_ratio']*100:.1f}%")
            m2.metric("Physical Damage", f"{result['physical_damage']:,.0f} {currency}")
            m3.metric("Residual Value", f"{result['residual_value']:,.0f} {currency}")
            m4.metric("Downtime", f"{result.get('downtime_days', 'N/A')} days")
            
            # Damage curve
            fig, ax = plt.subplots(figsize=(10, 4))
            hazard = HazardAssessment()
            
            if hazard_type == "flood":
                depths = np.linspace(0, 4, 100)
                damages = [hazard._flood_damage_curve(d, asset_type) for d in depths]
                ax.plot(depths, damages, 'b-', linewidth=2)
                ax.axvline(x=intensity, color='r', linestyle='--', linewidth=2, label=f'Current: {intensity}m')
                ax.fill_between(depths, damages, alpha=0.3, color='blue')
                ax.set_xlabel('Flood Depth (meters)')
            elif hazard_type == "cyclone":
                speeds = np.linspace(50, 300, 100)
                damages = [hazard._cyclone_damage_curve(s, asset_type) for s in speeds]
                ax.plot(speeds, damages, 'r-', linewidth=2)
                ax.axvline(x=intensity, color='b', linestyle='--', linewidth=2, label=f'Current: {intensity} km/h')
                ax.set_xlabel('Wind Speed (km/h)')
            else:
                ax.plot([0, intensity], [0, 1], 'orange', linewidth=2)
                ax.axvline(x=intensity, color='blue', linestyle='--', linewidth=2)
                ax.set_xlabel('Hazard Intensity')
            
            ax.set_ylabel('Damage Ratio')
            ax.set_title(f'{hazard_type.title()} Damage Function')
            ax.legend()
            ax.grid(True, alpha=0.3)
            ax.set_xlim(0, None)
            ax.set_ylim(0, 1.1)
            st.pyplot(fig)
        else:
            st.info("Configure parameters and click Calculate")


def show_financial_page(currency: str):
    """Financial impact page."""
    st.markdown("## 💰 Financial Impact Analysis")
    st.markdown("Calculate credit risk adjustments and capital impact")
    
    workflow = get_workflow_state()
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("#### Financial Parameters")
        
        base_pd = st.number_input("Base PD", 0.001, 0.5, 0.02, 0.001)
        base_lgd = st.number_input("Base LGD", 0.1, 1.0, 0.4, 0.05)
        climate_beta = st.slider("Climate Sensitivity (β)", 0.0, 1.0, 0.5, 0.05)
        
        if workflow.portfolio_data is not None:
            exposure = workflow.portfolio_data["value"].sum()
        else:
            exposure = st.number_input(f"Exposure ({currency})", 1000000, 1000000000, 100000000, 10000000)
        
        time_horizon = st.slider("Time Horizon (years)", 1, 30, 10, 1)
        
        if workflow.hazard_result is not None:
            damage_ratio = workflow.hazard_result["damage_ratio"]
            st.info(f"Using damage ratio: {damage_ratio:.1%}")
        else:
            damage_ratio = st.slider("Physical Damage Ratio", 0.0, 1.0, 0.25, 0.05)
        
        if st.button("Calculate Financial Impact"):
            vasicek = ClimateVasicek(base_pd=base_pd, base_lgd=base_lgd, climate_beta=climate_beta)
            result = vasicek.run_full_analysis(exposure=exposure, time_horizon=time_horizon, physical_damage_ratio=damage_ratio)
            workflow.financial_result = result
            st.success("Financial analysis complete!")
    
    with col2:
        if workflow.financial_result is not None:
            result = workflow.financial_result
            
            adj = result["climate_adjustment"]
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("PD Multiplier", f"{adj['pd_multiplier']:.2f}x")
            m2.metric("Adjusted PD", f"{adj['adjusted_pd']:.2%}")
            m3.metric("LGD Multiplier", f"{adj['lgd_multiplier']:.2f}x")
            m4.metric("Adjusted LGD", f"{adj['adjusted_lgd']:.0%}")
            
            el = result["expected_loss"]
            ul = result["unexpected_loss"]
            cap = result["capital"]
            
            m5, m6, m7, m8 = st.columns(4)
            m5.metric("Base EL", f"{el['base']:,.0f}")
            m6.metric("Stressed EL", f"{el['stressed']:,.0f}", delta=f"{el['increase_percentage']:.1f}%")
            m7.metric("Base UL", f"{ul['base']:,.0f}")
            m8.metric("Stressed UL", f"{ul['stressed']:,.0f}", delta=f"{ul['increase_percentage']:.1f}%")
            
            m9, m10, m11 = st.columns(3)
            m9.metric("Base Capital", f"{cap['base']:,.0f}")
            m10.metric("Stressed Capital", f"{cap['stressed']:,.0f}")
            m11.metric("Climate Buffer", f"{cap['climate_buffer']:,.0f}")
            
            fig, axes = plt.subplots(1, 3, figsize=(15, 4))
            axes[0].bar(['Base', 'Stressed'], [el['base'], el['stressed']], color=['steelblue', 'coral'])
            axes[0].set_title('Expected Loss')
            axes[1].bar(['Base', 'Stressed'], [ul['base'], ul['stressed']], color=['steelblue', 'coral'])
            axes[1].set_title('Unexpected Loss')
            axes[2].bar(['Base', 'Stressed'], [cap['base'], cap['stressed']], color=['steelblue', 'coral'])
            axes[2].set_title('Capital Requirement')
            st.pyplot(fig)
        else:
            st.info("Configure parameters and click Calculate")


def show_monte_carlo_page(currency: str):
    """Monte Carlo simulation page."""
    st.markdown("## 🎲 Monte Carlo Simulation")
    st.markdown("Run portfolio-level Monte Carlo simulations")
    
    workflow = get_workflow_state()
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("#### Simulation Parameters")
        
        n_simulations = st.number_input("Simulations", 1000, 50000, 10000, 1000)
        time_horizon = st.slider("Time Horizon (years)", 1, 30, 10, 1)
        confidence = st.selectbox("Confidence Level", [0.90, 0.95, 0.99, 0.999], index=1)
        climate_factor = st.slider("Climate Factor", 0.0, 1.0, 0.2, 0.05)
        hazard_type = st.selectbox("Hazard Type", ["flood", "wildfire", "cyclone", "drought"])
        
        if workflow.portfolio_data is not None:
            portfolio = [
                PortfolioAsset(asset_id=row["asset_id"], value=row["value"], asset_type=row["asset_type"], region=row.get("district", row.get("region", "central")), damage_ratio=row.get("damage_ratio", 0.1), climate_beta=0.5)
                for _, row in workflow.portfolio_data.iterrows()
            ]
            st.info(f"Using portfolio with {len(portfolio)} assets")
        else:
            st.warning("Using sample portfolio")
            portfolio = [PortfolioAsset(f"HK_{i}", 50000000, "residential_high_rise", "central", 0.3) for i in range(10)]
        
        if st.button("Run Simulation"):
            config = SimulationConfig(n_simulations=n_simulations, time_horizon=time_horizon, confidence_level=confidence, random_seed=42)
            engine = MonteCarloEngine(config)
            result = engine.run_simulation(assets=portfolio, climate_factor=climate_factor, hazard_type=hazard_type)
            workflow.simulation_result = result
            st.success(f"Completed {n_simulations:,} simulations!")
    
    with col2:
        if workflow.simulation_result is not None:
            result = workflow.simulation_result
            risk = result["risk_metrics"]
            
            m1, m2, m3, m4 = st.columns(4)
            mean_return = result.get("return_distribution", {}).get("mean", 0)
            m1.metric("Mean Return", f"{mean_return*100:.1f}%")
            m2.metric("Value at Risk", f"{risk['value_at_risk']*100:.1f}%")
            m3.metric("Expected Shortfall", f"{risk['expected_shortfall']*100:.1f}%")
            m4.metric("Prob. of Loss", f"{risk['probability_of_loss']*100:.1f}%")
            
            fig, axes = plt.subplots(1, 2, figsize=(14, 5))
            returns_array = result.get("return_distribution_array", np.random.normal(0, 0.15, 10000))
            axes[0].hist(returns_array * 100, bins=50, edgecolor="black", alpha=0.7, color="steelblue")
            axes[0].axvline(x=risk['value_at_risk'] * 100, color='r', linestyle='--', linewidth=2)
            axes[0].axvline(x=risk['expected_shortfall'] * 100, color='orange', linestyle='--', linewidth=2)
            axes[0].set_xlabel('Return (%)')
            axes[0].set_title('Return Distribution')
            axes[0].grid(True, alpha=0.3)
            
            paths = result.get("portfolio_paths", np.random.randn(50, 2520))
            for i in range(min(50, len(paths))):
                axes[1].plot(paths[i] / paths[i, 0], alpha=0.1, color='blue')
            axes[1].axhline(y=1.0, color='black', linestyle='-', linewidth=1)
            axes[1].set_xlabel('Time (days)')
            axes[1].set_title('Portfolio Value Paths')
            st.pyplot(fig)
        else:
            st.info("Configure and click Run Simulation")


def show_scenario_page(currency: str):
    """Scenario analysis page."""
    st.markdown("## 🎭 Scenario Analysis")
    st.markdown("Compare climate risks across different scenarios")
    
    workflow = get_workflow_state()
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("#### Scenario Selection")
        
        framework = ScenarioFramework()
        all_scenarios = framework.get_all_scenarios()
        
        for sid, scen in all_scenarios.items():
            with st.expander(f"{scen.name} ({scen.category})"):
                st.write(f"**Climate Factor:** {scen.climate_factor:.0%}")
                st.write(f"**Temp Rise:** {scen.temperature_rise_2100}°C")
                st.write(f"**Physical Risk:** {scen.physical_risk}")
        
        selected = st.multiselect("Select Scenarios", list(all_scenarios.keys()), default=["orderly_below_2c", "disorderly_divergent", "hot_house_ndc"])
        time_horizon = st.slider("Time Horizon (years)", 5, 50, 10, 5)
        
        if workflow.portfolio_data is not None:
            portfolio = [PortfolioAsset(asset_id=row["asset_id"], value=row["value"], asset_type=row["asset_type"], region=row["region"], climate_beta=0.5) for _, row in workflow.portfolio_data.iterrows()]
        else:
            portfolio = [PortfolioAsset(f"HK_{i}", 50000000, "residential_high_rise", "central", 0.3) for i in range(10)]
        
        if st.button("Compare Scenarios"):
            config = SimulationConfig(n_simulations=5000, time_horizon=time_horizon, random_seed=42)
            engine = MonteCarloEngine(config)
            results = {}
            for sid in selected:
                scen = all_scenarios[sid]
                results[sid] = engine.run_simulation(assets=portfolio, climate_factor=scen.climate_factor, hazard_type=sid)
            workflow.scenario_results = results
            st.success("Scenario comparison complete!")
    
    with col2:
        if workflow.scenario_results is not None:
            results = workflow.scenario_results
            
            comparison_data = []
            for sid, res in results.items():
                risk = res["risk_metrics"]
                scen = all_scenarios[sid]
                comparison_data.append({
                    "Scenario": scen.name,
                    "Category": scen.category,
                    "Mean Return": f"{risk['mean']*100:.1f}%",
                    "VaR (5%)": f"{risk['value_at_risk']*100:.1f}%",
                    "Prob. Loss": f"{risk['probability_of_loss']*100:.1f}%"
                })
            
            st.table(pd.DataFrame(comparison_data))
            
            fig, ax = plt.subplots(figsize=(10, 5))
            x = np.arange(len(results))
            means = [results[s]["risk_metrics"]["mean"] * 100 for s in results]
            var5s = [results[s]["risk_metrics"]["value_at_risk"] * 100 for s in results]
            
            width = 0.35
            ax.bar(x - width/2, means, width, label='Mean Return', color='steelblue')
            ax.bar(x + width/2, var5s, width, label='VaR 5%', color='coral')
            ax.set_ylabel('Return (%)')
            ax.set_title('Scenario Comparison')
            ax.set_xticks(x)
            ax.set_xticklabels([s.replace('_', '\n')[:15] for s in results.keys()], fontsize=8)
            ax.legend()
            ax.grid(True, alpha=0.3)
            st.pyplot(fig)
        else:
            st.info("Select scenarios and click Compare")


def show_reports_page(currency: str):
    """Reports page."""
    st.markdown("## 📄 Reports")
    st.markdown("Generate summary reports and exports")
    
    workflow = get_workflow_state()
    
    # Generate report
    report_sections = []
    
    if workflow.portfolio_data is not None:
        report_sections.append("✅ Portfolio Data Loaded")
    if workflow.hazard_result is not None:
        report_sections.append("✅ Hazard Assessment Complete")
    if workflow.financial_result is not None:
        report_sections.append("✅ Financial Impact Analysis Complete")
    if workflow.simulation_result is not None:
        report_sections.append("✅ Monte Carlo Simulation Complete")
    if workflow.scenario_results is not None:
        report_sections.append("✅ Scenario Analysis Complete")
    
    if report_sections:
        st.markdown("### Report Sections")
        for section in report_sections:
            st.write(f"- {section}")
        
        if st.button("Generate Full Report"):
            report = "=" * 60 + "\nCLIMATE DIGITAL TWIN - ANALYSIS REPORT\n" + "=" * 60 + "\n"
            
            if workflow.financial_result:
                result = workflow.financial_result
                report += f"\nExpected Loss (Base): {result['expected_loss']['base']:,.0f} {currency}\n"
                report += f"Expected Loss (Stressed): {result['expected_loss']['stressed']:,.0f} {currency}\n"
                report += f"Additional EL: {result['expected_loss']['additional']:,.0f} {currency}\n"
                report += f"\nCapital Impact: {result['capital']['additional']:,.0f} {currency}\n"
            
            st.text_area("Report", report, height=300)
    else:
        st.warning("Complete assessments to generate reports.")
# ===== HK Risk Map =====


def show_hk_risk_map_page():
    """HK interactive risk map page."""
    st.markdown("## 🗺️ HK Interactive Risk Map")
    st.markdown("Explore climate risks across Hong Kong districts")
    
    try:
        from utils.hk_map import create_hk_map, list_districts, get_district
        from streamlit_folium import st_folium
        
        # District selector
        selected = st.selectbox("Select District", ["All Districts"] + list_districts())
        
        # Create and display map
        m = create_hk_map()
        st_folium(m, width=900, height=550)
        
        # District details
        if selected != "All Districts":
            district = get_district(selected)
            if district:
                st.markdown(f"### {district.display_name} Details")
                risk = max(district.risk_levels.values(), key=lambda x: ["low", "medium", "high", "very_high"].index(x))
                st.markdown(f"**Overall Risk:** {risk.upper()}")
                for hazard, level in district.risk_levels.items():
                    st.write(f"- {hazard.title()}: {level.upper()}")
                st.write(f"**Population:** {district.population:,}")
                st.write(f"**Avg Property Value:** HKD ${district.avg_property_value_hkd:,.0f}")
    
    except ImportError:
        st.error("Map visualization requires folium and streamlit-folium packages")
        st.info("Install with: pip install folium streamlit-folium")
    except Exception as e:
        st.warning("Map temporarily unavailable")


def main():
    """Main application."""
    currency = show_sidebar()
    
    # Page navigation
    if "nav_page" not in st.session_state:
        st.session_state.nav_page = "home"
    page = st.session_state.nav_page
    
    # Pages that need currency parameter
    main_pages = {
        "home": show_home_page,
        "data": show_data_input_page,
        "hazard": show_hazard_page,
        "financial": show_financial_page,
        "monte_carlo": show_monte_carlo_page,
        "scenario": show_scenario_page,
        "hk_map": show_hk_risk_map_page,
        "reports": show_reports_page,
    }
    
    if page in main_pages:
        if page == "home":
            show_home_page(currency)
        else:
            main_pages[page](currency)
    else:
        show_home_page()


if __name__ == "__main__":
    main()
