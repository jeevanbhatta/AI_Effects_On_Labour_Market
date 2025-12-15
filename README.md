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
│   ├── occupation_panel.csv            # MAIN: 7.1M occupation-level observations (1.1 GB, not in Git)
│   ├── state_controls.csv              # State-level unemployment & labor force
│   ├── oes_raw/                        # Raw BLS OES files (1.3 GB, not in Git)
│   │   └── oes_research_YYYY_allsectors.xlsx (10 files, 2015-2024)
│   └── archive/                        # Old industry-level files
├── docs/
│   ├── VARIABLE_COOKBOOK.md            # Comprehensive variable documentation
│   ├── metadata.json                   # Machine-readable series metadata
│   └── ilo_report.txt                  # ILO Working Paper 96 (text extract)
├── scripts/
│   ├── build_occupation_panel.py       # MAIN: Builds occupation-level panel
│   └── archive/                        # Old industry-level scripts
├── .env                                # BLS API key (not tracked)
└── README.md
```

**Note:** Large data files (occupation_panel.csv, oes_raw/*.xlsx) are excluded from Git. Run the scripts to regenerate.

## Data Summary

**Current Dataset:** Occupation-Level Panel (State × Industry × Occupation × Year)

| Statistic | Value |
| :--- | :--- |
| **Observations** | 7,108,826 |
| **Time Period** | 2015-2024 (Annual, May reference) |
| **Geographic Units** | 54 (50 states + DC + PR + VI + national) |
| **Industries** | 5 NAICS sectors |
| **Occupations** | 832 SOC codes |
| **Pre-period observations** | 5,538,093 (2015-2022) |
| **Post-period observations** | 1,570,733 (2023-2024) |
| **File Size** | 1,065.9 MB (excluded from Git) |

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
pip install pandas openpyxl numpy
```

### 2. Download Raw OES Data (1.3 GB)
Download 10 files from BLS OES Special Requests page:
```bash
mkdir -p data/oes_raw
cd data/oes_raw

# Download manually from browser (faster):
# https://www.bls.gov/oes/special-requests/oes_research_2024_allsectors.xlsx
# ... (2015-2024)

# Or use curl (may be slow):
for year in {2015..2024}; do
  curl -O https://www.bls.gov/oes/special-requests/oes_research_${year}_allsectors.xlsx
done
```

### 3. Build Occupation Panel
```bash
cd ../..
python scripts/build_occupation_panel.py
# Takes ~8 minutes, creates data/occupation_panel.csv (1.1 GB)
```

### 4. Test Mode (Quick Validation)
```bash
python scripts/build_occupation_panel.py --test
# Processes only 2024 (~50 seconds)
```

## Documentation

For comprehensive variable documentation, see [docs/VARIABLE_COOKBOOK.md](docs/VARIABLE_COOKBOOK.md).

## Key References

- Gmyrek, P., Berg, J., & Bescond, D. (2023). *Generative AI and jobs: A global analysis of potential effects on job quantity and quality.* ILO Working Paper 96.
- Dingel, J. I., & Neiman, B. (2020). *How many jobs can be done at home?* Journal of Public Economics.
- Autor, D. H., & Dorn, D. (2013). *The growth of low-skill service jobs and the polarization of the US labor market.* American Economic Review.
- Frey, C. B., & Osborne, M. A. (2017). *The future of employment.* Technological Forecasting and Social Change.
