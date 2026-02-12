# Climate Digital Twin

A digital twin framework for quantifying physical climate-related financial risks.

## Overview

This project provides a framework for integrating climate risk assessments into financial modeling, with a focus on:

- **Physical Climate Risk Assessment**: Flood, wildfire, cyclone, and drought hazards
- **Financial Impact Analysis**: Credit risk adjustment for real estate portfolios
- **Scenario Analysis**: Forward-looking risk projections
- **Monte Carlo Simulation**: Portfolio-level risk quantification

## Key Features

### 1. Hazard Assessment Module
- Multiple hazard types: flood, wildfire, cyclone, drought
- Damage functions based on hazard intensity
- Real estate-specific vulnerability curves

### 2. Hong Kong Climate Data Integration
- Specialized HK flood zones (Victoria Harbour, Kowloon, New Territories)
- Tropical cyclone tracking (Signal 3, 8, 9, 10)
- Wildfire risk for country parks
- Drought monitoring (reservoir levels, SPI index)

### 3. Financial Risk Module
- Extended Vasicek model for credit risk adjustment
- Expected Loss (EL) and Unexpected Loss (UL) calculations
- Capital adequacy impact assessment

### 4. Scenario Framework
- Forward-looking climate projections
- Multiple scenario support
- Time-horizon based analysis

### 5. Monte Carlo Simulation
- Portfolio-level risk distribution
- 10,000+ simulation paths
- VaR and Expected Shortfall metrics

## Installation

```bash
git clone https://github.com/Weeris/climate-digital-twin.git
cd climate-digital-twin
pip install -r requirements.txt
pip install pytest pytest-cov
```

## Testing

This project includes a comprehensive pytest test suite with 53 tests covering hazard assessment, financial modeling, and HK-specific modules.

### Running Tests

```bash
# Run all tests
python3 -m pytest tests/ -v

# Run specific test file
python3 -m pytest tests/test_hazard.py -v
python3 -m pytest tests/test_financial.py -v
python3 -m pytest tests/test_hk_modules.py -v

# Run with coverage
python3 -m pytest tests/ --cov=core --cov=utils
```

### Test Coverage

| Module | Tests | Coverage |
|--------|-------|----------|
| core/hazard.py | 21 | Hazard damage curves, regional data |
| core/financial.py | 10 | ClimateVasicek, portfolio risk |
| HK modules | 22 | Regional data, property values, damage functions, financial |

### Test Categories

- **Hazard Tests**: Flood, cyclone, wildfire, drought damage curves with various intensities and building types
- **Financial Tests**: PD/LGD adjustments, Monte Carlo simulations, capital calculations
- **HK Module Tests**: District data, property valuations, damage assessments, tax/mortgage calculations

## Quick Start

### Basic Hazard Assessment

```python
from core.hazard import HazardAssessment

# Assess flood risk
hazard = HazardAssessment()
damage = hazard.assess_flood_risk(depth_m=1.5, asset_value=10000000)
print(f"Physical damage: ${damage['physical_damage']:,.0f}")
print(f"Repair cost: ${damage['repair_cost_estimate']:,.0f}")
```

### Hong Kong Climate Integration

```python
from core.hk_regional_data import HKRegionalHazardData, get_hk_zone_for_location
from core.hazard import RegionalHazardData

# Get HK flood parameters
hk_data = HKRegionalHazardData()
flood_params = hk_data.get_flood_parameters("hk_central")
print(f"100-year flood depth: {flood_params.avg_depth_100yr_m}m")
print(f"Storm surge risk: {flood_params.storm_surge_risk}")

# Map location to HK zone
zone = get_hk_zone_for_location("Tsim Sha Tsui")
print(f"Zone: {zone}")

# Use RegionalHazardData with HK zones
regional = RegionalHazardData()
params = regional.get_regional_hazard_params(
    region="hk_kowloon",
    hazard_type="flood",
    return_period=100,
    include_storm_surge=True
)
print(f"Flood depth (with surge): {params['base_depth_m']}m")
```

### Weather Data Integration

```python
import asyncio
from utils.hk_weather_api import HKWeatherAPI, WeatherAPI

async def get_hk_weather():
    api = HKWeatherAPI(api_source=WeatherAPI.OPEN_METEO)
    current = await api.get_current_weather()
    if current:
        print(f"Temperature: {current.temperature_c}°C")
        print(f"Humidity: {current.humidity_percent}%")
        print(f"Conditions: {current.weather_description}")
    
    # Get historical data for SPI calculation
    from datetime import datetime, timedelta
    history = await api.get_historical_weather_openmeteo(
        start_date=datetime.now() - timedelta(days=90),
        end_date=datetime.now()
    )
    
    # Calculate drought index
    precip = [h.total_rainfall_mm for h in history]
    spi = api.calculate_spi_index(precip)
    print(f"SPI (3-month): {spi.get(3, 0.0)}")
    
    await api.close()

asyncio.run(get_hk_weather())
```

## Project Structure

```
climate-digital-twin/
├── LICENSE
├── README.md
├── requirements.txt
├── app.py                    # Streamlit dashboard
├── core/
│   ├── __init__.py
│   ├── hazard.py            # Hazard assessment module (+ HK methods)
│   ├── hk_damage_functions.py # HK-specific building damage functions
│   ├── hk_property_values.py  # HK property value baselines
│   ├── hk_regional_data.py   # HK-specific hazard parameters
│   ├── financial.py         # Credit risk calculations
│   ├── simulation.py        # Monte Carlo engine
│   └── scenarios.py         # Scenario framework
├── utils/
│   ├── __init__.py
│   ├── hk_weather_api.py   # HK weather data ingestion
│   └── data_processing.py   # Data utilities
└── data/
    ├── hk_sample_portfolio.csv # Sample HK property portfolio
    └── README.md            # Data documentation
```

## HK Building Damage Functions (`core/hk_damage_functions.py`)

HK-specific damage functions for physical climate risk assessment:

### Supported Building Types
- `residential_high_rise` - High-rise apartments (10-70+ floors)
- `residential_walkup` - Older low-rise buildings
- `commercial_office` - Office towers
- `commercial_mall` - Shopping centers
- `commercial_hotel` - Hotels
- `industrial_factory` - Manufacturing facilities
- `industrial_warehouse` - Storage facilities
- `infrastructure_mtr` - MTR stations
- `infrastructure_tunnel` - Road/rail tunnels
- `infrastructure_bridge` - Bridges

### Flood Damage Assessment
```python
from core.hk_damage_functions import HKBuildingDamageFunctions, HKBuildingType

damage_fn = HKBuildingDamageFunctions()
result = damage_fn.assess_flood_damage(
    building_type=HKBuildingType.RESIDENTIAL_HIGH_RISE,
    flood_depth_m=1.5,
    building_value_hkd=50000000,
    num_floors=40,
    has_basement=True
)
print(f"Damage ratio: {result.damage_ratio}")
print(f"Physical damage: HKD {result.physical_damage_hkd:,.0f}")
print(f"Downtime: {result.downtime_days} days")
```

### Typhoon Damage Assessment
```python
result = damage_fn.assess_typhoon_damage(
    building_type=HKBuildingType.COMMERCIAL_OFFICE,
    wind_speed_kmh=150,
    building_value_hkd=200000000,
    construction_type=HKConstructionType.GLASS_CURTAIN_WALL,
    facade_area_sqm=3000,
    num_windows=200
)
print(f"Window damage: {result['window_damage_ratio']}")
print(f"Facade damage: {result['facade_damage_ratio']}")
```

### Downtime Estimates
High-rise buildings have extended recovery times due to:
- Complex building systems
- Multiple affected floors
- Relocation requirements
- Supply chain constraints

## HK Property Values (`core/hk_property_values.py`)

District-level property value baselines in HKD per sqft:

### Hong Kong Island
| District | Residential | Commercial Office | Commercial Retail |
|----------|-------------|-------------------|-------------------|
| Central | $22,000-$35,000 | $30,000-$50,000 | $35,000-$60,000 |
| Admiralty | $20,000-$32,000 | $28,000-$48,000 | - |
| Wan Chai | $18,000-$30,000 | $25,000-$45,000 | - |
| Causeway Bay | $19,000-$31,000 | - | $30,000-$55,000 |

### Kowloon
| District | Residential | Commercial | Industrial |
|----------|-------------|-----------|------------|
| TST | $16,000-$28,000 | $22,000-$40,000 | - |
| Hung Hom | $14,000-$23,000 | $20,000-$32,000 | - |
| Kwun Tong | $12,000-$20,000 | - | $7,000-$13,000 |

### New Territories
| District | Residential | Industrial |
|----------|-------------|------------|
| Sha Tin | $13,000-$22,000 | - |
| Tuen Mun | $11,000-$18,000 | $6,500-$12,000 |
| Yuen Long | $10,000-$17,000 | $5,500-$10,000 |
| Tin Shui Wai | $9,000-$16,000 | - |

### Islands
| District | Residential | Commercial |
|----------|-------------|-----------|
| Lantau | $11,000-$20,000 | - |
| Cheung Chau | $9,000-$16,000 | - |

### Adjustment Factors
- **Floor premium**: +1.5% per floor above 10
- **Sea view premium**: +20%
- **Mountain view premium**: +10%
- **City view premium**: +5%
- **Park view premium**: +8%
- **Age depreciation**: -0.2% per year (max 30%)

### Property Value Calculation
```python
from core.hk_property_values import HKPropertyValues

pv = HKPropertyValues()
result = pv.calculate_property_value(
    district="central",
    building_type="residential_apartment",
    area_sqft=1000,
    floor=25,
    view="sea",
    building_age_years=10
)
print(f"Property value: HKD {result['total_value_hkd']:,.0f}")
print(f"Price per sqft: HKD {result['final_price_sqft_hkd']:,.0f}")
```

## HK Hazard Assessment Methods (`core/hazard.py`)

HK-specific hazard assessment methods:

### Flood Risk Assessment
```python
from core.hazard import HKHazardAssessment

hk_hazard = HKHazardAssessment()
result = hk_hazard.assess_hk_flood_risk(
    district="central",
    building_type="residential_high_rise",
    flood_depth_m=1.0,
    building_value_hkd=50000000,
    num_floors=50,
    has_basement=True
)
print(f"Damage: HKD {result['physical_damage_hkd']:,.0f}")
print(f"Downtime: {result['downtime_days']} days")
```

### Typhoon Risk Assessment
```python
result = hk_hazard.assess_hk_typhoon_risk(
    building_type="commercial_office",
    wind_speed_kmh=120,
    building_value_hkd=100000000,
    has_glass_curtain=True,
    facade_area_sqm=2000
)
print(f"Signal equivalent: {result['signal_equivalent']}")
print(f"Total damage: HKD {result['total_damage_hkd']:,.0f}")
```

## Sample Portfolio (`data/hk_sample_portfolio.csv`)

Sample HK property portfolio with 20 properties across districts:

| Property Type | Districts Covered |
|---------------|-------------------|
| Commercial | Central, Admiralty, Wan Chai, TST, Causeway Bay |
| Residential | Central, Causeway Bay, Hung Hom, Sha Tin, Tuen Mun, Yuen Long, Tin Shui Wai, Lantau, Cheung Chau |
| Industrial | Kwun Tong, Tuen Mun, Yuen Long, Sha Tin |
| Infrastructure | MTR Station, Cross Harbour Tunnel, Island Bridge |
| Hotel | Causeway Bay |

Each record includes:
- Property ID and name
- District and building type
- Area (sqft), floor, view, building age
- Property value (HKD)
- 100-year flood depth exposure
- Typhoon exposure level
- Storm surge risk indicator

## Hong Kong Hazard Zones

| Zone | Risk Level | 100yr Flood Depth | Storm Surge |
|------|-----------|-------------------|-------------|
| hk_central | High | 1.5m | +0.8m |
| hk_kowloon | High | 1.4m | +0.7m |
| hk_new_territories_west | Very High | 1.8m | +1.0m |
| hk_new_territories_east | Medium | 0.8m | No |
| hk_islands | Medium | 1.0m | +0.9m |

## Typhoon Signals (Hong Kong)

| Signal | Wind Speed | Meaning | Avg Frequency/Year |
|--------|------------|---------|-------------------|
| Signal 3 | 41-62 km/h | Gale | 4.5 |
| Signal 8 | 63-117 km/h | Storm | 1.8 |
| Signal 9 | Increasing | Hurricane force | - |
| Signal 10 | ≥118 km/h | Hurricane | 0.3 |

Peak season: July - September
Average annual typhoon days: ~6

## Data Sources

### Hong Kong Data
- **Hong Kong Observatory (HKO)**: https://www.hko.gov.hk/
  - Weather observations, tropical cyclone warnings
  - Historical climate data
  
- **Open-Meteo**: https://open-meteo.com/
  - Free weather API (backup source)
  - Historical weather archives

### Cyclone Tracking
- **Joint Typhoon Warning Center (JTWC)**: https://www.metoc.navy.mil/jtwc/
- **Japan Meteorological Agency (JMA)**: https://www.jma.go.jp/jma/en/Activities/tc_e.html

## Hazard Types

| Hazard | Primary Metric | Damage Function |
|--------|---------------|-----------------|
| Flood | Water depth (m) | Depth-damage curve |
| Wildfire | Burn area (%) | Area-damage curve |
| Cyclone | Wind speed (km/h) | Wind-damage curve |
| Drought | SPI index | Severity-damage curve |

## Risk Outputs

- **Physical Damage**: Direct asset loss from climate events
- **Credit Risk Impact**: PD/LGD adjustments under stress
- **Capital Impact**: Additional capital requirements
- **Portfolio Metrics**: VaR, Expected Shortfall, Loss Distribution

## HK UI & Integration (Phase 4)

HK-specific user interface with interactive maps and Streamlit dashboard pages.

### Interactive Risk Map (`utils/hk_map.py`)

Folium-based interactive map visualization for Hong Kong climate risks:

```python
from utils.hk_map import create_hk_map, list_districts, get_district

# Create interactive map
m = create_hk_map()

# List all districts
districts = list_districts()  # ['central', 'wan_chai', ...]

# Get district details
district = get_district("central")
print(f"Risk: {district.risk_levels}")
```

**Map Features:**
- District markers color-coded by overall risk level
- Layer toggles for flood zones, typhoon paths, wildfire areas
- Popup information with risk details
- Legend with color coding

**Risk Level Colors:**
- Very High: Red (#FF0000)
- High: Orange (#FF6600)
- Medium: Yellow (#FFCC00)
- Low: Green (#00CC00)

### HK Dashboard Pages (Phase 4)

Four new HK-specific pages added to the Streamlit dashboard:

#### 1. HK Dashboard (`hk_home`)
- Portfolio exposure summary (HKD millions)
- District risk overview
- Current weather conditions
- Active warnings

#### 2. HK Risk Map (`hk_map`)
- Interactive Folium map
- District selector
- Layer controls
- Export map as HTML

#### 3. HK Property Analysis (`hk_property`)
- Property value calculator by district
- Floor/view/age adjustments
- Damage assessment tool

#### 4. HK Financial Analysis (`hk_financial`)
- Acquisition cost calculator (stamp duty, legal fees)
- Insurance premium calculator
- Mortgage affordability checker

### Demo Script (`demo_hk.py`)

Run the HK dashboard demo:

```bash
streamlit run demo_hk.py
```

Features demonstrated:
- District risk overview table
- Property value calculator
- Damage assessment tool
- Interactive map

### HK District Data (`data/hk_districts.json`)

JSON file containing district information:

```json
{
  "districts": {
    "central": {
      "name": "central",
      "display_name": "Central",
      "coordinates": [22.2823, 114.1589],
      "risk_levels": {
        "flood": "high",
        "typhoon": "high"
      },
      "avg_property_value_hkd": 28000000,
      "population": 132000
    }
  }
}
```

### Installation

Add these dependencies for HK visualization:

```bash
pip install folium>=2.0.0
pip install branca>=0.7.0
pip install streamlit-folium>=0.15.0
```

Or use requirements.txt:
```bash
pip install -r requirements.txt
```

### Usage

1. Run main dashboard:
```bash
streamlit run app.py
```

2. Navigate to HK-specific pages via sidebar

3. Run HK demo:
```bash
streamlit run demo_hk.py
```

### HK District Coordinates

| District | Latitude | Longitude |
|----------|----------|-----------|
| Central | 22.2823 | 114.1589 |
| Wan Chai | 22.2816 | 114.1725 |
| Causeway Bay | 22.2793 | 114.1821 |
| Kowloon TST | 22.3039 | 114.1704 |
| Hung Hom | 22.3033 | 114.1817 |
| Kwun Tong | 22.3124 | 114.2248 |
| Sha Tin | 22.3894 | 114.2034 |
| Tuen Mun | 22.3909 | 113.9728 |
| Yuen Long | 22.4445 | 114.0221 |
| Tin Shui Wai | 22.4623 | 113.9968 |
| Lantau (Tung Chung) | 22.2886 | 113.9356 |
| Cheung Chau | 22.2256 | 114.0275 |

---

## HK Financial Model (Phase 3)

HK-specific financial modeling with HKD currency and insurance integration.

### HK Financial Parameters (`data/hk_financial_params.json`)

```json
{
  "currency": {
    "code": "HKD",
    "symbol": "$",
    "exchange_rate_usd": 7.75
  },
  "mortgage_parameters": {
    "prime_rate": 0.05875,
    "ltv_max_residential": 0.70
  },
  "district_insurance_rates": {
    "central": {"base_premium_rate": 0.0015},
    "tst": {"base_premium_rate": 0.0018}
  }
}
```

### HK Financial Risk Module (`core/hk_financial.py`)

```python
from core.hk_financial import HKFinancialModel

model = HKFinancialModel()

# Calculate acquisition costs
cost = model.calculate_total_acquisition_cost(
    price=10000000,  # HKD
    is_resident=True
)
print(f"Total cost: {cost['total_acquisition_cost']:,.0f} HKD")

# Calculate mortgage impact
mortgage = model.calculate_mortgage_impact(
    property_value=12000000,
    damage_ratio=0.15,
    property_type="residential"
)
```

### HK Insurance Loss Module (`core/hk_insurance.py`)

```python
from core.hk_insurance import HKInsuranceCalculator

calc = HKInsuranceCalculator()

# Calculate premium
premium = calc.calculate_premium(
    sum_insured=10000000,
    district="central",
    hazards=["typhoon", "flood"]
)
print(f"Annual premium: {premium['total_premium']:,.0f} HKD")

# Calculate claim
claim = calc.calculate_claim(
    damage_amount=3000000,
    sum_insured=10000000,
    hazard_type="flood"
)
print(f"Claim amount: {claim['actual_claim']:,.0f} HKD")
```

### HK Insurance Loss Ratios

| Hazard Type | Min Loss Ratio | Max Loss Ratio | Typical |
|-------------|----------------|----------------|---------|
| Flood | 45% | 65% | 55% |
| Typhoon | 35% | 55% | 45% |
| Fire | 25% | 45% | 35% |
| Combined | 40% | 60% | 50% |

### HK Report Generator (`core/hk_reports.py`)

```python
from core.hk_reports import HKReportGenerator

report = HKReportGenerator()

# Analyze portfolio
analysis = report.analyze_portfolio(portfolio)

# Export to CSV
report.generate_csv_report(portfolio, "hk_risk_report.csv")

# Export to HTML
report.generate_html_report(portfolio, "hk_risk_report.html")
```

### HK-Specific Financial Model (`core/financial.py`)

```python
from core.financial import ClimateVasicekHK, HKD

# Initialize HK model
hk_model = ClimateVasicekHK(
    base_pd=0.015,  # Lower HK mortgage PD
    base_lgd=0.35,   # Typical HK LGD
    climate_beta=0.6  # Higher sensitivity for HK
)

# Calculate HK capital requirement
capital = hk_model.calculate_hk_capital_requirement(
    exposure_hkd=10000000,
    physical_damage_ratio=0.15,
    hazard_type="typhoon"
)
print(f"Total capital: {capital['total_capital_hkd']:,.0f} HKD")
```

### Currency Support

```python
from core.financial import HKD, USD, CNY

# Convert currencies
hkd_amount = 10000000
usd_amount = HKD.to_usd(hkd_amount)
cny_amount = HKD.to_cny(hkd_amount)

# Format with symbol
print(HKD.format(hkd_amount))  # $10,000,000.00
```

### Major HK Insurers

- AXA, AIA, Zurich, Prudential, MSIG, China Pacific, FWD, Bank of China Insurance

## Use Cases

### Real Estate Portfolio Risk (Hong Kong)
Analyzes flood and climate risks for property portfolios, providing:
- Location-specific risk scores (Central, Kowloon, NT)
- Expected damage estimates for 10yr/50yr/100yr/500yr events
- Storm surge impact assessment
- Credit risk adjustments
- Capital provisioning recommendations

### Scenario Analysis
Tests portfolio resilience under various climate scenarios:
- Near-term projections (2025-2035)
- Medium-term scenarios (2035-2050)
- Long-term projections (2050-2100)

## Dependencies

- Python 3.9+
- numpy
- pandas
- scipy
- matplotlib
- streamlit
- aiohttp (for weather API)

## License

MIT License - see LICENSE file for details.

## Disclaimer

This software is provided for educational and research purposes only. 
Financial risk calculations should be validated against regulatory requirements 
and professional standards before use in production environments.
