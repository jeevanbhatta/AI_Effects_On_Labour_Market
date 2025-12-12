# AI Effects on Labor Market Data Repository

This repository contains data and scripts to support the research paper: *"What is the causal effect of the availability of Generative AI on employment rates in the US for roles of varying degrees of occupational exposure to Generative AI?"*

## Research Design

**Method:** Difference-in-Differences (DiD)

**Treatment:** Availability of Generative AI (post-ChatGPT release, November 2022)

**Treatment Group:** Industries with high AI exposure (Information; Professional, Scientific, and Technical Services; Finance and Insurance)

**Control Group:** Industries with low AI exposure (Leisure and Hospitality)

## Project Structure

```
.
├── data/
│   ├── analysis_panel.csv              # Regression-ready panel dataset
│   ├── bls_employment_data.csv         # Raw BLS employment data
│   ├── industry_controls_with_sources.csv  # Control variables with citations
│   └── industry_static_controls.csv    # Legacy static controls
├── docs/
│   ├── VARIABLE_COOKBOOK.md            # Comprehensive variable documentation
│   ├── metadata.json                   # Machine-readable series metadata
│   └── ilo_report.txt                  # ILO Working Paper 96 (text extract)
├── scripts/
│   ├── fetch_bls_data.py               # Main BLS data fetcher
│   ├── fetch_remaining_data.py         # Resume incomplete fetches
│   ├── fetch_information_industry.py   # Information industry data fetcher
│   └── build_analysis_dataset.py       # Builds regression-ready panel
├── .env                                # BLS API key (not tracked)
└── README.md
```

## Data Summary

| Statistic | Value |
| :--- | :--- |
| **Observations** | 31,152 |
| **Time Period** | Jan 2015 - Sep 2025 |
| **Geographic Units** | 52 (50 states + DC + national) |
| **Industries** | 5 |
| **Pre-period observations** | 24,288 |
| **Post-period observations** | 6,864 |
| **Treated observations** | 4,197 |

## Industries and AI Exposure Classification

| Industry | AI Exposure Score | Classification | Source |
| :--- | :---: | :--- | :--- |
| Information | 0.52 | HIGH | ILO WP 96 |
| Finance and Insurance | 0.50 | HIGH | ILO WP 96 |
| Prof., Scientific, Tech. Services | 0.48 | HIGH | ILO WP 96 |
| Total Nonfarm | 0.38 | BENCHMARK | ILO WP 96 |
| Leisure and Hospitality | 0.28 | LOW (Control) | ILO WP 96 |

## Control Variables

All control variables are time-invariant at the industry level and absorbed by industry fixed effects:

| Variable | Description | Source |
| :--- | :--- | :--- |
| AI_Exposure_Score | GPT automation potential (0-1) | Gmyrek et al. (2023) ILO |
| Teleworkability | Share of teleworkable jobs | Dingel & Neiman (2020) |
| RoutineTaskIndex | Routine task intensity | Autor & Dorn (2013) |
| SkillIntensity | Education requirements | BLS OES + O*NET |
| AutomationRisk_PreAI | Pre-AI automation probability | Frey & Osborne (2017) |

## Quick Start

### 1. Setup Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install requests pandas numpy
```

### 2. Set API Key (Required for full data)
```bash
# Get a free key at https://data.bls.gov/registrationEngine/
export BLS_API_KEY='your_key_here'
# Or create a .env file with: BLS_API_KEY='your_key_here'
```

### 3. Fetch Data
```bash
python3 scripts/fetch_bls_data.py
```

### 4. Build Analysis Dataset
```bash
python3 scripts/build_analysis_dataset.py
```

## Documentation

For comprehensive variable documentation, see [docs/VARIABLE_COOKBOOK.md](docs/VARIABLE_COOKBOOK.md).

## Key References

- Gmyrek, P., Berg, J., & Bescond, D. (2023). *Generative AI and jobs: A global analysis of potential effects on job quantity and quality.* ILO Working Paper 96.
- Dingel, J. I., & Neiman, B. (2020). *How many jobs can be done at home?* Journal of Public Economics.
- Autor, D. H., & Dorn, D. (2013). *The growth of low-skill service jobs and the polarization of the US labor market.* American Economic Review.
- Frey, C. B., & Osborne, M. A. (2017). *The future of employment.* Technological Forecasting and Social Change.
