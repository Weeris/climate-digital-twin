"""
HK Map Visualization Module

Interactive Folium map visualization for Hong Kong climate risk assessment.
Provides district-level risk mapping with hazard layer toggles and property markers.

Author: Climate Digital Twin Team
Version: 1.0.0
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import folium

# Default coordinates for Hong Kong
HK_CENTER = [22.3193, 114.1694]  # Victoria Harbour
HK_ZOOM = 11

# Risk level colors
RISK_COLORS = {
    "very_high": "#FF0000",
    "high": "#FF6600",
    "medium": "#FFCC00",
    "low": "#00CC00",
}


@dataclass
class HKDistrict:
    """Hong Kong district with risk data."""
    name: str
    display_name: str
    coordinates: Tuple[float, float]
    risk_levels: Dict[str, str]
    avg_property_value_hkd: float
    population: Optional[int] = None


# District data with coordinates and risk levels
DISTRICTS: Dict[str, HKDistrict] = {
    "central": HKDistrict("central", "Central", (22.2823, 114.1589),
        {"flood": "high", "typhoon": "high", "wildfire": "low", "drought": "medium"},
        28000000, 132000),
    "wan_chai": HKDistrict("wan_chai", "Wan Chai", (22.2816, 114.1725),
        {"flood": "high", "typhoon": "high", "wildfire": "low", "drought": "medium"},
        24000000, 152000),
    "causeway_bay": HKDistrict("causeway_bay", "Causeway Bay", (22.2793, 114.1821),
        {"flood": "high", "typhoon": "high", "wildfire": "low", "drought": "medium"},
        25000000, 183000),
    "tsim_sha_tsui": HKDistrict("tsim_sha_tsui", "Kowloon TST", (22.3039, 114.1704),
        {"flood": "high", "typhoon": "high", "wildfire": "low", "drought": "medium"},
        22000000, 164000),
    "hung_hom": HKDistrict("hung_hom", "Hung Hom", (22.3033, 114.1817),
        {"flood": "medium", "typhoon": "high", "wildfire": "low", "drought": "medium"},
        18000000, 116000),
    "kwun_tong": HKDistrict("kwun_tong", "Kwun Tong", (22.3124, 114.2248),
        {"flood": "medium", "typhoon": "medium", "wildfire": "low", "drought": "low"},
        16000000, 689000),
    "sha_tin": HKDistrict("sha_tin", "Sha Tin", (22.3894, 114.2034),
        {"flood": "medium", "typhoon": "medium", "wildfire": "medium", "drought": "medium"},
        17000000, 686000),
    "tuen_mun": HKDistrict("tuen_mun", "Tuen Mun", (22.3909, 113.9728),
        {"flood": "very_high", "typhoon": "high", "wildfire": "medium", "drought": "high"},
        14000000, 507000),
    "yuen_long": HKDistrict("yuen_long", "Yuen Long", (22.4445, 114.0221),
        {"flood": "very_high", "typhoon": "high", "wildfire": "medium", "drought": "high"},
        13000000, 614000),
    "tin_shui_wai": HKDistrict("tin_shui_wai", "Tin Shui Wai", (22.4623, 113.9968),
        {"flood": "very_high", "typhoon": "high", "wildfire": "low", "drought": "high"},
        12000000, 287000),
    "lantau": HKDistrict("lantau", "Lantau (Tung Chung)", (22.2886, 113.9356),
        {"flood": "medium", "typhoon": "high", "wildfire": "medium", "drought": "low"},
        15000000, 112000),
    "cheung_chau": HKDistrict("cheung_chau", "Cheung Chau", (22.2256, 114.0275),
        {"flood": "medium", "typhoon": "high", "wildfire": "low", "drought": "low"},
        12000000, 23000),
}


def _get_overall_risk(risks: Dict[str, str]) -> str:
    """Get overall risk level (highest of all hazards)."""
    order = ["very_high", "high", "medium", "low"]
    max_risk = "low"
    for r in risks.values():
        if order.index(r) > order.index(max_risk):
            max_risk = r
    return max_risk


def create_hk_map() -> folium.Map:
    """Create Hong Kong climate risk map."""
    m = folium.Map(location=HK_CENTER, zoom_start=HK_ZOOM, tiles="cartodbpositron", control_scale=True)
    
    title_html = '''<div style="position: fixed; top: 10px; left: 50%; transform: translateX(-50%); z-index: 9999; background: white; padding: 10px 20px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.3);"><h3 style="margin: 0; color: #1E88E5;">🇭🇰 Hong Kong Climate Risk Map</h3></div>'''
    m.get_root().html.add_child(folium.Element(title_html))
    
    districts_fg = folium.FeatureGroup(name="📍 Districts")
    properties_fg = folium.FeatureGroup(name="🏠 Properties")
    
    color_map = {"very_high": "red", "high": "orange", "medium": "lightorange", "low": "green"}
    
    for key, d in DISTRICTS.items():
        risk = _get_overall_risk(d.risk_levels)
        popup = f"""<b>{d.display_name}</b><br>Risk: {risk.upper()}<br>Pop: {d.population:,}<br>Avg Property: HKD ${d.avg_property_value_hkd/1e6:.1f}M"""
        folium.Marker(
            location=list(d.coordinates),
            popup=popup,
            tooltip=f"{d.display_name} - {risk.upper()}",
            icon=folium.Icon(color=color_map.get(risk, "gray")),
        ).add_to(districts_fg)
    
    m.add_child(districts_fg)
    m.add_child(properties_fg)
    folium.LayerControl().add_to(m)
    
    legend = '''<div style="position: fixed; bottom: 50px; right: 50px; background: white; padding: 15px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.3); font-size: 12px;"><h4 style="margin: 0 0 10px 0;">Risk Level</h4><div style="margin: 3px 0;"><span style="background:#FF0000;width:15px;height:15px;display:inline-block;margin-right:8px;"></span>Very High</div><div style="margin: 3px 0;"><span style="background:#FF6600;width:15px;height:15px;display:inline-block;margin-right:8px;"></span>High</div><div style="margin: 3px 0;"><span style="background:#FFCC00;width:15px;height:15px;display:inline-block;margin-right:8px;"></span>Medium</div><div style="margin: 3px 0;"><span style="background:#00CC00;width:15px;height:15px;display:inline-block;margin-right:8px;"></span>Low</div></div>'''
    m.get_root().html.add_child(folium.Element(legend))
    
    return m


def get_district(name: str) -> Optional[HKDistrict]:
    """Get district by name."""
    return DISTRICTS.get(name.lower())


def list_districts() -> List[str]:
    """List all districts."""
    return list(DISTRICTS.keys())


def get_district_options() -> List[Tuple[str, str]]:
    """Get district options for dropdowns."""
    return [(k, v.display_name) for k, v in DISTRICTS.items()]