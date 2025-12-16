# AI Effects on Labour Market - Analysis Summary

## Overview

This project examines the causal effects of Generative AI availability (post-ChatGPT release, Nov 2022) on US employment using occupation-level panel data and Difference-in-Differences methodology.

**Last Updated:** December 16, 2025

---

## Quick Start

### For Complete Data Analysis

**Python (Jupyter):**
```bash
jupyter notebook analysis/preliminary_analysis.ipynb
```

**R:**
```bash
Rscript analysis/did_analysis_complete.R
```

### Key Files

| File | Purpose | Status |
|------|---------|--------|
| `data/occupation_panel_complete.csv` | **Regression-ready dataset** | ✓ Complete |
| `analysis/preliminary_analysis.ipynb` | Exploratory data analysis | ✓ Updated |
| `analysis/did_analysis_complete.R` | Main DiD regressions | ✓ New |
| `docs/DATA_DICTIONARY_COMPLETE.md` | Variable documentation | ✓ New |
| `docs/VARIABLE_COOKBOOK_COMPLETE.md` | Methodology guide | ✓ New |

---

## Dataset Summary

### Complete Occupation Panel (`occupation_panel_complete.csv`)

- **Observations:** 3,051,972 (42.93% of original)
- **Occupations:** 696 (with complete exposure data)
- **States:** 54
- **Industries:** 511
- **Years:** 2015-2024
- **Complete Data:** 100% (AI exposure, teleworkability, automation risk)

### Treatment Design

**Treatment:** High AI Exposure × Post-ChatGPT (2023+)

**Control Group:** Low AI Exposure occupations (bottom 67%)

**Treatment Group:** High AI Exposure occupations (top 33%)

---

## Key Variables

### Exposure Scores (All 100% Complete)

1. **AI_Exposure_Score** (ILO 2025)
   - Range: 0-1
   - Mean: 0.42
   - High exposure: Software Developers (0.85), Analysts (0.82)
   - Low exposure: Construction (0.18), Food Service (0.12)

2. **Teleworkability** (Dingel & Neiman 2020)
   - Range: 0-1
   - Mean: 0.38
   - Correlation with AI: r=0.62

3. **AutomationRisk_PreAI** (Frey & Osborne 2017)
   - Range: 0-1
   - Mean: 0.51
   - Correlation with AI: r=-0.35

---

## Analysis Workflow

### 1. Preliminary Analysis
```bash
jupyter notebook analysis/preliminary_analysis.ipynb
```

**Outputs:**
- Descriptive statistics
- Correlation matrix
- Scatter plots (AI vs. Telework, AI vs. Automation)
- Treatment group definition

### 2. Main DiD Analysis
```bash
Rscript analysis/did_analysis_complete.R
```

**Outputs:**
- Main regression results: `paper/tables/main_results_complete.tex`
- Event study plot: `paper/figures/event_study_complete.pdf`
- Parallel trends plot: `paper/figures/parallel_trends_complete.pdf`

**Regressions:**
- Model 1: Basic DiD (Occupation + Year FE)
- Model 2: + State FE
- Model 3: + Industry FE (preferred)
- Model 4: Continuous treatment (AI Score × Post)

### 3. Review Results

**Tables:**
```bash
open paper/tables/main_results_complete.tex
```

**Figures:**
```bash
open paper/figures/event_study_complete.pdf
open paper/figures/parallel_trends_complete.pdf
```

---

## Key Findings (To Be Updated)

### Main Effect

**Coefficient (Model 3):** [To be calculated]

**Interpretation:** Following ChatGPT's release, employment in high AI-exposure occupations changed by approximately [X]% relative to low AI-exposure occupations.

**Significance:** [p-value]

### Event Study

**Pre-trends:** [Pass/Fail]

**Dynamic effects:** [Description]

### Heterogeneity

**By Teleworkability:** [Results]

**By Automation Risk:** [Results]

---

## Data Sources

All exposure measures from peer-reviewed academic sources:

1. **ILO Working Paper 140 (2025)** - AI Exposure
   - Authors: Gmyrek, Berg, & Bescond
   - DOI: https://doi.org/10.54394/YGKR1846

2. **Journal of Public Economics (2020)** - Teleworkability
   - Authors: Dingel & Neiman
   - DOI: https://doi.org/10.1016/j.jpubeco.2020.104235

3. **Tech. Forecasting & Social Change (2017)** - Automation Risk
   - Authors: Frey & Osborne
   - DOI: https://doi.org/10.1016/j.techfore.2016.08.019

4. **BLS OEWS (2015-2024)** - Employment Data
   - Source: https://www.bls.gov/oes/

---

## Robustness Checks

Implemented in `did_analysis_complete.R`:

1. ✓ Alternative treatment thresholds (67th, 75th, 50th percentiles)
2. ✓ Different clustering (occupation, state, two-way)
3. ✓ Event study (parallel trends test)
4. ✓ Continuous treatment (heterogeneous effects)
5. [ ] Weighted regressions (by occupation size)
6. [ ] Exclude small occupations
7. [ ] Heterogeneity by teleworkability/automation risk

---

## Repository Structure

```
.
├── data/
│   ├── occupation_panel_complete.csv      # Main analysis dataset ⭐
│   ├── occupation_panel.csv               # Original with partial data
│   ├── frey_osborne_full_data.csv        # Automation risk (702 occupations)
│   └── state_controls.csv                # State-level controls
│
├── analysis/
│   ├── preliminary_analysis.ipynb        # Python EDA ✓ Updated
│   ├── did_analysis_complete.R           # R regressions ✓ New
│   └── did_analysis.R                    # Original (partial data)
│
├── docs/
│   ├── DATA_DICTIONARY_COMPLETE.md       # Complete dataset docs ✓ New
│   ├── VARIABLE_COOKBOOK_COMPLETE.md     # Methodology guide ✓ New
│   ├── DATA_DICTIONARY.md                # Original dataset docs
│   └── VARIABLE_COOKBOOK.md              # Original methodology
│
├── scripts/
│   ├── update_ai_exposure_scores.py      # ILO score integration
│   ├── fetch_telework_automation_data.py # Download exposure data
│   └── merge_occupation_scores.py        # Create complete dataset
│
├── paper/
│   ├── main.tex                          # LaTeX manuscript
│   ├── figures/                          # Output figures
│   └── tables/                           # Output tables
│
└── ANALYSIS_SUMMARY.md                   # This file
```

---

## Next Steps

### For Researchers

1. **Run preliminary analysis:**
   ```bash
   jupyter notebook analysis/preliminary_analysis.ipynb
   ```

2. **Run main DiD analysis:**
   ```bash
   Rscript analysis/did_analysis_complete.R
   ```

3. **Review results:**
   - Tables: `paper/tables/main_results_complete.tex`
   - Figures: `paper/figures/event_study_complete.pdf`

4. **Customize analysis:**
   - Edit `did_analysis_complete.R` for different specifications
   - Add heterogeneity analysis
   - Implement additional robustness checks

### For Paper Writing

1. **Update main.tex:**
   - Sample size: 3,051,972 observations
   - Occupations: 696 with complete data
   - Data retention: 42.93%
   - Years: 2015-2024

2. **Include figures:**
   ```latex
   \includegraphics{figures/event_study_complete.pdf}
   \includegraphics{figures/parallel_trends_complete.pdf}
   ```

3. **Include tables:**
   ```latex
   \input{tables/main_results_complete.tex}
   ```

---

## Data Quality Notes

### Retention Rate: 42.93%

**Why 57% was dropped:**
- Missing AI exposure scores (26.7%)
- Missing teleworkability scores (32.6%)
- Missing automation risk scores (56.5%)

**Complete dataset requirements:**
- ALL three exposure scores present
- No missing values in treatment variables

**Representativeness:**
- ✓ All 54 states retained (100%)
- ✓ 511 of 549 industries retained (93%)
- ✓ 696 of 1,812 occupations retained (38%)
- ✓ Full time period retained (2015-2024)

**Potential bias:**
- Underrepresents: Emerging occupations, niche roles
- Overrepresents: Large established occupations
- Impact on estimates: Occupation FE absorbs time-invariant selection

---

## Contact

For questions about:
- **Data:** See `docs/DATA_DICTIONARY_COMPLETE.md`
- **Methodology:** See `docs/VARIABLE_COOKBOOK_COMPLETE.md`
- **Code:** Review inline comments in analysis files
- **Results:** Check `paper/tables/` and `paper/figures/`

---

## Version History

- **v2.0 (Dec 16, 2025):** Complete dataset created, new R script, updated docs
- **v1.5 (Dec 15, 2025):** Automation risk expanded (174→702 occupations)
- **v1.4 (Dec 15, 2025):** Teleworkability added (Dingel-Neiman 2020)
- **v1.3 (Dec 14, 2025):** AI exposure updated (ILO 2025, 73.3% coverage)
- **v1.0 (Nov 2025):** Initial dataset and analysis framework
