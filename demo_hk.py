"""
HK Dashboard Demo Script

Demonstrates Hong Kong dashboard features including:
- Interactive risk map
- Property value calculator
- Damage assessment tool
- Financial analysis

Run: streamlit run demo_hk.py
"""

import streamlit as st
import pandas as pd

# Import HK modules
from utils.hk_map import HKMapVisualizer, list_districts, get_district, create_hk_map
from core.hk_property_values import HKPropertyValues
from core.hk_damage_functions import HKBuildingDamageFunctions, HKBuildingType


def show_header():
    """Show HK dashboard header."""
    st.markdown("""
    <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #1E88E5 0%, #0D47A1 100%); 
                border-radius: 10px; margin-bottom: 20px;">
        <h1 style="color: white; margin: 0;">🇭🇰 Hong Kong Climate Digital Twin</h1>
        <p style="color: #E3F2FD; margin: 10px 0 0 0;">Climate Risk Assessment Dashboard</p>
    </div>
    """, unsafe_allow_html=True)


def show_district_overview():
    """Show district risk overview."""
    st.markdown("## 📊 District Risk Overview")
    
    districts = list_districts()
    data = []
    for d in districts:
        district = get_district(d)
        if district:
            risk = max(district.risk_levels.values(), key=lambda x: ["low", "medium", "high", "very_high"].index(x))
            data.append({
                "District": district.display_name,
                "Flood": district.risk_levels["flood"].title(),
                "Typhoon": district.risk_levels["typhoon"].title(),
                "Wildfire": district.risk_levels["wildfire"].title(),
                "Drought": district.risk_levels["drought"].title(),
                "Avg Property (HKD)": f"${district.avg_property_value_hkd/1e6:.1f}M",
                "Population": f"{district.population:,}"
            })
    
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)


def show_property_calculator():
    """Show property value calculator."""
    st.markdown("## 🏠 Property Value Calculator")
    
    pv = HKPropertyValues()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        district = st.selectbox("District", pv.get_district_list())
    with col2:
        building_type = st.selectbox("Building Type", ["residential_apartment", "commercial_office", "commercial_retail"])
    with col3:
        area_sqft = st.number_input("Area (sqft)", 200, 5000, 800)
    
    col4, col5, col6 = st.columns(3)
    with col4:
        floor = st.number_input("Floor", 1, 80, 20)
    with col5:
        view = st.selectbox("View", ["city", "sea", "mountain", "park", "none"])
    with col6:
        age = st.number_input("Building Age (years)", 0, 50, 10)
    
    if st.button("Calculate Value"):
        result = pv.calculate_property_value(district, building_type, area_sqft, floor, view, age)
        if "error" not in result:
            st.success(f"**Estimated Value: HKD ${result['total_value_hkd']:,.0f}**")
            st.markdown(f"""
            - Base Price: ${result['base_price_sqft_hkd']:,.0f}/sqft
            - Floor Premium: {result['floor_premium_factor']:.2f}x
            - View Premium: {result['view_premium_factor']:.2f}x
            - Age Factor: {result['age_depreciation_factor']:.2f}x
            """)


def show_damage_calculator():
    """Show damage assessment calculator."""
    st.markdown("## 🌊 Damage Assessment Tool")
    
    df = HKBuildingDamageFunctions()
    
    col1, col2 = st.columns(2)
    with col1:
        building_type = st.selectbox("Building Type", [e.value for e in HKBuildingType])
    with col2:
        flood_depth = st.slider("Flood Depth (m)", 0.0, 5.0, 1.0, 0.1)
    
    col3, col4 = st.columns(2)
    with col3:
        building_value = st.number_input("Building Value (HKD)", 1000000, 100000000, 20000000, 1000000)
    with col4:
        num_floors = st.number_input("Number of Floors", 1, 80, 30)
    
    has_basement = st.checkbox("Has Basement")
    
    if st.button("Calculate Damage"):
        result = df.assess_flood_damage(
            building_type=HKBuildingType.RESIDENTIAL_HIGH_RISE,
            flood_depth_m=flood_depth,
            building_value_hkd=building_value,
            num_floors=num_floors,
            has_basement=has_basement
        )
        
        st.error(f"**Damage Ratio: {result.damage_ratio:.1%}**")
        st.markdown(f"""
        - Physical Damage: HKD ${result.physical_damage_hkd:,.0f}
        - Repair Cost: HKD ${result.repair_cost_hkd:,.0f}
        - Downtime: {result.downtime_days} days
        - Affected Floors: {result.affected_floors}
        """)


def show_map_demo():
    """Show interactive map demo."""
    st.markdown("## 🗺️ Interactive Risk Map")
    
    try:
        m = create_hk_map()
        st_folium(m, width=800, height=500)
    except Exception as e:
        st.warning("Map visualization requires folium and streamlit-folium packages")
        st.info("Install with: pip install folium streamlit-folium")


def main():
    """Main demo function."""
    st.set_page_config(page_title="HK Climate Dashboard Demo", page_icon="🇭🇰", layout="wide")
    
    show_header()
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "🏠 Property", "🌊 Damage", "🗺️ Map"])
    
    with tab1:
        show_district_overview()
    
    with tab2:
        show_property_calculator()
    
    with tab3:
        show_damage_calculator()
    
    with tab4:
        show_map_demo()
    
    st.markdown("---")
    st.markdown("*HK Climate Digital Twin - Phase 4 Demo*")


if __name__ == "__main__":
    main()
