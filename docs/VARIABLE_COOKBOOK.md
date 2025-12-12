# Variable Cookbook

## Dataset Overview
This repository contains data and analysis for studying the causal effects of Generative AI availability on employment rates in the US, comparing industries with varying degrees of occupational exposure to Generative AI.

**Primary Analysis File:** `data/analysis_panel.csv`
**Raw Employment Data:** `data/bls_employment_data.csv`
**Time Range:** January 2015 - September 2025 (Monthly)
**Geographic Coverage:** 50 US States + District of Columbia + National Totals

---

## Analysis Panel Dataset

**File:** `data/analysis_panel.csv`

This is the regression-ready panel dataset for Difference-in-Differences analysis.

### Column Descriptions

| Variable | Description | Type | Example |
| :--- | :--- | :--- | :--- |
| `Date` | First day of the month | Date | `2023-01-01` |
| `Year` | Calendar year | Integer | `2023` |
| `Month` | Month number (1-12) | Integer | `1` |
| `YearMonth` | Year-month identifier (YYYYMM) | Integer | `202301` |
| `Period` | BLS period code | String | `M01` |
| `PeriodName` | Month name | String | `January` |
| `State` | US State or 'Total' for national | String | `California` |
| `Industry` | Industry sector | String | `Information` |
| `SeriesID` | BLS series identifier | String | `CES5000000001` |
| `Employment` | Employment level (thousands) | Float | `3050.5` |
| `LogEmployment` | Natural log of employment | Float | `8.02` |
| `Post` | Post-treatment indicator (1 if year ≥ 2023) | Binary | `1` |
| `HighExposure` | High AI exposure indicator (1 if AI score ≥ 0.45) | Binary | `1` |
| `Treat` | Treatment variable (HighExposure × Post) | Binary | `1` |
| `AI_Exposure_Score` | ILO GPT exposure score (0-1) | Float | `0.52` |
| `Teleworkability` | Share of jobs teleworkable (0-1) | Float | `0.72` |
| `RoutineTaskIndex` | Routine task intensity (0-1) | Float | `0.35` |
| `SkillIntensity` | Skill/education requirements (0-1) | Float | `0.58` |
| `AutomationRisk_PreAI` | Pre-AI automation risk (0-1) | Float | `0.25` |

---

## Treatment Variable Specification

The treatment follows a Difference-in-Differences design:

```
Treat(i,t) = HighExposure(i) × Post(t)
```

### Post(t)
- **Definition:** Binary indicator = 1 for years 2023-2025, = 0 for 2015-2022
- **Rationale:** ChatGPT publicly released November 30, 2022. The post-period captures the era of widespread GenAI availability.

### HighExposure(i)
- **Definition:** Binary indicator = 1 if industry AI_Exposure_Score ≥ 0.45
- **Source:** ILO Working Paper 96 (Gmyrek, Berg, & Bescond, 2023)
- **Classification:**
  - **High Exposure (Treat = 1):** Information (0.52), Finance & Insurance (0.50), Professional/Scientific/Technical Services (0.48)
  - **Low Exposure (Control = 0):** Leisure & Hospitality (0.28), Total Nonfarm benchmark (0.38)

---

## Industry-Level Control Variables

**File:** `data/industry_controls_with_sources.csv`

These are time-invariant characteristics at the industry level. In a panel regression with industry fixed effects, these are absorbed. They are included for descriptive purposes and potential heterogeneity analysis.

### AI Exposure Score
| Industry | Score | Classification |
| :--- | :---: | :--- |
| Information | 0.52 | HIGH |
| Finance and Insurance | 0.50 | HIGH |
| Professional, Scientific, and Technical Services | 0.48 | HIGH |
| Total Nonfarm | 0.38 | LOW (benchmark) |
| Leisure and Hospitality | 0.28 | LOW (control) |

**Source:** ILO Working Paper 96 - "Generative AI and Jobs: A Global Analysis of Potential Effects on Job Quantity and Quality" (Gmyrek, Berg, & Bescond, August 2023)

**Methodology:** Scores derived from GPT-4 task-level automation potential assessments mapped to ISCO-08 occupations, then aggregated to industry level. Scores range 0-1; >0.5 = medium exposure, >0.75 = high exposure.

**Citation:** Gmyrek, P., Berg, J., Bescond, D. 2023. *Generative AI and jobs: A global analysis of potential effects on job quantity and quality*, ILO Working Paper 96. Geneva: International Labour Office. https://doi.org/10.54394/FHEM8239

### Teleworkability
| Industry | Score |
| :--- | :---: |
| Finance and Insurance | 0.76 |
| Information | 0.72 |
| Professional, Scientific, and Technical Services | 0.68 |
| Total Nonfarm | 0.37 |
| Leisure and Hospitality | 0.04 |

**Source:** Dingel & Neiman (2020) - "How Many Jobs Can be Done at Home?" NBER Working Paper 26948

**Methodology:** Share of jobs that can feasibly be performed entirely from home, based on O*NET work context and activities data.

**Citation:** Dingel, J. I., & Neiman, B. (2020). *How many jobs can be done at home?* Journal of Public Economics, 189, 104235.

### Routine Task Index
| Industry | Score |
| :--- | :---: |
| Finance and Insurance | 0.55 |
| Total Nonfarm | 0.50 |
| Leisure and Hospitality | 0.45 |
| Information | 0.35 |
| Professional, Scientific, and Technical Services | 0.25 |

**Source:** Autor & Dorn (2013) methodology, based on O*NET task measures

**Methodology:** Combines measures of routine cognitive tasks, routine manual tasks, non-routine cognitive analytical, non-routine cognitive interpersonal, and non-routine manual physical tasks.

**Citation:** Autor, D. H., & Dorn, D. (2013). *The growth of low-skill service jobs and the polarization of the US labor market.* American Economic Review, 103(5), 1553-97.

### Skill Intensity
| Industry | Score |
| :--- | :---: |
| Professional, Scientific, and Technical Services | 0.72 |
| Information | 0.58 |
| Finance and Insurance | 0.52 |
| Total Nonfarm | 0.38 |
| Leisure and Hospitality | 0.12 |

**Source:** BLS Occupational Employment Statistics + O*NET Education Requirements

**Methodology:** Proxy based on share of workers in occupations requiring bachelor's degree or higher.

### Pre-AI Automation Risk
| Industry | Score |
| :--- | :---: |
| Leisure and Hospitality | 0.75 |
| Total Nonfarm | 0.47 |
| Finance and Insurance | 0.43 |
| Information | 0.25 |
| Professional, Scientific, and Technical Services | 0.18 |

**Source:** Frey & Osborne (2017) - "The Future of Employment"

**Methodology:** Probability of computerization by traditional automation technologies (robotics, rule-based software), calculated before the GenAI era.

**Citation:** Frey, C. B., & Osborne, M. A. (2017). *The future of employment: How susceptible are jobs to computerisation?* Technological Forecasting and Social Change, 114, 254-280.

---

## Raw Employment Data

**File:** `data/bls_employment_data.csv`

### Column Descriptions

| Variable | Description | Type | Example |
| :--- | :--- | :--- | :--- |
| `SeriesID` | BLS time series identifier | String | `CES5000000001` |
| `State` | US State or 'Total' for national | String | `California` |
| `Industry` | Industry sector | String | `Information` |
| `Metric` | Labor market measure | String | `All Employees` |
| `Source` | BLS survey (CES or JOLTS) | String | `CES` |
| `Unit` | Measurement unit | String | `Thousands` |
| `Year` | Calendar year | Integer | `2023` |
| `Period` | Month code | String | `M01` |
| `PeriodName` | Month name | String | `January` |
| `Value` | Recorded value | Float | `3050.5` |
| `Footnotes` | BLS notes | String | `Preliminary` |

### Industries Covered

| Industry | NAICS Code | BLS Supersector | AI Exposure |
| :--- | :---: | :---: | :--- |
| Information | 51 | 50 | HIGH |
| Finance and Insurance | 52 | 55 | HIGH |
| Professional, Scientific, and Technical Services | 54 | 60 | HIGH |
| Leisure and Hospitality | 71-72 | 70 | LOW |
| Total Nonfarm | -- | 00 | BENCHMARK |

### Data Sources

- **CES (Current Employment Statistics):** Monthly employment, hours, and earnings from establishment surveys. [BLS CES](https://www.bls.gov/ces/)
- **JOLTS (Job Openings and Labor Turnover Survey):** Monthly job openings, hires, and separations. [BLS JOLTS](https://www.bls.gov/jlt/)

---

## Fixed Effects Strategy

For a Difference-in-Differences regression with panel data:

```
log(Employment_ist) = β₁(Treat_it) + α_i + γ_t + δ_s + ε_ist
```

Where:
- `α_i` = Industry fixed effects (absorbs time-invariant industry characteristics: AI exposure, teleworkability, RTI, skill intensity, pre-AI automation risk)
- `γ_t` = Time fixed effects (absorbs economy-wide shocks)
- `δ_s` = State fixed effects (absorbs time-invariant state characteristics)
- `β₁` = **Causal effect of GenAI availability on employment in high-exposure industries**

### Alternative: Continuous Treatment Intensity

Instead of binary HighExposure, use AI_Exposure_Score as continuous treatment:

```
log(Employment_ist) = β₁(AI_Exposure_i × Post_t) + α_i + γ_t + δ_s + ε_ist
```

This captures heterogeneous effects by exposure intensity.

---

## Data Quality Notes

1. **Seasonally Adjusted:** All BLS series are seasonally adjusted unless otherwise noted.
2. **State Coverage:** Some state-industry combinations may have missing data if BLS suppresses for confidentiality.
3. **COVID-19:** The 2020 period shows significant employment disruptions due to the pandemic. Consider robustness checks excluding 2020.
4. **Preliminary Data:** Recent months may contain preliminary estimates subject to revision.

---

## References

- Gmyrek, P., Berg, J., & Bescond, D. (2023). *Generative AI and jobs: A global analysis of potential effects on job quantity and quality.* ILO Working Paper 96.
- Dingel, J. I., & Neiman, B. (2020). *How many jobs can be done at home?* Journal of Public Economics, 189, 104235.
- Autor, D. H., & Dorn, D. (2013). *The growth of low-skill service jobs and the polarization of the US labor market.* American Economic Review, 103(5), 1553-97.
- Frey, C. B., & Osborne, M. A. (2017). *The future of employment: How susceptible are jobs to computerisation?* Technological Forecasting and Social Change, 114, 254-280.
- Felten, E., Raj, M., & Seamans, R. (2021). *Occupational, industry, and geographic exposure to artificial intelligence: A novel dataset and its potential uses.* Strategic Management Journal, 42(12), 2195-2217.
