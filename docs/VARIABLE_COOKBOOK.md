# Variable Cookbook

## Dataset Overview
This dataset contains time-series data from the US Bureau of Labor Statistics (BLS) focusing on employment, job openings, and labor turnover across various industries. The data is intended to support research into the causal effects of Generative AI availability on employment.

**File:** `data/bls_employment_data.csv`
**Time Range:** 2015 - 2025 (Monthly)

## Column Descriptions

| Variable Name | Description | Data Type | Example | Source |
| :--- | :--- | :--- | :--- | :--- |
| `SeriesID` | Unique identifier for the BLS time series. | String | `CES5100000001` | [BLS Series ID Formats](https://www.bls.gov/help/hlpforma.htm) |
| `State` | The state associated with the data (or 'Total' for national). | String | `California` | [FIPS Codes](https://www.bls.gov/respondents/mwr/electronic-data-interchange/appendix-d-usps-state-abbreviations-and-fips-codes.htm) |
| `Industry` | The industry sector associated with the data. | String | `Information` | [NAICS Codes](https://www.census.gov/naics/) |
| `Metric` | The specific labor market measure. | String | `All Employees` | [BLS CES](https://www.bls.gov/ces/) / [JOLTS](https://www.bls.gov/jlt/) |
| `Source` | The BLS survey source (CES or JOLTS). | String | `CES` | - |
| `Unit` | The unit of measurement. | String | `Thousands`, `Level` | - |
| `Year` | The year of the observation. | Integer | `2023` | - |
| `Period` | The month code. | String | `M01` | - |
| `PeriodName` | The full name of the month. | String | `January` | - |
| `Value` | The recorded value for the metric. | Float | `3050.5` | - |
| `Footnotes` | Any notes provided by BLS for that specific data point. | String | `Preliminary` | - |

## Series Definitions

The dataset includes the following series, selected to represent industries with varying degrees of exposure to Generative AI.

### High AI Exposure Industries

**1. Information (NAICS 51)**
*   **Employment:** `CES5100000001` - All Employees, Thousands (Seasonally Adjusted). [Source](https://data.bls.gov/timeseries/CES5100000001)
*   **Earnings:** `CES5100000003` - Average Hourly Earnings of All Employees (Seasonally Adjusted). [Source](https://data.bls.gov/timeseries/CES5100000003)
*   **Hours:** `CES5100000002` - Average Weekly Hours of All Employees (Seasonally Adjusted). [Source](https://data.bls.gov/timeseries/CES5100000002)
*   **Job Openings:** `JTS510000000000000JOL` - Job Openings Level (Seasonally Adjusted). [Source](https://data.bls.gov/timeseries/JTS510000000000000JOL)
*   **Hires:** `JTS510000000000000HIL` - Hires Level (Seasonally Adjusted). [Source](https://data.bls.gov/timeseries/JTS510000000000000HIL)

**2. Professional, Scientific, and Technical Services (NAICS 54)**
*   **Employment:** `CES6054000001` - All Employees, Thousands (Seasonally Adjusted). [Source](https://data.bls.gov/timeseries/CES6054000001)
*   **Earnings:** `CES6054000003` - Average Hourly Earnings of All Employees (Seasonally Adjusted). [Source](https://data.bls.gov/timeseries/CES6054000003)
*   **Hours:** `CES6054000002` - Average Weekly Hours of All Employees (Seasonally Adjusted). [Source](https://data.bls.gov/timeseries/CES6054000002)
*   **Job Openings:** `JTS540000000000000JOL` - Job Openings Level (Seasonally Adjusted). *(Note: JOLTS data is for Professional and Business Services)*. [Source](https://data.bls.gov/timeseries/JTS540000000000000JOL)
*   **Hires:** `JTS540000000000000HIL` - Hires Level (Seasonally Adjusted). *(Note: JOLTS data is for Professional and Business Services)*. [Source](https://data.bls.gov/timeseries/JTS540000000000000HIL)

**3. Finance and Insurance (NAICS 52)**
*   **Employment:** `CES5552000001` - All Employees, Thousands (Seasonally Adjusted). [Source](https://data.bls.gov/timeseries/CES5552000001)
*   **Earnings:** `CES5552000003` - Average Hourly Earnings of All Employees (Seasonally Adjusted). [Source](https://data.bls.gov/timeseries/CES5552000003)
*   **Hours:** `CES5552000002` - Average Weekly Hours of All Employees (Seasonally Adjusted). [Source](https://data.bls.gov/timeseries/CES5552000002)
*   **Job Openings:** `JTS520000000000000JOL` - Job Openings Level (Seasonally Adjusted). [Source](https://data.bls.gov/timeseries/JTS520000000000000JOL)
*   **Hires:** `JTS520000000000000HIL` - Hires Level (Seasonally Adjusted). [Source](https://data.bls.gov/timeseries/JTS520000000000000HIL)

### Control / Low AI Exposure Industries

**4. Leisure and Hospitality (NAICS 70)**
*   **Employment:** `CES7000000001` - All Employees, Thousands (Seasonally Adjusted). [Source](https://data.bls.gov/timeseries/CES7000000001)
*   **Earnings:** `CES7000000003` - Average Hourly Earnings of All Employees (Seasonally Adjusted). [Source](https://data.bls.gov/timeseries/CES7000000003)
*   **Hours:** `CES7000000002` - Average Weekly Hours of All Employees (Seasonally Adjusted). [Source](https://data.bls.gov/timeseries/CES7000000002)
*   **Job Openings:** `JTS700000000000000JOL` - Job Openings Level (Seasonally Adjusted). [Source](https://data.bls.gov/timeseries/JTS700000000000000JOL)
*   **Hires:** `JTS700000000000000HIL` - Hires Level (Seasonally Adjusted). [Source](https://data.bls.gov/timeseries/JTS700000000000000HIL)

### Benchmark

**5. Total Nonfarm**
*   **Employment:** `CES0000000001`. [Source](https://data.bls.gov/timeseries/CES0000000001)
*   **Earnings:** `CES0000000003`. [Source](https://data.bls.gov/timeseries/CES0000000003)
*   **Hours:** `CES0000000002`. [Source](https://data.bls.gov/timeseries/CES0000000002)
*   **Job Openings:** `JTS000000000000000JOL`. [Source](https://data.bls.gov/timeseries/JTS000000000000000JOL)
*   **Hires:** `JTS000000000000000HIL`. [Source](https://data.bls.gov/timeseries/JTS000000000000000HIL)

## Static Industry Controls (New)

A separate file `data/industry_static_controls.csv` has been created to include time-invariant characteristics suggested by the DAG. These are representative values derived from academic literature.

| Variable Name | Description | Source / Proxy |
| :--- | :--- | :--- |
| `AI_Exposure_Score` | Measure of occupational exposure to Generative AI. | [Felten et al. (2021)](https://arxiv.org/abs/2103.12648) / [Eloundou et al. (2023)](https://arxiv.org/abs/2303.10130) |
| `Teleworkability_Score` | Share of jobs that can be performed remotely. | [Dingel & Neiman (2020)](https://www.nber.org/papers/w26948) |
| `Routine_Task_Index` | Measure of how routine/codifiable tasks are. | [Autor & Dorn (2013)](https://www.aeaweb.org/articles?id=10.1257/aer.103.5.1553) (based on O*NET) |
| `Skill_Intensity_Index` | Proxy for skill level (e.g., education requirements). | [O*NET Education Requirements](https://www.onetonline.org/) |
| `Automation_Risk_Score` | Risk of automation by previous generations of technology (Robotics/Software). | [Frey & Osborne (2017)](https://www.oxfordmartin.ox.ac.uk/downloads/academic/The_Future_of_Employment.pdf) |

## Data Sources
*   **CES (Current Employment Statistics):** Provides data on employment, hours, and earnings.
*   **JOLTS (Job Openings and Labor Turnover Survey):** Provides data on job openings, hires, and separations.
