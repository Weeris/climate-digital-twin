# Data Directory

This directory contains Hong Kong climate and financial data for the Climate Digital Twin project.

## Data Files

### hk_districts.json
HK district risk data for the interactive map:
- 12 districts: central, wan_chai, causeway_bay, tst, hung_hom, kwun_tong, sha_tin, tuen_mun, yuen_long, tin_shui_wai, lantau, cheung_chau
- Risk levels: flood, typhoon, wildfire, drought
- Coordinates, population, property values

### hk_financial_params.json
HK-specific financial parameters:
- Currency: HKD (7.75 per USD)
- Property taxes: BSD, AVD, stamp duty
- Mortgage parameters: prime rate 5.875%
- Insurance rates by district

## Sample Portfolio Format

HK sample portfolio (in app.py):
```
asset_id,asset_type,district,value,base_pd,base_lgd,damage_ratio,floor,building_age
HK001,residential_high_rise,central,50000000,0.015,0.35,0.12,35,8
HK002,residential_high_rise,wan_chai,30000000,0.018,0.38,0.15,22,15
...
```

## External Data Sources

Climate and hazard data sourced from:
- **Hong Kong Observatory**: Local weather and typhoon data
- **NASA Earth Data**: Satellite imagery and climate observations
- **Copernicus EMS**: European Emergency Management Service
- **World Bank Climate Data**: Open climate datasets

## Data Processing

Data processing pipelines are defined in `utils/data_processing.py`.
