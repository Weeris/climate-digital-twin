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

### 2. Financial Risk Module
- Extended Vasicek model for credit risk adjustment
- Expected Loss (EL) and Unexpected Loss (UL) calculations
- Capital adequacy impact assessment

### 3. Scenario Framework
- Forward-looking climate projections
- Multiple scenario support
- Time-horizon based analysis

### 4. Monte Carlo Simulation
- Portfolio-level risk distribution
- 10,000+ simulation paths
- VaR and Expected Shortfall metrics

## Installation

```bash
git clone https://github.com/Weeris/climate-digital-twin.git
cd climate-digital-twin
pip install -r requirements.txt
```

## Quick Start

```python
from core.hazard import HazardAssessment
from core.financial import ClimateVasicek
from core.simulation import MonteCarloEngine

# Assess hazard impact
hazard = HazardAssessment()
damage = hazard.assess_flood_risk(depth_m=1.5, asset_value=10000000)

# Calculate credit risk adjustment
vasicek = ClimateVasicek(base_pd=0.02, base_lgd=0.4)
pd_result = vasicek.calculate_adjusted_pd(time_horizon=10)

# Run Monte Carlo simulation
engine = MonteCarloEngine(portfolio_data)
results = engine.run_simulation(n_scenarios=10000)
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
│   ├── hazard.py            # Hazard assessment module
│   ├── financial.py         # Credit risk calculations
│   ├── simulation.py        # Monte Carlo engine
│   └── scenarios.py         # Scenario framework
├── utils/
│   ├── __init__.py
│   └── data_processing.py   # Data utilities
└── data/
    └── README.md            # Data documentation
```

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

## Use Cases

### Real Estate Portfolio Risk
Analyzes flood and climate risks for property portfolios, providing:
- Location-specific risk scores
- Expected damage estimates
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

## License

MIT License - see LICENSE file for details.

## Disclaimer

This software is provided for educational and research purposes only. 
Financial risk calculations should be validated against regulatory requirements 
and professional standards before use in production environments.
