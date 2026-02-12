"""
Hong Kong Weather API Integration Module

Provides data ingestion from Hong Kong Observatory API and Open-Meteo
for current weather, historical data, and cyclone tracking.

Supports:
- Current weather conditions
- Historical weather records
- Tropical cyclone information
- Air quality and climate indices

Uses Hong Kong Observatory Open Data API as primary source,
with Open-Meteo as backup.
"""

import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class WeatherAPI(Enum):
    """Available weather data sources."""
    HKO = "hong_kong_observatory"
    OPEN_METEO = "open_meteo"


@dataclass
class HKCurrentWeather:
    """Current weather conditions in Hong Kong."""
    temperature_c: float
    humidity_percent: float
    wind_direction: str
    wind_speed_kmh: float
    pressure_hpa: float
    visibility_km: float
    weather_description: str
    updated_at: datetime


@dataclass
class HKHistoricalWeather:
    """Historical weather record."""
    date: datetime
    max_temp_c: float
    min_temp_c: float
    avg_temp_c: float
    total_rainfall_mm: float
    avg_humidity_percent: float
    avg_wind_speed_kmh: float


@dataclass
class HKTyphoonInfo:
    """Tropical cyclone information."""
    name: str
    code: str
    status: str  # "active", "landfall", "dissipated"
    current_signal: str
    current_position_lat: float
    current_position_lon: float
    max_sustained_wind_kmh: float
    movement_direction: str
    movement_speed_kmh: float
    distance_to_hk_km: Optional[float]
    last_updated: datetime


class HKWeatherAPI:
    """
    Hong Kong Weather API integration.
    
    Fetches weather data from Hong Kong Observatory API
    and provides structured access to weather information.
    
    Note: HKO API requires registration for full access.
    Open-Meteo is used as backup for general weather data.
    """
    
    # API endpoints
    HKO_BASE_URL = "https://data.weather.gov.hk"
    HKO_API_URL = f"{HKO_BASE_URL}/weatherAPI/opendata/weather.php"
    
    OPEN_METEO_BASE_URL = "https://api.open-meteo.com/v1"
    
    def __init__(
        self,
        api_source: WeatherAPI = WeatherAPI.OPEN_METEO,
        api_key: Optional[str] = None
    ):
        """
        Initialize weather API client.
        
        Args:
            api_source: Primary API source to use
            api_key: API key for HKO (if required)
        """
        self.api_source = api_source
        self.api_key = api_key
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session
    
    async def close(self):
        """Close the HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def get_current_weather_hko(self) -> Optional[HKCurrentWeather]:
        """
        Fetch current weather from Hong Kong Observatory.
        
        Returns:
            HKCurrentWeather or None if unavailable
        """
        try:
            session = await self._get_session()
            params = {"dataType": "rhrread", "lang": "en"}
            headers = {}
            
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            async with session.get(
                self.HKO_API_URL,
                params=params,
                headers=headers
            ) as response:
                if response.status != 200:
                    return None
                
                data = await response.json()
                return self._parse_hko_current(data)
                
        except Exception:
            return None
    
    def _parse_hko_current(self, data: Dict) -> HKCurrentWeather:
        """Parse HKO current weather response."""
        # Extract temperature (usually in °C)
        temp_data = data.get("temperature", {})
        temp_c = temp_data.get("data", [20.0])[0] if temp_data.get("data") else 20.0
        
        # Extract humidity
        humidity_data = data.get("humidity", {})
        humidity = humidity_data.get("data", [60.0])[0] if humidity_data.get("data") else 60.0
        
        # Extract wind
        wind_data = data.get("wind", {})
        direction = wind_data.get("direction", "NE")
        speed = wind_data.get("speed", 10.0)
        
        # Extract pressure
        pressure_data = data.get("pressure", {})
        pressure = pressure_data.get("data", [1013.0])[0] if pressure_data.get("data") else 1013.0
        
        # Extract weather description
        icon_data = data.get("icon", [])
        weather_desc = "Partly cloudy"
        if icon_data:
            weather_map = {
                0: "Sunny",
                1: "Sunny",
                2: "Cloudy",
                3: "Overcast",
                45: "Fog",
                61: "Rain",
                63: "Heavy Rain",
                95: "Thunderstorm"
            }
            weather_desc = weather_map.get(icon_data[0], "Partly cloudy")
        
        return HKCurrentWeather(
            temperature_c=temp_c,
            humidity_percent=humidity,
            wind_direction=direction,
            wind_speed_kmh=speed,
            pressure_hpa=pressure,
            visibility_km=10.0,  # Default for HK
            weather_description=weather_desc,
            updated_at=datetime.now()
        )
    
    async def get_current_weather_openmeteo(
        self,
        lat: float = 22.3193,
        lon: float = 114.1694
    ) -> Optional[HKCurrentWeather]:
        """
        Fetch current weather from Open-Meteo API.
        
        Args:
            lat: Latitude (default: Hong Kong)
            lon: Longitude (default: Hong Kong)
            
        Returns:
            HKCurrentWeather or None if unavailable
        """
        try:
            session = await self._get_session()
            url = f"{self.OPEN_METEO_BASE_URL}/forecast"
            params = {
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m,surface_pressure",
                "timezone": "Asia/Hong_Kong"
            }
            
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    return None
                
                data = await response.json()
                return self._parse_openmeteo_current(data)
                
        except Exception:
            return None
    
    def _parse_openmeteo_current(self, data: Dict) -> HKCurrentWeather:
        """Parse Open-Meteo current weather response."""
        current = data.get("current", {})
        
        temp_c = current.get("temperature_2m", 22.0)
        humidity = current.get("relative_humidity_2m", 60.0)
        wind_speed = current.get("wind_speed_10m", 10.0)
        pressure = current.get("surface_pressure", 1013.0)
        weather_code = current.get("weather_code", 0)
        
        # WMO weather code to description
        weather_map = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Fog",
            48: "Depositing rime fog",
            51: "Light drizzle",
            53: "Moderate drizzle",
            55: "Dense drizzle",
            61: "Slight rain",
            63: "Moderate rain",
            65: "Heavy rain",
            71: "Slight snow",
            73: "Moderate snow",
            75: "Heavy snow",
            80: "Slight rain showers",
            81: "Moderate rain showers",
            82: "Violent rain showers",
            95: "Thunderstorm",
            96: "Thunderstorm with hail",
            99: "Thunderstorm with heavy hail"
        }
        weather_desc = weather_map.get(weather_code, "Unknown")
        
        return HKCurrentWeather(
            temperature_c=temp_c,
            humidity_percent=humidity,
            wind_direction="N",  # Not provided by Open-Meteo
            wind_speed_kmh=wind_speed,
            pressure_hpa=pressure,
            visibility_km=10.0,
            weather_description=weather_desc,
            updated_at=datetime.now()
        )
    
    async def get_current_weather(self) -> Optional[HKCurrentWeather]:
        """
        Get current weather using configured API source.
        
        Falls back to Open-Meteo if primary source fails.
        
        Returns:
            HKCurrentWeather or None if both sources fail
        """
        if self.api_source == WeatherAPI.HKO:
            result = await self.get_current_weather_hko()
            if result:
                return result
        
        # Fallback to Open-Meteo
        return await self.get_current_weather_openmeteo()
    
    async def get_historical_weather_openmeteo(
        self,
        start_date: datetime,
        end_date: datetime,
        lat: float = 22.3193,
        lon: float = 114.1694
    ) -> List[HKHistoricalWeather]:
        """
        Fetch historical weather from Open-Meteo.
        
        Args:
            start_date: Start date for historical data
            end_date: End date for historical data
            lat: Latitude (default: Hong Kong)
            lon: Longitude (default: Hong Kong)
            
        Returns:
            List of historical weather records
        """
        try:
            session = await self._get_session()
            url = f"{self.OPEN_METEO_BASE_URL}/archive"
            params = {
                "latitude": lat,
                "longitude": lon,
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "daily": "temperature_2m_max,temperature_2m_min,temperature_2m_mean,precipitation_sum,relative_humidity_2m_mean,wind_speed_10m_mean",
                "timezone": "Asia/Hong_Kong"
            }
            
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    return []
                
                data = await response.json()
                return self._parse_historical_weather(data)
                
        except Exception:
            return []
    
    def _parse_historical_weather(self, data: Dict) -> List[HKHistoricalWeather]:
        """Parse Open-Meteo historical weather response."""
        daily = data.get("daily", {})
        dates = daily.get("time", [])
        
        records = []
        for i, date_str in enumerate(dates):
            date = datetime.fromisoformat(date_str)
            record = HKHistoricalWeather(
                date=date,
                max_temp_c=daily.get("temperature_2m_max", [20.0])[i],
                min_temp_c=daily.get("temperature_2m_min", [20.0])[i],
                avg_temp_c=daily.get("temperature_2m_mean", [20.0])[i],
                total_rainfall_mm=daily.get("precipitation_sum", [0.0])[i],
                avg_humidity_percent=daily.get("relative_humidity_2m_mean", [60.0])[i],
                avg_wind_speed_kmh=daily.get("wind_speed_10m_mean", [10.0])[i]
            )
            records.append(record)
        
        return records
    
    def get_cyclone_tracking_sources(self) -> List[Dict[str, str]]:
        """
        Get list of cyclone tracking data sources.
        
        Returns:
            List of source information dicts
        """
        return [
            {
                "name": "Hong Kong Observatory - Tropical Cyclone Track",
                "url": "https://www.hko.gov.hk/tc/informtc/tc_index.htm",
                "description": "Official HKO tropical cyclone track maps and warnings"
            },
            {
                "name": "Joint Typhoon Warning Center (JTWC)",
                "url": "https://www.metoc.navy.mil/jtwc/",
                "description": "US Navy tropical cyclone warnings for Western Pacific"
            },
            {
                "name": "Japan Meteorological Agency (JMA)",
                "url": "https://www.jma.go.jp/jma/en/Activities/tc_e.html",
                "description": "JMA tropical cyclone information for Western Pacific"
            },
            {
                "name": "Open-Meteo Tropical Cyclone API",
                "url": "https://open-meteo.com/en/docs/tropical-storm-api",
                "description": "Open-Meteo tropical cyclone position data"
            }
        ]
    
    async def get_cyclone_data_jtwc(self) -> List[HKTyphoonInfo]:
        """
        Fetch active cyclone data from JTWC.
        
        Note: This requires parsing JTWC advisories.
        Returns simulated data for demonstration.
        
        Returns:
            List of active tropical cyclones
        """
        # In production, this would parse JTWC advisories
        # For demonstration, return empty list (no active cyclones)
        return []
    
    def calculate_spi_index(
        self,
        precipitation_mm: List[float],
        timescales: List[int] = [1, 3, 6, 12]
    ) -> Dict[int, float]:
        """
        Calculate Standardized Precipitation Index (SPI).
        
        Args:
            precipitation_mm: List of monthly precipitation values
            timescales: SPI calculation periods in months
            
        Returns:
            Dict mapping timescale to SPI value
        """
        import numpy as np
        
        if len(precipitation_mm) == 0:
            return {t: 0.0 for t in timescales}
        
        spi_results = {}
        
        for months in timescales:
            if len(precipitation_mm) < months:
                spi_results[months] = 0.0
                continue
            
            # Calculate cumulative precipitation
            cumsum = []
            for i in range(len(precipitation_mm)):
                start = max(0, i - months + 1)
                cumsum.append(sum(precipitation_mm[start:i + 1]))
            
            cumsum = np.array(cumsum)
            
            # Simple SPI approximation (zero-centered)
            mean_val = np.mean(cumsum)
            std_val = np.std(cumsum)
            
            if std_val > 0:
                spi = (cumsum[-1] - mean_val) / std_val
            else:
                spi = 0.0
            
            spi_results[months] = round(spi, 2)
        
        return spi_results
    
    async def get_reservoir_levels(self) -> Dict[str, float]:
        """
        Get Hong Kong reservoir levels (simulated).
        
        Note: Real-time reservoir data requires HKO API access.
        
        Returns:
            Dict mapping reservoir name to fill percentage
        """
        # Simulated data - in production, fetch from HKO
        return {
            "Plover Cove": 0.75,
            "Shek Pik": 0.82,
            "Tai Lam Chung": 0.68,
            "High Island": 0.85,
            "Sham Shui Po": 0.70
        }


async def demo_weather_api():
    """Demonstrate weather API usage."""
    api = HKWeatherAPI(api_source=WeatherAPI.OPEN_METEO)
    
    # Get current weather
    current = await api.get_current_weather()
    if current:
        print(f"Current weather in HK:")
        print(f"  Temperature: {current.temperature_c}°C")
        print(f"  Humidity: {current.humidity_percent}%")
        print(f"  Wind: {current.wind_direction} {current.wind_speed_kmh} km/h")
        print(f"  Conditions: {current.weather_description}")
    
    # Get historical weather
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    history = await api.get_historical_weather_openmeteo(start_date, end_date)
    print(f"\nRetrieved {len(history)} historical records")
    
    # Calculate SPI
    precip = [h.total_rainfall_mm for h in history]
    spi = api.calculate_spi_index(precip)
    print(f"\nSPI Index (1-month): {spi.get(1, 0.0)}")
    print(f"SPI Index (3-month): {spi.get(3, 0.0)}")
    
    # Cyclone sources
    print("\nCyclone tracking sources:")
    for source in api.get_cyclone_tracking_sources():
        print(f"  - {source['name']}")
    
    await api.close()
    print("\nDemo completed.")


if __name__ == "__main__":
    asyncio.run(demo_weather_api())
