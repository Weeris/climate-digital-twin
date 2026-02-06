# Data Directory

This directory contains sample data and data documentation for the Climate Digital Twin project.

## Sample Data Files

### Portfolio Data
Format for portfolio CSV files:
```
asset_id,value,asset_type,region,base_pd,base_lgd,damage_ratio
A001,50000000,residential,Bangkok,0.02,0.4,0.15
A002,30000000,residential,Bangkok,0.015,0.4,0.10
...
```

### Regional Hazard Data
Regional flood parameters (flood depth in meters by return period):
```
region,risk_level,10yr_depth,100yr_depth,500yr_depth
bangkok_central,high,0.3,1.2,2.0
bangkok_peripheral,medium,0.2,0.8,1.5
ayutthaya_industrial,very_high,0.8,2.5,3.5
```

## External Data Sources

Climate and hazard data should be sourced from:
- **NASA Earth Data**: Satellite imagery and climate observations
- **Copernicus EMS**: European Emergency Management Service
- **World Bank Climate Data**: Open climate datasets
- **Local meteorological agencies**: Country-specific hazard data

## Data Processing

Data processing pipelines are defined in `utils/data_processing.py`.
