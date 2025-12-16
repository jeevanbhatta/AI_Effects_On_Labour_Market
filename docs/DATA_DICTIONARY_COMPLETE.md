# Data Dictionary: Occupation Panel (Complete Data Only)

Generated from: `data/occupation_panel_complete.csv`

**Total Observations:** 3,051,972 (42.93% of original 7,108,826 rows)

**Date Generated:** December 16, 2025

**Complete Data Criteria:** Only includes rows where all three key exposure variables (AI_Exposure_Score, Teleworkability, AutomationRisk_PreAI) have non-missing values. SkillIntensity and RoutineTaskIndex are excluded from the complete dataset.

---

## Dataset Characteristics

- **Unique Occupations:** 696 (with complete exposure data)
- **Unique States:** 54
- **Unique Industries:** 511
- **Years:** 2015-2024 (10 years)
- **Coverage:** 42.93% retention of original observations

---

## Variable Descriptions

### Identifiers

| Variable | Type | Description | Example |
|----------|------|-------------|---------|
| `Occupation` | String | SOC occupation code | `15-1132` |
| `State` | Integer | State FIPS code | `6` (California) |
| `Industry` | Integer | Industry code | `5112` |
| `Year` | Integer | Calendar year | `2023` |

### Employment Measures

| Variable | Type | Description | Range |
|----------|------|-------------|-------|
| `Employment` | Float | Employment level (count) | 0 to millions |
| `LogEmployment` | Float | Natural log of employment | Real number |

### Treatment Variables

| Variable | Type | Description | Values |
|----------|------|-------------|--------|
| `Post` | Binary | Post-ChatGPT period indicator | 0 (2015-2022), 1 (2023-2024) |

### Exposure Scores (Complete Data)

All observations have non-missing values for these three variables:

| Variable | Type | Description | Range | Source |
|----------|------|-------------|-------|--------|
| `AI_Exposure_Score` | Float | Occupation-level AI exposure | 0.0 - 1.0 | ILO 2025 |
| `Teleworkability` | Float | Share of tasks teleworkable | 0.0 - 1.0 | Dingel & Neiman 2020 |
| `AutomationRisk_PreAI` | Float | Pre-AI automation probability | 0.0 - 1.0 | Frey & Osborne 2017 |

**Note:** SkillIntensity and RoutineTaskIndex are **excluded** from the complete dataset due to insufficient coverage.

---

## Data Sources

### AI Exposure Score
- **Source:** ILO Working Paper 140 (2025) - "Generative AI and jobs: A global analysis of potential effects on job quantity and quality"
- **Authors:** Gmyrek, P., Berg, J., & Bescond, D.
- **Coverage in Complete Dataset:** 100% (by definition)
- **Original Coverage:** 73.3% of full dataset
- **Methodology:** GPT-4 task-level automation assessments mapped to ISCO-08, crosswalked to SOC 2018
- **DOI:** https://doi.org/10.54394/YGKR1846

### Teleworkability
- **Source:** Dingel & Neiman (2020) - "How Many Jobs Can be Done at Home?"
- **Journal:** Journal of Public Economics, 189, 104235
- **Coverage in Complete Dataset:** 100% (by definition)
- **Original Coverage:** 67.4% of full dataset
- **Methodology:** O*NET work context and activities analysis
- **DOI:** https://doi.org/10.1016/j.jpubeco.2020.104235

### Automation Risk (Pre-AI)
- **Source:** Frey & Osborne (2017) - "The Future of Employment: How Susceptible Are Jobs to Computerisation?"
- **Journal:** Technological Forecasting and Social Change, 114, 254-280
- **Coverage in Complete Dataset:** 100% (by definition)
- **Original Coverage:** 43.5% of full dataset (improved from 31.3% by extracting full PDF appendix)
- **Number of Occupations:** 702 SOC codes
- **Methodology:** Machine learning assessment of computerization probability via traditional automation
- **DOI:** https://doi.org/10.1016/j.techfore.2016.08.019

---

## Treatment Group Definition

For Difference-in-Differences analysis, treatment groups can be defined using AI exposure:

```r
# High AI Exposure: Top 33% (67th percentile threshold)
AI_threshold <- quantile(df$AI_Exposure_Score, 0.67)
HighAIExposure <- as.integer(df$AI_Exposure_Score >= AI_threshold)

# Treatment variable
Treat <- HighAIExposure * Post
```

**Recommended Thresholds:**
- 67th percentile: Top 33% as "high exposure"
- 75th percentile: Top 25% as "very high exposure"
- 50th percentile: Top 50% as "above-median exposure"

---

## Summary Statistics (Complete Data)

### Exposure Score Distribution

| Statistic | AI_Exposure | Teleworkability | AutomationRisk |
|-----------|-------------|-----------------|----------------|
| Mean | 0.42 | 0.38 | 0.51 |
| Std Dev | 0.18 | 0.27 | 0.28 |
| Min | 0.05 | 0.00 | 0.003 |
| 25th Percentile | 0.28 | 0.15 | 0.28 |
| Median | 0.40 | 0.34 | 0.55 |
| 75th Percentile | 0.54 | 0.60 | 0.71 |
| Max | 0.95 | 1.00 | 0.99 |

### Correlation Matrix

|  | AI_Exposure | Telework | Automation |
|--|-------------|----------|------------|
| **AI_Exposure** | 1.00 | 0.62 | -0.35 |
| **Telework** | 0.62 | 1.00 | -0.54 |
| **Automation** | -0.35 | -0.54 | 1.00 |

**Interpretation:**
- High AI exposure correlates with teleworkability (r=0.62): Cognitive work amenable to both
- High automation risk correlates with low teleworkability (r=-0.54): Manual/physical jobs
- High AI exposure correlates with low traditional automation risk (r=-0.35): Different types of work

---

## Example Occupations by Exposure Level

### High AI Exposure (>0.70)
- Software Developers (0.85)
- Market Research Analysts (0.82)
- Financial Analysts (0.78)
- Technical Writers (0.75)
- Accountants (0.72)

### Medium AI Exposure (0.40-0.60)
- Registered Nurses (0.52)
- Sales Representatives (0.48)
- Customer Service Representatives (0.45)
- Office Clerks (0.42)

### Low AI Exposure (<0.30)
- Construction Laborers (0.18)
- Janitors (0.15)
- Food Service Workers (0.12)
- Agricultural Workers (0.08)

---

## Data Quality Notes

1. **Complete Cases Only:** This dataset contains only observations with all three exposure scores present.
2. **Retention Rate:** 42.93% of original observations retained (3,051,972 of 7,108,826).
3. **Excluded Variables:** SkillIntensity and RoutineTaskIndex removed due to insufficient data.
4. **Bias Assessment:** Complete-case analysis may underrepresent:
   - Newer occupations (less likely in historical databases)
   - Niche occupations (less likely in crosswalks)
   - State-specific occupation variants
5. **Robustness:** Despite 57% data loss, retained observations span:
   - All 54 states/territories
   - 511 of 549 industries (93%)
   - 696 of 1,812 occupations (38%)
   - Full time period (2015-2024)

---

## Comparison to Original Dataset

| Characteristic | Original | Complete | Retention |
|----------------|----------|----------|-----------|
| Total Observations | 7,108,826 | 3,051,972 | 42.93% |
| Occupations | 1,812 | 696 | 38.41% |
| States | 54 | 54 | 100% |
| Industries | 549 | 511 | 93.08% |
| Years | 10 | 10 | 100% |
| AI Score Coverage | 73.3% | 100% | -- |
| Telework Coverage | 67.4% | 100% | -- |
| Automation Coverage | 43.5% | 100% | -- |

---

## Recommended Analysis Approach

### Difference-in-Differences Specification

```r
# Model 1: Basic DiD with Occupation and Year FE
feols(LogEmployment ~ Treat | Occupation + Year, data = df, cluster = ~Occupation)

# Model 2: Add State FE
feols(LogEmployment ~ Treat | Occupation + Year + State, data = df, cluster = ~Occupation)

# Model 3: Add Industry FE (full specification)
feols(LogEmployment ~ Treat | Occupation + Year + State + Industry, 
      data = df, cluster = ~Occupation)

# Model 4: Continuous treatment
feols(LogEmployment ~ AI_Exposure_Score:Post | Occupation + Year + State + Industry,
      data = df, cluster = ~Occupation)
```

### Heterogeneity Analysis

```r
# By teleworkability terciles
df$TeleworkGroup <- cut(df$Teleworkability, breaks = c(0, 0.33, 0.67, 1.0))

# By automation risk terciles
df$AutoGroup <- cut(df$AutomationRisk_PreAI, breaks = c(0, 0.33, 0.67, 1.0))

# Interaction effects
feols(LogEmployment ~ Treat:TeleworkGroup | Occupation + Year + State + Industry,
      data = df, cluster = ~Occupation)
```

---

## References

1. **Gmyrek, P., Berg, J., & Bescond, D. (2025).** *Generative AI and jobs: A global analysis of potential effects on job quantity and quality.* ILO Working Paper 140. Geneva: International Labour Office. https://doi.org/10.54394/YGKR1846

2. **Dingel, J. I., & Neiman, B. (2020).** *How many jobs can be done at home?* Journal of Public Economics, 189, 104235. https://doi.org/10.1016/j.jpubeco.2020.104235

3. **Frey, C. B., & Osborne, M. A. (2017).** *The future of employment: How susceptible are jobs to computerisation?* Technological Forecasting and Social Change, 114, 254-280. https://doi.org/10.1016/j.techfore.2016.08.019

---

## File Metadata

- **Created:** December 16, 2025
- **Python Environment:** Python 3.x with pandas, numpy
- **R Environment:** R 4.x with fixest, tidyverse
- **Encoding:** UTF-8
- **Missing Values:** None (by design - complete cases only)
- **File Size:** ~150 MB
