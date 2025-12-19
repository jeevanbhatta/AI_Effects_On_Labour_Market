# Data Codebook

**Dataset:** Complete Occupation Panel  
**File:** `data/occupation_panel_complete.csv`  
**Observations:** 3,051,972  
**Period:** 2015-2024 (annual)  
**Last Updated:** December 19, 2025

---

## Variable Definitions

| Variable Name | Description | Format | Unit | Data Source |
|---------------|-------------|--------|------|-------------|
| `Occupation` | Occupational category (SOC 2018 code) | Categorical (string) | Occupation code | BLS Occupational Employment Statistics (OES); crosswalked from ISCO-08 using JOLTS crosswalk |
| `AI_Exposure_Score` | Occupation-level AI exposure index capturing the likelihood that tasks are augmented or replaced by generative AI | Continuous (float) | Exposure score (0-1 scale) | ILO Working Paper 140 (2025): "Generative AI and jobs" by Gmyrek, Berg, & Bescond. Task-to-AI mapping using GPT-4 assessments. [https://doi.org/10.54394/YGKR1846](https://doi.org/10.54394/YGKR1846) |
| `Year` | Calendar year associated with occupation-level observation | Discrete (integer) | Calendar year | BLS OES (annual May reference period) |
| `Employment` | Employment level for given occupation-state-industry-year | Continuous (float) | Count (number of workers) | BLS OES |
| `LogEmployment` | Natural logarithm of employment | Continuous (float) | Log count | Derived from `Employment` |
| `AutomationRisk_PreAI` | Index measuring pre-AI exposure of occupations to automation from traditional technologies (ICT, robotics) | Continuous (float) | Probability (0-1 scale) | Frey, C. B., & Osborne, M. A. (2017). "The future of employment: How susceptible are jobs to computerisation?" Technological Forecasting and Social Change, 114, 254-280. Machine learning assessment trained on expert evaluations. [https://doi.org/10.1016/j.techfore.2016.08.019](https://doi.org/10.1016/j.techfore.2016.08.019) |
| `Teleworkability` | Index capturing the feasibility of performing occupational tasks remotely | Continuous (float) | Share (0-1 scale) | Dingel, J. I., & Neiman, B. (2020). "How many jobs can be done at home?" Journal of Public Economics, 189, 104235. Based on O*NET work context and activities analysis. [https://doi.org/10.1016/j.jpubeco.2020.104235](https://doi.org/10.1016/j.jpubeco.2020.104235) |
| `Post` | Binary indicator for post-ChatGPT period | Binary (0/1) | Indicator | Derived (1 for 2023-2024; 0 for 2015-2022) |
| `State` | State FIPS code | Integer | State code | BLS OES |
| `Industry` | NAICS industry code | Integer | Industry code | BLS OES |

---

## Summary Statistics

### Exposure Variables

| Variable | Mean | Std Dev | Min | 25th Pct | Median | 75th Pct | Max |
|----------|------|---------|-----|----------|--------|----------|-----|
| `AI_Exposure_Score` | 0.42 | 0.18 | 0.05 | 0.28 | 0.40 | 0.54 | 0.95 |
| `Teleworkability` | 0.38 | 0.27 | 0.00 | 0.15 | 0.34 | 0.60 | 1.00 |
| `AutomationRisk_PreAI` | 0.51 | 0.28 | 0.003 | 0.28 | 0.55 | 0.71 | 0.99 |

### Correlation Matrix

|  | AI_Exposure | Teleworkability | AutomationRisk_PreAI |
|--|-------------|-----------------|---------------------|
| **AI_Exposure_Score** | 1.00 | 0.62 | -0.35 |
| **Teleworkability** | 0.62 | 1.00 | -0.54 |
| **AutomationRisk_PreAI** | -0.35 | -0.54 | 1.00 |

---

## Dataset Coverage

- **Occupations:** 696 SOC codes (38% of original 1,812)
- **States:** 54 (50 states + DC, PR, VI, National)
- **Industries:** 511 NAICS codes (93% of original 549)
- **Years:** 10 (2015-2024)
- **Retention rate:** 42.93% of original observations (complete cases only)

---

## Treatment Variable Construction

For Difference-in-Differences analysis:

**Treatment Group:** High AI Exposure occupations (top 33% by AI_Exposure_Score, ≥67th percentile)

**Control Group:** Low AI Exposure occupations (bottom 67%)

**Treatment Period:** Post = 1 for years 2023-2024 (post-ChatGPT release)

**Pre-Treatment Period:** Post = 0 for years 2015-2022

**Treatment Variable:** `Treat = HighAIExposure × Post`

---

## Example Occupations

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

### Low AI Exposure (<0.30)
- Construction Laborers (0.18)
- Janitors (0.15)
- Food Service Workers (0.12)
- Agricultural Workers (0.08)

---

## References

1. **Gmyrek, P., Berg, J., & Bescond, D. (2025).** *Generative AI and jobs: A global analysis of potential effects on job quantity and quality.* ILO Working Paper 140. Geneva: International Labour Office. https://doi.org/10.54394/YGKR1846

2. **Dingel, J. I., & Neiman, B. (2020).** *How many jobs can be done at home?* Journal of Public Economics, 189, 104235. https://doi.org/10.1016/j.jpubeco.2020.104235

3. **Frey, C. B., & Osborne, M. A. (2017).** *The future of employment: How susceptible are jobs to computerisation?* Technological Forecasting and Social Change, 114, 254-280. https://doi.org/10.1016/j.techfore.2016.08.019

4. **Bureau of Labor Statistics.** *Occupational Employment and Wage Statistics (OES).* U.S. Department of Labor. https://www.bls.gov/oes/
