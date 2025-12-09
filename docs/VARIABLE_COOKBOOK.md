# Variable Cookbook

## Dataset Overview
This dataset contains time-series data from the US Bureau of Labor Statistics (BLS) focusing on employment, job openings, and labor turnover across various industries. The data is intended to support research into the causal effects of Generative AI availability on employment.

**File:** `data/bls_employment_data.csv`
**Time Range:** 2015 - 2025 (Monthly)

## Column Descriptions

| Variable Name | Description | Data Type | Example |
| :--- | :--- | :--- | :--- |
| `SeriesID` | Unique identifier for the BLS time series. | String | `CES5100000001` |
| `Industry` | The industry sector associated with the data. | String | `Information` |
| `Metric` | The specific labor market measure. | String | `All Employees` |
| `Source` | The BLS survey source (CES or JOLTS). | String | `CES` |
| `Unit` | The unit of measurement. | String | `Thousands`, `Level` |
| `Year` | The year of the observation. | Integer | `2023` |
| `Period` | The month code. | String | `M01` |
| `PeriodName` | The full name of the month. | String | `January` |
| `Value` | The recorded value for the metric. | Float | `3050.5` |
| `Footnotes` | Any notes provided by BLS for that specific data point. | String | `Preliminary` |

## Series Definitions

The dataset includes the following series, selected to represent industries with varying degrees of exposure to Generative AI.

### High AI Exposure Industries

**1. Information (NAICS 51)**
*   **Employment:** `CES5100000001` - All Employees, Thousands (Seasonally Adjusted)
*   **Earnings:** `CES5100000003` - Average Hourly Earnings of All Employees (Seasonally Adjusted)
*   **Job Openings:** `JTS510000000000000JOL` - Job Openings Level (Seasonally Adjusted)
*   **Hires:** `JTS510000000000000HIL` - Hires Level (Seasonally Adjusted)

**2. Professional, Scientific, and Technical Services (NAICS 54)**
*   **Employment:** `CES6054000001` - All Employees, Thousands (Seasonally Adjusted)
*   **Earnings:** `CES6054000003` - Average Hourly Earnings of All Employees (Seasonally Adjusted)
*   **Job Openings:** `JTS540000000000000JOL` - Job Openings Level (Seasonally Adjusted) *(Note: JOLTS data is for Professional and Business Services)*
*   **Hires:** `JTS540000000000000HIL` - Hires Level (Seasonally Adjusted) *(Note: JOLTS data is for Professional and Business Services)*

**3. Finance and Insurance (NAICS 52)**
*   **Employment:** `CES5552000001` - All Employees, Thousands (Seasonally Adjusted)
*   **Earnings:** `CES5552000003` - Average Hourly Earnings of All Employees (Seasonally Adjusted)
*   **Job Openings:** `JTS520000000000000JOL` - Job Openings Level (Seasonally Adjusted)
*   **Hires:** `JTS520000000000000HIL` - Hires Level (Seasonally Adjusted)

### Control / Low AI Exposure Industries

**4. Leisure and Hospitality (NAICS 70)**
*   **Employment:** `CES7000000001` - All Employees, Thousands (Seasonally Adjusted)
*   **Earnings:** `CES7000000003` - Average Hourly Earnings of All Employees (Seasonally Adjusted)
*   **Job Openings:** `JTS700000000000000JOL` - Job Openings Level (Seasonally Adjusted)
*   **Hires:** `JTS700000000000000HIL` - Hires Level (Seasonally Adjusted)

### Benchmark

**5. Total Nonfarm**
*   **Employment:** `CES0000000001`
*   **Earnings:** `CES0000000003`
*   **Job Openings:** `JTS000000000000000JOL`
*   **Hires:** `JTS000000000000000HIL`

## Data Sources
*   **CES (Current Employment Statistics):** Provides data on employment, hours, and earnings.
*   **JOLTS (Job Openings and Labor Turnover Survey):** Provides data on job openings, hires, and separations.
