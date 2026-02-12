"""
HK Climate Digital Twin - Quick Demo

Simplified demo of HK climate risk features using tabs.
For full features, use: streamlit run app.py

Run: streamlit run demo_hk.py
"""

import streamlit as st
import pandas as pd
from utils.hk_map import list_districts, get_district, create_hk_map
from core.hk_property_values import HKPropertyValues
from core.hk_damage_functions import HKBuildingDamageFunctions, HKBuildingType


def show_header():
    """Show HK dashboard header."""
    st.markdown("""
    <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #1E88E5 0%, #0D47A1 100%); 
                border-radius: 10px; margin-bottom: 20px;">
        <h1 style="color: white; margin: 0;">🇭🇰 HK Climate Digital Twin</h1>
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
            data.append({
                "District": district.display_name,
                "Flood": district.risk_levels["flood"].title(),
                "Typhoon": district.risk_levels["typhoon"].title(),
                "Avg Property": f"${district.avg_property_value_hkd/1e6:.1f}M"
            })
    
    st.dataframe(pd.DataFrame(data), use_container_width=True)


def show_property_calculator():
    """Show property value calculator."""
    st.markdown("## 🏠 Property Value Calculator")
    
    pv = HKPropertyValues()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        district = st.selectbox("District", pv.get_district_list())
    with col2:
        building_type = st.selectbox("Type", ["residential_apartment", "commercial_office"])
    with col3:
        area_sqft = st.number_input("Area (sqft)", 200, 5000, 800)
    
    col4, col5, col6 = st.columns(3)
    with col4:
        floor = st.number_input("Floor", 1, 80, 20)
    with col5:
        view = st.selectbox("View", ["city", "sea", "mountain", "park"])
    with col6:
        age = st.number_input("Age (years)", 0, 50, 10)
    
    if st.button("Calculate"):
        result = pv.calculate_property_value(district, building_type, area_sqft, floor, view, age)
        if "error" not in result:
            st.success(f"**HKD ${result['total_value_hkd']:,.0f}**")


def show_damage_calculator():
    """Show damage assessment calculator."""
    st.markdown("## 🌊 Damage Assessment")
    
    df = HKBuildingDamageFunctions()
    
    col1, col2 = st.columns(2)
    with col1:
        building_type = st.selectbox("Building", [e.value for e in HKBuildingType])
    with col2:
        flood_depth = st.slider("Flood Depth (m)", 0.0, 5.0, 1.0, 0.1)
    
    col3, col4 = st.columns(2)
    with col3:
        building_value = st.number_input("Value (HKD)", 1000000, 100000000, 20000000)
    with col4:
        num_floors = st.number_input("Floors", 1, 80, 30)
    
    if st.button("Calculate Damage"):
        result = df.assess_flood_damage(
            building_type=HKBuildingType.RESIDENTIAL_HIGH_RISE,
            flood_depth_m=flood_depth,
            building_value_hkd=building_value,
            num_floors=num_floors
        )
        st.error(f"**Damage: {result.damage_ratio:.1%}** = HKD {result.physical_damage_hkd:,.0f}")


def show_map_demo():
    """Show interactive map."""
    st.markdown("## 🗺️ Interactive Risk Map")
    try:
        from streamlit_folium import st_folium
        st_folium(create_hk_map(), width=800, height=500)
    except ImportError:
        st.warning("Install: pip install folium streamlit-folium")


def main():
    """Main demo function."""
    st.set_page_config(page_title="HK Climate Demo", page_icon="🇭🇰", layout="wide")
    
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
    
    st.markdown("*For full features: streamlit run app.py*")


if __name__ == "__main__":
    main()
