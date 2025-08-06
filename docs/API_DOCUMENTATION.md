# Climate Analysis System API Documentation

## Base URL
```
http://localhost:8000
```

## Endpoints

### CO2 Data

#### Get Monthly CO2 Data
```
GET /api/co2/monthly
```
Query Parameters:
- `start_date` (optional): ISO datetime string
- `end_date` (optional): ISO datetime string

Response: Array of CO2Data objects

#### Get CO2 Summary
```
GET /api/co2/summary
```
Returns statistical summary of CO2 data including trends.

### Temperature Data

#### Get Global Temperature Data
```
GET /api/temperature/global
```
Query Parameters:
- `start_date` (optional): ISO datetime string
- `end_date` (optional): ISO datetime string

#### Get Regional Temperature Data
```
GET /api/temperature/regional/{region}
```
Available regions: Arctic, Europe, North America, Asia, Africa, South America, Australia, Antarctica

### Analysis

#### CO2 Gap Analysis
```
GET /api/analysis/co2-gap
```
Analyzes the gap between theoretical CO2-based temperature and actual temperature.

Query Parameters:
- `start_date` (optional)
- `end_date` (optional)
- `region` (optional, default: "Global")

#### Calculate Single CO2 Gap
```
POST /api/analysis/co2-gap/calculate
```
Query Parameters:
- `co2_ppm` (required): CO2 concentration in ppm
- `actual_temp` (required): Actual temperature in Celsius
- `baseline_temp` (optional, default: 14.0)

#### Time-Lag Correlation Analysis
```
POST /api/analysis/time-lag/correlation
```
Analyzes correlation between groundwater and temperature with time delays.

Body Parameters:
- `groundwater_data`: Array of groundwater levels
- `temperature_data`: Array of temperature values
- `max_lag_months`: Maximum lag to test (1-60)

#### Comprehensive Analysis
```
GET /api/analysis/trends/comprehensive
```
Performs complete climate analysis including all factors.

## Response Formats

### CO2Data
```json
{
  "date": "2024-01-01T00:00:00",
  "ppm": 421.78,
  "location": "Mauna Loa",
  "source": "NOAA"
}
```

### TemperatureData
```json
{
  "date": "2024-01-01T00:00:00",
  "temperature_celsius": 15.5,
  "temperature_anomaly": 1.2,
  "region": "Global",
  "source": "NASA GISS"
}
```

### CO2GapAnalysis
```json
{
  "date": "2024-01-01T00:00:00",
  "co2_ppm": 421.78,
  "theoretical_temp": 15.0,
  "actual_temp": 15.6,
  "unexplained_gap": 0.6,
  "gap_percentage": 40.0,
  "p_value": 0.001,
  "confidence_interval": [0.4, 0.8]
}
```