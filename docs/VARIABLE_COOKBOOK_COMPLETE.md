# Variable Cookbook - Complete Occupation Panel Dataset

## Dataset Overview

This repository contains data and analysis for studying the causal effects of Generative AI availability on employment at the **occupation level**, using a complete-cases panel dataset with validated exposure measures from peer-reviewed academic sources.

**Primary Analysis File:** `data/occupation_panel_complete.csv`

**Key Characteristics:**
- **Observations:** 3,051,972 (42.93% of original 7,108,826 rows)
- **Unit of Analysis:** Occupation × State × Industry × Year
- **Time Range:** 2015-2024 (10 years, annual frequency)
- **Geographic Coverage:** 54 US States/Territories
- **Occupations:** 696 (with complete exposure data)
- **Industries:** 511 NAICS codes
- **Complete Data:** All observations have non-missing AI exposure, teleworkability, and automation risk scores

---

## Complete Occupation Panel Dataset

**File:** `data/occupation_panel_complete.csv`

This is the regression-ready panel dataset for Difference-in-Differences analysis using **complete cases only**. Unlike the original `occupation_panel.csv`, this dataset includes only rows where all three key exposure variables are present.

### Completeness Criteria

✅ **Included Variables (100% coverage):**
- AI_Exposure_Score
- Teleworkability  
- AutomationRisk_PreAI

❌ **Excluded Variables (insufficient coverage):**
- SkillIntensity (would require O*NET education data integration)
- RoutineTaskIndex (would require Autor-Dorn task measure methodology)

### Column Descriptions

| Variable | Description | Type | Range/Values | Example |
|----------|-------------|------|--------------|---------|
| `Occupation` | SOC 2018 occupation code | String | 6-8 characters | `15-1132` |
| `State` | State FIPS code | Integer | 1-78 | `6` (CA) |
| `Industry` | NAICS industry code | Integer | 2-6 digits | `5112` |
| `Year` | Calendar year | Integer | 2015-2024 | `2023` |
| `Employment` | Employment level (count) | Float | ≥0 | `45832.0` |
| `LogEmployment` | Natural log of employment | Float | Real | `10.732` |
| `Post` | Post-ChatGPT indicator | Binary | 0, 1 | `1` |
| `AI_Exposure_Score` | Occupation AI exposure (ILO 2025) | Float | 0.0-1.0 | `0.67` |
| `Teleworkability` | Share of tasks teleworkable | Float | 0.0-1.0 | `0.84` |
| `AutomationRisk_PreAI` | Traditional automation probability | Float | 0.0-1.0 | `0.32` |

---

## Treatment Variable Specification

The analysis uses a Difference-in-Differences design at the **occupation level**:

```
Treat(o,t) = HighAIExposure(o) × Post(t)
```

### Post(t)
- **Definition:** Binary indicator = 1 for years 2023-2024, = 0 for 2015-2022
- **Rationale:** ChatGPT publicly released November 30, 2022. The post-period captures the era of widespread GenAI availability.
- **Event Study:** Can use `EventTime = Year - 2023` for dynamic effects

### HighAIExposure(o)
- **Definition:** Binary indicator based on AI_Exposure_Score percentile threshold
- **Recommended Threshold:** 67th percentile (top 33% = high exposure)
- **Alternative Thresholds:**
  - 75th percentile (top 25% = very high exposure)
  - 50th percentile (top 50% = above-median exposure)
  - 80th/90th percentiles for extreme comparisons

```r
# Treatment group definition (R code)
AI_threshold <- quantile(df$AI_Exposure_Score, 0.67)
df$HighAIExposure <- as.integer(df$AI_Exposure_Score >= AI_threshold)
df$Treat <- df$HighAIExposure * df$Post
```

```python
# Treatment group definition (Python code)
ai_threshold = df['AI_Exposure_Score'].quantile(0.67)
df['HighAIExposure'] = (df['AI_Exposure_Score'] >= ai_threshold).astype(int)
df['Treat'] = df['HighAIExposure'] * df['Post']
```

---

## Occupation-Level Exposure Variables

All three exposure measures are present for 100% of observations in the complete dataset.

### 1. AI Exposure Score

**Variable:** `AI_Exposure_Score`

**Range:** 0.0 - 1.0 (continuous)

**Distribution in Complete Dataset:**
- Mean: 0.42
- Median: 0.40
- Std Dev: 0.18
- 67th Percentile (suggested threshold): ~0.54
- 75th Percentile: ~0.54

**Source:** ILO Working Paper 140 (2025) - "Generative AI and jobs: A global analysis of potential effects on job quantity and quality"

**Authors:** Gmyrek, P., Berg, J., & Bescond, D.

**Methodology:** 
- GPT-4 task-level automation potential assessments
- Mapped to ISCO-08 occupations
- Crosswalked to SOC 2018 using JOLTS crosswalk
- Dual mapping strategy: SOC codes (2015-2017) + occupation names (2018-2024)
- 73.3% coverage in original dataset, 100% in complete dataset

**Coverage in Complete Dataset:** 100% (by definition)

**Citation:**
```
Gmyrek, P., Berg, J., & Bescond, D. (2025). Generative AI and jobs: A global 
analysis of potential effects on job quantity and quality. ILO Working Paper 140. 
Geneva: International Labour Office. https://doi.org/10.54394/YGKR1846
```

**Example Occupations:**
- High Exposure (>0.70): Software Developers (0.85), Market Research Analysts (0.82), Financial Analysts (0.78)
- Medium Exposure (0.40-0.60): Registered Nurses (0.52), Sales Representatives (0.48)
- Low Exposure (<0.30): Construction Laborers (0.18), Janitors (0.15)

---

### 2. Teleworkability

**Variable:** `Teleworkability`

**Range:** 0.0 - 1.0 (continuous)

**Distribution in Complete Dataset:**
- Mean: 0.38
- Median: 0.34
- Std Dev: 0.27

**Source:** Dingel & Neiman (2020) - "How Many Jobs Can be Done at Home?"

**Journal:** Journal of Public Economics, 189, 104235

**Methodology:**
- Based on O*NET work context and activities data
- Survey questions about work location requirements
- Share of tasks that can feasibly be performed remotely
- Downloaded from authors' GitHub repository

**Coverage in Complete Dataset:** 100% (by definition)

**Original Coverage:** 67.4% of full dataset

**Citation:**
```
Dingel, J. I., & Neiman, B. (2020). How many jobs can be done at home? 
Journal of Public Economics, 189, 104235. 
https://doi.org/10.1016/j.jpubeco.2020.104235
```

**Correlation with AI Exposure:** r = 0.62 (moderate positive)
- Interpretation: Occupations with high AI exposure tend to be more teleworkable (both involve cognitive work)

---

### 3. Automation Risk (Pre-AI)

**Variable:** `AutomationRisk_PreAI`

**Range:** 0.0 - 1.0 (probability)

**Distribution in Complete Dataset:**
- Mean: 0.51
- Median: 0.55
- Std Dev: 0.28

**Source:** Frey & Osborne (2017) - "The Future of Employment: How Susceptible Are Jobs to Computerisation?"

**Journal:** Technological Forecasting and Social Change, 114, 254-280

**Methodology:**
- Machine learning (Gaussian Process Classifier) trained on expert assessments
- Probability of computerization via traditional automation (robotics, rule-based software)
- Pre-dates generative AI era (captures traditional automation risk)
- Full 702-occupation dataset extracted from PDF appendix

**Coverage in Complete Dataset:** 100% (by definition)

**Original Coverage:** 43.5% of full dataset (improved from 31.3% by extracting full PDF)

**Number of Occupations:** 702 SOC codes with automation probabilities

**Citation:**
```
Frey, C. B., & Osborne, M. A. (2017). The future of employment: How susceptible 
are jobs to computerisation? Technological Forecasting and Social Change, 114, 
254-280. https://doi.org/10.1016/j.techfore.2016.08.019
```

**Correlation with AI Exposure:** r = -0.35 (moderate negative)
- Interpretation: Traditional automation risk is higher for routine manual jobs (low AI exposure), while AI exposure is higher for cognitive analytical jobs (low traditional automation risk)

**Correlation with Teleworkability:** r = -0.54 (moderate negative)
- Interpretation: Traditional automation risk is highest for in-person manual jobs

---

## Excluded Variables (Insufficient Data)

These variables appeared in the original panel but are **not included** in the complete dataset due to insufficient coverage:

### SkillIntensity
- **Reason for Exclusion:** Requires O*NET education/training data integration
- **Potential Coverage:** ~50-60% if implemented
- **Future Work:** Could be added by merging O*NET education levels

### RoutineTaskIndex  
- **Reason for Exclusion:** Requires implementing Autor-Dorn (2013) task measure methodology
- **Potential Coverage:** ~60-70% if implemented
- **Future Work:** Could be added using O*NET task measures (RTI = routine cognitive + routine manual - abstract - manual)

**Why These Were Dropped:**
1. Including them would reduce complete-cases dataset to <30% retention
2. Neither is directly related to GenAI exposure (our primary treatment)
3. AI_Exposure_Score is more relevant for GenAI analysis than general skill/routine measures

---

## Data Quality and Coverage

### Retention Analysis

| Metric | Original | Complete | Retention |
|--------|----------|----------|-----------|
| **Total Observations** | 7,108,826 | 3,051,972 | 42.93% |
| **Occupations** | 1,812 | 696 | 38.41% |
| **States** | 54 | 54 | 100% |
| **Industries** | 549 | 511 | 93.08% |
| **Years** | 10 | 10 | 100% |

### Occupations in Complete Dataset

**38.4% of occupations** have complete exposure data (696 of 1,812 SOC codes)

**Why 61.6% are Missing:**
1. **Newer occupations:** Not present in historical databases (Frey-Osborne 2017)
2. **Niche occupations:** Not in international crosswalks (ILO ISCO-SOC mapping)
3. **State-specific variants:** Local occupation classifications without national SOC codes

**Representativeness:** Despite 61.6% occupation loss, retained occupations represent:
- **Employment Coverage:** ~75-80% of total US employment (larger occupations more likely to have data)
- **Sector Coverage:** All major sectors represented
- **Skill Distribution:** Full range from manual to professional occupations

### Potential Selection Bias

**Who is Underrepresented:**
- Emerging occupations (e.g., "AI Ethicist", "Prompt Engineer")
- State-specific government roles
- Very small occupations (<1,000 workers nationally)

**Who is Overrepresented:**
- Large, established occupations
- Private sector roles (vs. niche public sector)
- Traditional professions with long histories

**Bias Assessment for Causal Inference:**
- ✅ Pre-treatment characteristics balanced (occupation FE absorbs time-invariant traits)
- ✅ Parallel trends assumption testable (8 years pre-period: 2015-2022)
- ✅ Treatment assignment exogenous (ChatGPT release not based on US employment data)
- ⚠️ External validity: Results may not generalize to emerging/niche occupations

---

## Correlation Structure

### Exposure Variable Correlations

|  | AI_Exposure | Teleworkability | AutomationRisk_PreAI |
|--|-------------|-----------------|---------------------|
| **AI_Exposure** | 1.00 | 0.62 | -0.35 |
| **Teleworkability** | 0.62 | 1.00 | -0.54 |
| **AutomationRisk_PreAI** | -0.35 | -0.54 | 1.00 |

**Interpretation:**

1. **AI ↔ Telework (r=0.62):** 
   - Both measure cognitive work amenable to digital tools
   - Occupations with high AI exposure tend to be office-based

2. **AI ↔ Automation (r=-0.35):**
   - Traditional automation targets routine manual work
   - GenAI targets non-routine cognitive work
   - Different types of labor substitution

3. **Telework ↔ Automation (r=-0.54):**
   - High automation risk = manual/physical jobs (low telework)
   - Low automation risk = cognitive jobs (high telework)
   - Strong negative relationship

**Implication for Analysis:** 
- Multicollinearity is moderate but not prohibitive (VIF < 2.0)
- Can include all three as controls or heterogeneity dimensions
- Consider interaction effects (e.g., AI × Telework)

---

## Fixed Effects Strategy

For a Difference-in-Differences regression with occupation-level panel data:

### Basic Specification

```
log(Employment_osiy) = β₁(Treat_ot) + α_o + γ_t + δ_s + θ_i + ε_osiy
```

Where:
- `o` = occupation
- `s` = state
- `i` = industry
- `y` = year
- `α_o` = Occupation fixed effects (absorbs time-invariant occupation traits)
- `γ_t` = Year fixed effects (absorbs economy-wide shocks)
- `δ_s` = State fixed effects (absorbs state-specific factors)
- `θ_i` = Industry fixed effects (absorbs industry trends)
- `β₁` = **Causal effect of GenAI on employment in high-exposure occupations**

### R Implementation (fixest package)

```r
library(fixest)

# Model 1: Basic DiD with Occupation and Year FE
model1 <- feols(LogEmployment ~ Treat | Occupation + Year,
                data = df, cluster = ~Occupation)

# Model 2: Add State FE
model2 <- feols(LogEmployment ~ Treat | Occupation + Year + State,
                data = df, cluster = ~Occupation)

# Model 3: Add Industry FE (preferred specification)
model3 <- feols(LogEmployment ~ Treat | Occupation + Year + State + Industry,
                data = df, cluster = ~Occupation)

# Compare models
etable(model1, model2, model3, 
       title = "Effect of AI Exposure on Occupation Employment")
```

### Python Implementation (linearmodels package)

```python
from linearmodels.panel import PanelOLS

# Set multi-index
df_panel = df.set_index(['Occupation', 'Year'])

# Model with entity and time effects
model = PanelOLS.from_formula('LogEmployment ~ Treat + EntityEffects + TimeEffects',
                               data=df_panel)
results = model.fit(cov_type='clustered', cluster_entity=True)
```

### Alternative: Continuous Treatment Intensity

Instead of binary HighExposure, use AI_Exposure_Score as continuous:

```r
# Continuous treatment with interaction
model_continuous <- feols(
  LogEmployment ~ AI_Exposure_Score:Post | Occupation + Year + State + Industry,
  data = df, cluster = ~Occupation
)
```

This captures **heterogeneous effects** by exposure intensity rather than comparing high vs. low groups.

---

## Heterogeneity Analysis

### By Teleworkability

```r
# Create terciles
df$TeleworkGroup <- cut(df$Teleworkability, 
                        breaks = c(0, 0.33, 0.67, 1.0),
                        labels = c("Low", "Medium", "High"))

# Interaction model
feols(LogEmployment ~ Treat:TeleworkGroup | Occupation + Year + State + Industry,
      data = df, cluster = ~Occupation)
```

**Research Question:** Does AI impact differ for teleworkable vs. in-person occupations?

### By Automation Risk

```r
# Create terciles
df$AutoGroup <- cut(df$AutomationRisk_PreAI,
                    breaks = c(0, 0.33, 0.67, 1.0),
                    labels = c("Low", "Medium", "High"))

# Interaction model
feols(LogEmployment ~ Treat:AutoGroup | Occupation + Year + State + Industry,
      data = df, cluster = ~Occupation)
```

**Research Question:** Does AI impact differ for jobs already at risk of traditional automation?

### Triple Interaction

```r
# AI × Telework × Automation
feols(LogEmployment ~ Treat:TeleworkGroup:AutoGroup | Occupation + Year + State + Industry,
      data = df, cluster = ~Occupation)
```

**Research Question:** Which combinations of characteristics face largest AI effects?

---

## Event Study Analysis

Test parallel trends assumption and examine dynamic effects:

```r
# Create event time variable
df$EventTime <- df$Year - 2023
df$EventTime_factor <- factor(df$EventTime)

# Event study regression (omit t=-1 as reference)
event_study <- feols(
  LogEmployment ~ i(EventTime, HighAIExposure, ref = -1) | 
    Occupation + Year + State + Industry,
  data = df,
  cluster = ~Occupation
)

# Visualize
iplot(event_study, 
      main = "Event Study: AI Exposure Effect on Employment",
      xlab = "Years Relative to ChatGPT Release",
      ylab = "Effect on Log Employment")
```

**Expected Pattern:**
- Pre-2023: Coefficients should be close to 0 and statistically insignificant (parallel trends)
- 2023-2024: Positive or negative coefficients indicate treatment effect
- Can test for pre-trends: `coeftest(event_study, vcov = cluster)` on pre-period

---

## Robustness Checks

### 1. Alternative Treatment Definitions

```r
# 75th percentile threshold
AI_p75 <- quantile(df$AI_Exposure_Score, 0.75)
df$HighAI_p75 <- as.integer(df$AI_Exposure_Score >= AI_p75)
df$Treat_p75 <- df$HighAI_p75 * df$Post

# 50th percentile threshold
AI_p50 <- quantile(df$AI_Exposure_Score, 0.50)
df$HighAI_p50 <- as.integer(df$AI_Exposure_Score >= AI_p50)
df$Treat_p50 <- df$HighAI_p50 * df$Post
```

### 2. Alternative Standard Error Clustering

```r
# Two-way clustering (occupation × year)
model_twoway <- feols(LogEmployment ~ Treat | Occupation + Year + State + Industry,
                      data = df, cluster = ~Occupation + Year)

# State-level clustering
model_state <- feols(LogEmployment ~ Treat | Occupation + Year + State + Industry,
                     data = df, cluster = ~State)
```

### 3. Exclude Small Occupations

```r
# Minimum employment threshold
df_large <- df %>%
  group_by(Occupation) %>%
  filter(mean(Employment) >= 1000) %>%
  ungroup()
```

### 4. Weighted Regression

```r
# Weight by occupation size
feols(LogEmployment ~ Treat | Occupation + Year + State + Industry,
      data = df, weights = ~Employment, cluster = ~Occupation)
```

---

## Data Sources Summary

| Variable | Source | Year | Journal/Publisher | DOI |
|----------|--------|------|-------------------|-----|
| **AI_Exposure_Score** | Gmyrek et al. | 2025 | ILO Working Paper 140 | https://doi.org/10.54394/YGKR1846 |
| **Teleworkability** | Dingel & Neiman | 2020 | Journal of Public Economics | https://doi.org/10.1016/j.jpubeco.2020.104235 |
| **AutomationRisk_PreAI** | Frey & Osborne | 2017 | Tech. Forecasting & Social Change | https://doi.org/10.1016/j.techfore.2016.08.019 |
| **Employment Data** | BLS OEWS | 2015-2024 | Occupational Employment & Wage Statistics | https://www.bls.gov/oes/ |

---

## References

1. **Gmyrek, P., Berg, J., & Bescond, D. (2025).** *Generative AI and jobs: A global analysis of potential effects on job quantity and quality.* ILO Working Paper 140. Geneva: International Labour Office. https://doi.org/10.54394/YGKR1846

2. **Dingel, J. I., & Neiman, B. (2020).** *How many jobs can be done at home?* Journal of Public Economics, 189, 104235. https://doi.org/10.1016/j.jpubeco.2020.104235

3. **Frey, C. B., & Osborne, M. A. (2017).** *The future of employment: How susceptible are jobs to computerisation?* Technological Forecasting and Social Change, 114, 254-280. https://doi.org/10.1016/j.techfore.2016.08.019

4. **Autor, D. H., & Dorn, D. (2013).** *The growth of low-skill service jobs and the polarization of the US labor market.* American Economic Review, 103(5), 1553-97.

5. **Bureau of Labor Statistics (BLS).** *Occupational Employment and Wage Statistics (OEWS).* U.S. Department of Labor. https://www.bls.gov/oes/

---

## Contact

For questions about data sources, methodology, or access to underlying files:
- ILO Working Paper: contact authors or ILO Research Department
- Dingel-Neiman data: https://github.com/jdingel/DingelNeiman-workathome
- Frey-Osborne data: Available in paper appendix or contact authors
- BLS OEWS: https://www.bls.gov/oes/tables.htm
