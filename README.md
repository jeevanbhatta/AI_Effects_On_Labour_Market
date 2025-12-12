# AI Effects on Labor Market Data Repository

This repository contains data and scripts to support the research paper: *"What is the causal effect of the availability of Generative AI on employment rates in the US for roles of varying degrees of occupational exposure to Generative AI?"*

## Project Structure

```
.
├── data/                   # Contains raw and processed data files
│   └── bls_employment_data.csv  # The main dataset
├── docs/                   # Documentation
│   ├── VARIABLE_COOKBOOK.md     # Detailed description of variables and series
│   └── metadata.json            # Machine-readable metadata for the series
├── scripts/                # Python scripts for data collection
│   └── fetch_bls_data.py        # Script to fetch data from BLS API
└── README.md               # This file
```

## Data Description

The data is sourced from the **US Bureau of Labor Statistics (BLS)** and includes monthly time-series data from 2015 to 2025.

It covers two main surveys:
1.  **Current Employment Statistics (CES):** Employment levels and average hourly earnings.
2.  **Job Openings and Labor Turnover Survey (JOLTS):** Job openings and hires.

The data covers specific industries selected for their varying degrees of exposure to Generative AI:
*   **High Exposure:** Information; Professional, Scientific, and Technical Services; Finance and Insurance.
*   **Low Exposure (Control):** Leisure and Hospitality.
*   **Benchmark:** Total Nonfarm.

For a detailed list of variables, please refer to [docs/VARIABLE_COOKBOOK.md](docs/VARIABLE_COOKBOOK.md).

## How to Update the Data

To fetch the latest data or modify the series being collected:

1.  **Prerequisites:** Python 3.x installed.
2.  **Setup:**
    ```bash
    # Create a virtual environment (optional but recommended)
    python3 -m venv .venv
    source .venv/bin/activate
    
    # Install dependencies
    pip install requests
    ```
3.  **Run the script:**
    ```bash
    # Optional: Set your BLS API Key for higher rate limits (required for full state data)
    export BLS_API_KEY='your_api_key_here'
    
    python3 scripts/fetch_bls_data.py
    ```
    This will fetch the data from the BLS API and update `data/bls_employment_data.csv` and `docs/metadata.json`.

## Notes
*   The script supports fetching data for all 50 states + DC.
*   **Important:** Fetching state-level data requires a significant number of API requests. It is highly recommended to use a BLS API Registration Key (set via `BLS_API_KEY` environment variable) to avoid hitting daily rate limits. Unregistered users are limited to 25 series per day.
*   All data series are Seasonally Adjusted unless otherwise noted.
