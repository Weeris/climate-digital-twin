"""
Real-time Climate Data API Integration

Supports:
- Open-Meteo: Free historical and forecast weather data
- OpenWeatherMap: Current conditions (API key required)

Usage:
    from utils.climate_api import ClimateAPIClient
    
    client = ClimateAPIClient()
    data = client.get_current_weather("Hong Kong")
"""

import asyncio
import aiohttp
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class WeatherData:
    """Current weather data."""
    location: str
    temperature_c: float
    humidity_percent: float
    wind_speed_kmh: float
    wind_direction: str
    pressure_hpa: float
    precipitation_mm: float
    cloud_cover_percent: float
    weather_description: str
    timestamp: datetime


@dataclass
class ClimateData:
    """Climate/hazard data derived from weather."""
    flood_risk: str
    drought_index: float
    heat_stress_level: str
    tropical_cyclone_risk: str
    raw_weather: WeatherData


class ClimateAPIClient:
    """Unified client for climate data APIs."""
    
    def __init__(self, owm_api_key: Optional[str] = None):
        """
        Initialize API client.
        
        Args:
            owm_api_key: OpenWeatherMap API key (optional)
        """
        self.owm_api_key = owm_api_key
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close(self):
        """Close the aiohttp session."""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def get_current_weather(self, location: str = "Hong Kong") -> Optional[WeatherData]:
        """
        Get current weather from Open-Meteo (free, no API key).
        
        Args:
            location: Location name (HK coordinates used by default)
            
        Returns:
            WeatherData or None if API call fails
        """
        # Hong Kong coordinates
        hk_coords = {
            "Hong Kong": (22.3193, 114.1694),
            "Central": (22.2823, 114.1589),
            "Wan Chai": (22.2816, 114.1725),
            "TST": (22.3039, 114.1704),
            "Kwun Tong": (22.3124, 114.2248),
            "Sha Tin": (22.3894, 114.2034),
            "Tuen Mun": (22.3909, 113.9728),
        }
        
        lat, lon = hk_coords.get(location, hk_coords["Hong Kong"])
        
        try:
            session = await self._get_session()
            
            # Open-Meteo Free API
            url = (
                f"https://api.open-meteo.com/v1/forecast?"
                f"latitude={lat}&longitude={lon}"
                f"&current=temperature_2m,relative_humidity_2m,precipitation,"
                f"surface_pressure,wind_speed_10m,wind_direction_10m,cloud_cover"
                f"&timezone=Asia/Hong_Kong"
            )
            
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    current = data.get("current", {})
                    
                    # Map wind direction
                    wd = current.get("wind_direction_10m", 0)
                    directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
                    wind_dir = directions[int((wd + 22.5) / 45) % 8] if wd else "Calm"
                    
                    return WeatherData(
                        location=location,
                        temperature_c=current.get("temperature_2m", 0),
                        humidity_percent=current.get("relative_humidity_2m", 0),
                        wind_speed_kmh=current.get("wind_speed_10m", 0),
                        wind_direction=wind_dir,
                        pressure_hpa=current.get("surface_pressure", 0),
                        precipitation_mm=current.get("precipitation", 0),
                        cloud_cover_percent=current.get("cloud_cover", 0),
                        weather_description="Clear/Cloudy",
                        timestamp=datetime.now()
                    )
                else:
                    return None
        except Exception as e:
            print(f"Weather API error: {e}")
            return None
    
    async def get_historical_weather(
        self, 
        location: str = "Hong Kong",
        days: int = 30
    ) -> Optional[List[Dict]]:
        """
        Get historical weather data from Open-Meteo.
        
        Args:
            location: Location name
            days: Number of days of historical data
            
        Returns:
            List of daily weather records or None
        """
        hk_coords = {
            "Hong Kong": (22.3193, 114.1694),
        }
        
        lat, lon = hk_coords.get(location, hk_coords["Hong Kong"])
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        try:
            session = await self._get_session()
            
            url = (
                f"https://archive-api.open-meteo.com/v1/archive?"
                f"latitude={lat}&longitude={lon}"
                f"&start_date={start_date.strftime('%Y-%m-%d')}"
                f"&end_date={end_date.strftime('%Y-%m-%d')}"
                f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,"
                f"wind_speed_max,humidity_mean"
                f"&timezone=Asia/Hong_Kong"
            )
            
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("daily", {})
                return None
        except Exception as e:
            print(f"Historical weather API error: {e}")
            return None
    
    def calculate_drought_index(self, weather_data: WeatherData) -> float:
        """
        Calculate simple drought index based on recent conditions.
        
        Returns:
            SPI-like index: negative = drier, positive = wetter
        """
        base_temp = 25
        base_rain = 5
        
        temp_factor = (weather_data.temperature_c - base_temp) / 30
        rain_factor = (weather_data.precipitation_mm - base_rain) / 10
        
        drought_index = -rain_factor + (temp_factor * 0.3)
        return round(drought_index, 2)
    
    def assess_climate_risk(self, weather_data: WeatherData) -> ClimateData:
        """Assess climate risk based on current weather."""
        if weather_data.precipitation_mm > 20:
            flood_risk = "High"
        elif weather_data.precipitation_mm > 5:
            flood_risk = "Medium"
        else:
            flood_risk = "Low"
        
        drought_index = self.calculate_drought_index(weather_data)
        
        if weather_data.temperature_c > 35:
            heat_stress = "Extreme"
        elif weather_data.temperature_c > 30:
            heat_stress = "High"
        elif weather_data.temperature_c > 25:
            heat_stress = "Moderate"
        else:
            heat_stress = "Low"
        
        if weather_data.wind_speed_kmh > 63:
            tc_risk = "Signal 8+"
        elif weather_data.wind_speed_kmh > 41:
            tc_risk = "Signal 3"
        else:
            tc_risk = "None"
        
        return ClimateData(
            flood_risk=flood_risk,
            drought_index=drought_index,
            heat_stress_level=heat_stress,
            tropical_cyclone_risk=tc_risk,
            raw_weather=weather_data
        )


# Convenience functions for Streamlit
def get_weather_sync(location: str = "Hong Kong") -> Optional[WeatherData]:
    """Get weather synchronously (for Streamlit)."""
    client = ClimateAPIClient()
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        weather = loop.run_until_complete(client.get_current_weather(location))
        loop.run_until_complete(client.close())
        return weather
    except Exception:
        return None


def get_climate_risk_sync(location: str = "Hong Kong") -> Optional[ClimateData]:
    """Get climate risk assessment synchronously."""
    weather = get_weather_sync(location)
    if weather:
        client = ClimateAPIClient()
        return client.assess_climate_risk(weather)
    return None
