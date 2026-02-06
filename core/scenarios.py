"""
Scenario Framework Module

Forward-looking climate scenario definitions and projections.

Supports:
- Standardized scenario framework
- Time-horizon based projections
- Hazard intensity evolution
"""

from typing import Dict, List
from dataclasses import dataclass


@dataclass
class ScenarioDefinition:
    """Climate scenario definition."""
    name: str
    category: str  # orderly, disorderly, hot_house
    climate_factor: float
    description: str
    temperature_rise_2100: float
    transition_risk: str
    physical_risk: str


class ScenarioFramework:
    """
    Climate scenario framework provider.
    
    Provides standardized scenarios for forward-looking
    climate risk assessment.
    """
    
    # Standardized scenarios
    SCENARIOS = {
        "orderly_net_zero": {
            "name": "Orderly - Net Zero 2050",
            "category": "orderly",
            "climate_factor": 0.15,
            "description": "Immediate coordinated climate policy action",
            "temperature_rise_2100": 1.5,
            "transition_risk": "Low",
            "physical_risk": "Medium-Low"
        },
        "orderly_below_2c": {
            "name": "Orderly - Below 2°C",
            "category": "orderly",
            "climate_factor": 0.20,
            "description": "Below 2°C pathway with coordinated action",
            "temperature_rise_2100": 1.8,
            "transition_risk": "Low-Medium",
            "physical_risk": "Medium"
        },
        "disorderly_divergent": {
            "name": "Disorderly - Divergent Net Zero",
            "category": "disorderly",
            "climate_factor": 0.30,
            "description": "Uneven transition across regions",
            "temperature_rise_2100": 2.0,
            "transition_risk": "High",
            "physical_risk": "Medium-High"
        },
        "disorderly_delayed": {
            "name": "Disorderly - Delayed Transition",
            "category": "disorderly",
            "climate_factor": 0.35,
            "description": "Delayed policy action followed by rapid transition",
            "temperature_rise_2100": 2.2,
            "transition_risk": "High",
            "physical_risk": "High"
        },
        "hot_house_ndc": {
            "name": "Hot House - Nationally Determined Contributions",
            "category": "hot_house",
            "climate_factor": 0.50,
            "description": "Current policy commitments only",
            "temperature_rise_2100": 3.0,
            "transition_risk": "Low",
            "physical_risk": "High"
        },
        "hot_house_current": {
            "name": "Hot House - Current Policies",
            "category": "hot_house",
            "climate_factor": 0.60,
            "description": "No additional climate policy action",
            "temperature_rise_2100": 3.5,
            "transition_risk": "Low",
            "physical_risk": "Very High"
        }
    }
    
    # Hazard projections by scenario (% change from baseline)
    HAZARD_PROJECTIONS = {
        "orderly_net_zero": {
            "flood_frequency": "+10%",
            "flood_intensity": "+15%",
            "wildfire_area": "+20%",
            "drought_severity": "+15%",
            "cyclone_frequency": "+5%",
            "sea_level_rise_cm": 25
        },
        "orderly_below_2c": {
            "flood_frequency": "+15%",
            "flood_intensity": "+20%",
            "wildfire_area": "+30%",
            "drought_severity": "+25%",
            "cyclone_frequency": "+10%",
            "sea_level_rise_cm": 35
        },
        "disorderly_divergent": {
            "flood_frequency": "+25%",
            "flood_intensity": "+35%",
            "wildfire_area": "+45%",
            "drought_severity": "+40%",
            "cyclone_frequency": "+15%",
            "sea_level_rise_cm": 50
        },
        "hot_house_ndc": {
            "flood_frequency": "+50%",
            "flood_intensity": "+70%",
            "wildfire_area": "+80%",
            "drought_severity": "+70%",
            "cyclone_frequency": "+30%",
            "sea_level_rise_cm": 80
        },
        "hot_house_current": {
            "flood_frequency": "+70%",
            "flood_intensity": "+100%",
            "wildfire_area": "+120%",
            "drought_severity": "+100%",
            "cyclone_frequency": "+40%",
            "sea_level_rise_cm": 110
        }
    }
    
    def get_scenario(self, scenario_id: str) -> ScenarioDefinition:
        """
        Get scenario definition by ID.
        
        Args:
            scenario_id: Scenario identifier
            
        Returns:
            ScenarioDefinition object
        """
        data = self.SCENARIOS.get(scenario_id, self.SCENARIOS["orderly_below_2c"])
        
        return ScenarioDefinition(
            name=data["name"],
            category=data["category"],
            climate_factor=data["climate_factor"],
            description=data["description"],
            temperature_rise_2100=data["temperature_rise_2100"],
            transition_risk=data["transition_risk"],
            physical_risk=data["physical_risk"]
        )
    
    def get_all_scenarios(self) -> Dict[str, ScenarioDefinition]:
        """Get all available scenarios."""
        return {
            sid: self.get_scenario(sid)
            for sid in self.SCENARIOS
        }
    
    def get_scenarios_by_category(self, category: str) -> Dict[str, ScenarioDefinition]:
        """Get scenarios by category."""
        return {
            sid: self.get_scenario(sid)
            for sid, data in self.SCENARIOS.items()
            if data["category"] == category
        }
    
    def project_hazard_parameters(
        self,
        scenario_id: str,
        hazard_type: str,
        time_horizon: int,
        baseline_intensity: float
    ) -> Dict:
        """
        Project hazard intensity over time horizon.
        
        Args:
            scenario_id: Climate scenario
            hazard_type: Type of hazard
            time_horizon: Years from baseline
            baseline_intensity: Current hazard intensity
            
        Returns:
            Projected hazard parameters
        """
        scenario = self.get_scenario(scenario_id)
        projections = self.HAZARD_PROJECTIONS.get(
            scenario_id, self.HAZARD_PROJECTIONS["orderly_below_2c"]
        )
        
        # Time scaling (linear approximation)
        year_fraction = time_horizon / 26  # 2024 to 2050 baseline
        
        # Get hazard-specific projection
        hazard_mapping = {
            "flood": ("flood_frequency", "flood_intensity"),
            "wildfire": ("wildfire_area",),
            "cyclone": ("cyclone_frequency",),
            "drought": ("drought_severity",)
        }
        
        keys = hazard_mapping.get(hazard_type, ["flood_frequency"])
        intensity_key = keys[0]
        
        # Calculate projected multiplier
        base_multiplier = 1.0
        projection_str = projections.get(intensity_key, "+0%")
        
        if projection_str.startswith("+"):
            pct_change = float(projection_str[1:-1]) / 100
            base_multiplier = 1.0 + pct_change * year_fraction
        
        # Temperature scaling
        temp_factor = 1.0 + (
            (scenario.temperature_rise_2100 - 1.5) / 2.0
        ) * year_fraction
        
        return {
            "scenario": scenario_id,
            "scenario_name": scenario.name,
            "category": scenario.category,
            "hazard_type": hazard_type,
            "time_horizon": time_horizon,
            "baseline_intensity": baseline_intensity,
            "projected_intensity": baseline_intensity * base_multiplier * temp_factor,
            "intensity_multiplier": base_multiplier * temp_factor,
            "temperature_rise": scenario.temperature_rise_2100 * year_fraction,
            "physical_risk_profile": scenario.physical_risk,
            "full_projection": projections
        }
    
    def get_hazard_curves(self, scenario_id: str, hazard_type: str) -> Dict:
        """
        Get hazard intensity curves for scenario.
        
        Returns dictionary of hazard intensity at different return periods.
        """
        projections = self.HAZARD_PROJECTIONS.get(
            scenario_id, self.HAZARD_PROJECTIONS["orderly_below_2c"]
        )
        
        base_depths = {
            "flood": {
                10: 0.3,
                25: 0.5,
                50: 0.8,
                100: 1.2,
                200: 1.8,
                500: 2.5
            }
        }
        
        hazard_base = base_depths.get(hazard_type, base_depths["flood"])
        
        # Apply scenario multiplier
        multiplier_str = projections.get("flood_intensity", "+0%")
        if multiplier_str.startswith("+"):
            multiplier = 1.0 + float(multiplier_str[1:-1]) / 100
        else:
            multiplier = 1.0
        
        return {
            scenario_id: {
                rp: depth * multiplier
                for rp, depth in hazard_base.items()
            }
        }


# Convenience function
def get_framework() -> ScenarioFramework:
    """Get scenario framework instance."""
    return ScenarioFramework()
