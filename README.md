# Climate Digital Twin

A digital twin framework for quantifying physical climate-related financial risks with Hong Kong focus.

## Overview

This project provides a framework for integrating climate risk assessments into financial modeling:

- **Physical Climate Risk Assessment**: Flood, typhoon, wildfire, drought hazards
- **Financial Impact Analysis**: Credit risk adjustment for real estate portfolios  
- **Scenario Analysis**: NGFS climate scenarios (Orderly, Disorderly, Hot House)
- **Monte Carlo Simulation**: Portfolio-level risk quantification
- **CLIMADA Integration**: Scientific impact functions (MDD/PAA/MDR pattern)

## Key Features

### 1. Hazard Assessment Module
- Multiple hazard types: flood, typhoon, wildfire, drought
- CLIMADA-compatible impact functions with HK calibrations
- Regional hazard data (12 HK districts)

### 2. Hong Kong Integration
- 12 HK districts: central, wan_chai, causeway_bay, tst, hung_hom, kwun_tong, sha_tin, tuen_mun, yuen_long, tin_shui_wai, lantau, cheung_chau
- District risk levels (flood, typhoon, wildfire, drought)
- Interactive Folium risk map

### 3. Financial Risk Module
- Extended Vasicek model for climate-adjusted PD/LGD
- Expected Loss (EL) and Unexpected Loss (UL)
- Capital adequacy impact

### 4. Scenario Framework
- NGFS scenarios: Orderly, Disorderly, Hot House
- Time-horizon based projections
- Multi-scenario comparison

### 5. Monte Carlo Simulation
- 10,000+ simulation paths
- VaR and Expected Shortfall metrics
- Portfolio risk distribution

## Installation

```bash
git clone https://github.com/Weeris/climate-digital-twin.git
cd climate-digital-twin
pip install -r requirements.txt
pip install pytest pytest-cov
```

## Testing

71 tests covering hazard, financial, and CLIMADA modules.

### Running Tests

```bash
# Run all tests
python3 -m pytest tests/ -v

# Run specific test file
python3 -m pytest tests/test_hazard.py -v
python3 -m pytest tests/test_financial.py -v
python3 -m pytest tests/test_hazard_climada.py -v

# Run with coverage
python3 -m pytest tests/ --cov=core --cov=utils
```

### Test Coverage

| Module | Tests | Description |
|--------|-------|-------------|
| core/hazard.py | 21 | Hazard damage curves, regional data |
| core/financial.py | 10 | ClimateVasicek, portfolio risk |
| core/hazard_climada.py | 40 | CLIMADA impact functions |

## Quick Start

### Streamlit Dashboard

```bash
streamlit run app.py
```

Pages: Home → Data Input → Hazard → Financial → Monte Carlo → Scenario → HK Risk Map → Reports

### Basic Hazard Assessment

```python
from core.hazard import HazardAssessment

hazard = HazardAssessment()
damage = hazard.assess_flood_risk(depth_m=1.5, asset_value=10000000)
print(f"Physical damage: ${damage['physical_damage']:,.0f}")
```

### CLIMADA Impact Functions

```python
from core.hazard_climada import create_flood_func, ImpactFuncSet

funcset = ImpactFuncSet()
flood_func = create_flood_func()
funcset.add_func(flood_func)

# Assess damage using CLIMADA pattern
result = flood_func.assess(intensity=0.8)  # intensity: 0-1 scale
print(f"Damage: {result['damage_ratio']:.2%}")
```

### HK Regional Data

```python
from core.hazard import RegionalHazardData

regional = RegionalHazardData()
params = regional.get_regional_hazard_params(
    region="central",
    hazard_type="flood",
    return_period=100
)
```

## Project Structure

```
climate-digital-twin/
├── LICENSE
├── README.md
├── requirements.txt
├── app.py                    # Streamlit dashboard (8 pages)
├── core/
│   ├── __init__.py
│   ├── hazard.py            # Hazard assessment + CLIMADA wrapper
│   ├── hazard_climada.py     # CLIMADA ImpactFunc implementation
│   ├── financial.py          # ClimateVasicek, portfolio risk
│   ├── simulation.py        # Monte Carlo engine
│   └── scenarios.py         # NGFS scenario framework
├── utils/
│   ├── __init__.py
│   ├── hk_map.py            # Interactive HK risk map (Folium)
│   └── data_processing.py   # Data utilities
├── data/
│   ├── hk_districts.json    # HK district risk data
│   ├── hk_financial_params.json
│   └── README.md
└── tests/
    ├── test_hazard.py       # 21 tests
    ├── test_financial.py    # 10 tests
    └── test_hazard_climada.py  # 40 tests
```

## HK District Risk Summary

| District | Flood | Typhoon | Wildfire | Drought |
|----------|-------|---------|----------|---------|
| Central | High | High | Low | Medium |
| Wan Chai | High | High | Low | Medium |
| Causeway Bay | High | High | Low | Medium |
| TST | High | High | Low | Medium |
| Kwun Tong | Medium | Medium | Low | Low |
| Sha Tin | Medium | Medium | Medium | Medium |
| Tuen Mun | Very High | High | Medium | High |
| Yuen Long | Very High | High | Medium | High |
| Tin Shui Wai | Very High | High | Low | High |

## Financial Parameters (HKD)

| Parameter | Value |
|-----------|-------|
| HKD per USD | 7.75 |
| Prime Rate | 5.875% |
| Max LTV (Residential) | 70% |
| Max LTV (Commercial) | 60% |

## Dependencies

```
numpy>=1.21.0
pandas>=1.3.0
scipy>=1.7.0
matplotlib>=3.4.0
streamlit>=1.20.0
folium==0.20.0
streamlit-folium==0.20.0
```

## License

MIT License - see LICENSE file.

## Disclaimer

Educational and research purposes only. Validate calculations before production use.
