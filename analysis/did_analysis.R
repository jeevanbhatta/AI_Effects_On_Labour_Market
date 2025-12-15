# =============================================================================
# SS154 Final Project: Difference-in-Differences Analysis
# Effect of Generative AI Availability on Employment
# =============================================================================

# Clear environment
rm(list = ls())

# -----------------------------------------------------------------------------
# 1. Setup and Load Packages
# -----------------------------------------------------------------------------

# Install packages if needed
packages <- c("tidyverse", "fixest", "modelsummary", "kableExtra", 
              "ggplot2", "scales", "stargazer", "broom", "sandwich", "lmtest")

install_if_missing <- function(pkg) {
  if (!require(pkg, character.only = TRUE)) {
    install.packages(pkg)
    library(pkg, character.only = TRUE)
  }
}

lapply(packages, install_if_missing)

# Set working directory to project root
project_root <- "/Users/jeevanbhatta/Minerva/SS154/AI_Effects_On_Labour_Market"
setwd(project_root)

# Create output directories
dir.create("paper/figures", showWarnings = FALSE, recursive = TRUE)
dir.create("paper/tables", showWarnings = FALSE, recursive = TRUE)

# Set ggplot theme
theme_set(theme_minimal(base_size = 12) +
            theme(
              plot.title = element_text(face = "bold", hjust = 0.5),
              legend.position = "bottom",
              panel.grid.minor = element_blank()
            ))

# -----------------------------------------------------------------------------
# 2. Load and Prepare Data
# -----------------------------------------------------------------------------

# Load the analysis panel
df <- read.csv("data/analysis_panel.csv")

# Convert Date to proper format
df$Date <- as.Date(df$Date)

# Create additional variables
df <- df %>%
  mutate(
    # Year-Month factor for time fixed effects
    YearMonth_factor = factor(YearMonth),
    # Industry factor
    Industry_factor = factor(Industry),
    # State factor
    State_factor = factor(State),
    # Relative time to treatment (ChatGPT release = Nov 2022)
    RelativeTime = (Year - 2022) * 12 + (Month - 11),
    # Event study bins (cap at -24 and +24)
    EventTime = pmax(pmin(RelativeTime, 24), -24),
    EventTime_factor = factor(EventTime)
  )

# Filter to exclude Total Nonfarm for main analysis
df_analysis <- df %>% 
  filter(Industry != "Total Nonfarm")

cat("Data loaded successfully!\n")
cat(sprintf("Total observations: %d\n", nrow(df_analysis)))
cat(sprintf("Industries: %d\n", n_distinct(df_analysis$Industry)))
cat(sprintf("States: %d\n", n_distinct(df_analysis$State)))
cat(sprintf("Time period: %s to %s\n", min(df_analysis$Date), max(df_analysis$Date)))

# -----------------------------------------------------------------------------
# 3. Summary Statistics Table
# -----------------------------------------------------------------------------

# Calculate summary statistics
summary_stats <- df_analysis %>%
  summarise(
    `Employment (thousands)` = list(c(
      mean = mean(Employment, na.rm = TRUE),
      sd = sd(Employment, na.rm = TRUE),
      min = min(Employment, na.rm = TRUE),
      max = max(Employment, na.rm = TRUE),
      n = n()
    )),
    `Log Employment` = list(c(
      mean = mean(LogEmployment, na.rm = TRUE),
      sd = sd(LogEmployment, na.rm = TRUE),
      min = min(LogEmployment, na.rm = TRUE),
      max = max(LogEmployment, na.rm = TRUE),
      n = n()
    )),
    `Post (=1 if >= 2023)` = list(c(
      mean = mean(Post, na.rm = TRUE),
      sd = sd(Post, na.rm = TRUE),
      min = min(Post, na.rm = TRUE),
      max = max(Post, na.rm = TRUE),
      n = n()
    )),
    `High Exposure` = list(c(
      mean = mean(HighExposure, na.rm = TRUE),
      sd = sd(HighExposure, na.rm = TRUE),
      min = min(HighExposure, na.rm = TRUE),
      max = max(HighExposure, na.rm = TRUE),
      n = n()
    )),
    `Treatment (Post × High Exposure)` = list(c(
      mean = mean(Treat, na.rm = TRUE),
      sd = sd(Treat, na.rm = TRUE),
      min = min(Treat, na.rm = TRUE),
      max = max(Treat, na.rm = TRUE),
      n = n()
    )),
    `AI Exposure Score` = list(c(
      mean = mean(AI_Exposure_Score, na.rm = TRUE),
      sd = sd(AI_Exposure_Score, na.rm = TRUE),
      min = min(AI_Exposure_Score, na.rm = TRUE),
      max = max(AI_Exposure_Score, na.rm = TRUE),
      n = n()
    ))
  )

# Create summary statistics by treatment group
summary_by_group <- df_analysis %>%
  group_by(HighExposure) %>%
  summarise(
    N = n(),
    `Mean Employment` = mean(Employment),
    `SD Employment` = sd(Employment),
    `Mean Log Employment` = mean(LogEmployment),
    `SD Log Employment` = sd(LogEmployment),
    .groups = "drop"
  )

cat("\nSummary Statistics by Treatment Group:\n")
print(summary_by_group)

# -----------------------------------------------------------------------------
# 4. Main DiD Regressions
# -----------------------------------------------------------------------------

cat("\n" , rep("=", 60), "\n")
cat("MAIN DIFFERENCE-IN-DIFFERENCES RESULTS\n")
cat(rep("=", 60), "\n\n")

# Model 1: Basic DiD with Industry and Time FE
model1 <- feols(LogEmployment ~ Treat | Industry_factor + YearMonth_factor, 
                data = df_analysis,
                cluster = ~State_factor + Industry_factor)

# Model 2: Add State FE
model2 <- feols(LogEmployment ~ Treat | Industry_factor + YearMonth_factor + State_factor,
                data = df_analysis,
                cluster = ~State_factor + Industry_factor)

# Model 3: State-Time FE (more demanding)
model3 <- feols(LogEmployment ~ Treat | Industry_factor + State_factor^YearMonth_factor,
                data = df_analysis,
                cluster = ~State_factor + Industry_factor)

# Model 4: Continuous treatment (AI Score × Post)
model4 <- feols(LogEmployment ~ AI_Exposure_Score:Post | Industry_factor + YearMonth_factor + State_factor,
                data = df_analysis,
                cluster = ~State_factor + Industry_factor)

# Display results
cat("Model 1: Basic DiD (Industry + Time FE)\n")
print(summary(model1))

cat("\nModel 2: DiD with State FE\n")
print(summary(model2))

cat("\nModel 3: DiD with State×Time FE\n")
print(summary(model3))

cat("\nModel 4: Continuous Treatment (AI Score × Post)\n")
print(summary(model4))

# -----------------------------------------------------------------------------
# 5. Create Regression Table for LaTeX
# -----------------------------------------------------------------------------

# Using modelsummary for nice tables
models <- list(
  "Basic DiD" = model1,
  "+ State FE" = model2,
  "+ State×Time FE" = model3,
  "Continuous" = model4
)

# Create LaTeX table
modelsummary(
  models,
  output = "paper/tables/main_results.tex",
  stars = c('*' = .1, '**' = .05, '***' = .01),
  coef_map = c(
    "Treat" = "Treat (Post × High Exposure)",
    "AI_Exposure_Score:Post" = "AI Score × Post"
  ),
  gof_map = c("nobs", "r.squared", "adj.r.squared"),
  title = "Difference-in-Differences Estimates: Effect of AI Availability on Employment",
  notes = c(
    "Notes: Dependent variable is log employment.",
    "Standard errors clustered at state-industry level in parentheses.",
    "* p < 0.10, ** p < 0.05, *** p < 0.01"
  )
)

cat("\nRegression table saved to: paper/tables/main_results.tex\n")

# Also create HTML version for easy viewing
modelsummary(
  models,
  output = "paper/tables/main_results.html",
  stars = c('*' = .1, '**' = .05, '***' = .01),
  coef_map = c(
    "Treat" = "Treat (Post × High Exposure)",
    "AI_Exposure_Score:Post" = "AI Score × Post"
  ),
  gof_map = c("nobs", "r.squared", "adj.r.squared"),
  title = "Difference-in-Differences Estimates: Effect of AI Availability on Employment"
)

# -----------------------------------------------------------------------------
# 6. Event Study Analysis
# -----------------------------------------------------------------------------

cat("\n" , rep("=", 60), "\n")
cat("EVENT STUDY ANALYSIS\n")
cat(rep("=", 60), "\n\n")

# Create event study variables
# Reference period: November 2022 (EventTime = 0)
df_analysis <- df_analysis %>%
  mutate(
    # Create separate dummies for each event time
    EventTime_clean = ifelse(RelativeTime < -24, -24, 
                              ifelse(RelativeTime > 24, 24, RelativeTime))
  )

# Event study regression
event_study <- feols(
  LogEmployment ~ i(EventTime_clean, HighExposure, ref = -1) | 
    Industry_factor + YearMonth_factor + State_factor,
  data = df_analysis,
  cluster = ~State_factor + Industry_factor
)

cat("Event Study Results:\n")
print(summary(event_study))

# Extract coefficients for plotting
es_coefs <- broom::tidy(event_study, conf.int = TRUE) %>%
  filter(str_detect(term, "EventTime")) %>%
  mutate(
    EventTime = as.numeric(str_extract(term, "-?\\d+")),
    # Add reference period
  ) %>%
  bind_rows(data.frame(EventTime = -1, estimate = 0, conf.low = 0, conf.high = 0)) %>%
  arrange(EventTime)

# Create event study plot
p_event_study <- ggplot(es_coefs, aes(x = EventTime, y = estimate)) +
  geom_hline(yintercept = 0, linetype = "dashed", color = "gray50") +
  geom_vline(xintercept = -0.5, linetype = "dashed", color = "red", linewidth = 1) +
  geom_ribbon(aes(ymin = conf.low, ymax = conf.high), alpha = 0.2, fill = "#2E86AB") +
  geom_line(color = "#2E86AB", linewidth = 1) +
  geom_point(color = "#2E86AB", size = 2) +
  annotate("text", x = -12, y = max(es_coefs$conf.high, na.rm = TRUE) * 0.9, 
           label = "Pre-Treatment", fontface = "italic", size = 4) +
  annotate("text", x = 12, y = max(es_coefs$conf.high, na.rm = TRUE) * 0.9, 
           label = "Post-Treatment", fontface = "italic", size = 4) +
  labs(
    x = "Months Relative to ChatGPT Release (Nov 2022)",
    y = "Effect on Log Employment",
    title = "Event Study: Dynamic Effects of AI Availability on Employment",
    caption = "Notes: Reference period is October 2022 (t = -1). Shaded area shows 95% CI.\nStandard errors clustered at state-industry level."
  ) +
  scale_x_continuous(breaks = seq(-24, 24, 6)) +
  theme(
    plot.caption = element_text(hjust = 0, size = 9)
  )

ggsave("paper/figures/event_study.pdf", p_event_study, width = 10, height = 6, dpi = 300)
ggsave("paper/figures/event_study.png", p_event_study, width = 10, height = 6, dpi = 300)

cat("\nEvent study figure saved to: paper/figures/event_study.pdf\n")

# -----------------------------------------------------------------------------
# 7. Robustness Checks
# -----------------------------------------------------------------------------

cat("\n" , rep("=", 60), "\n")
cat("ROBUSTNESS CHECKS\n")
cat(rep("=", 60), "\n\n")

# Robustness 1: Exclude COVID period (March 2020 - December 2021)
df_no_covid <- df_analysis %>%
  filter(!(Date >= "2020-03-01" & Date <= "2021-12-31"))

robust1 <- feols(LogEmployment ~ Treat | Industry_factor + YearMonth_factor + State_factor,
                 data = df_no_covid,
                 cluster = ~State_factor + Industry_factor)

cat("Robustness 1: Excluding COVID Period (Mar 2020 - Dec 2021)\n")
print(summary(robust1))

# Robustness 2: Alternative treatment date (January 2023)
df_analysis <- df_analysis %>%
  mutate(
    Post_alt = ifelse(Year >= 2023, 1, 0),
    Treat_alt = Post_alt * HighExposure
  )

robust2 <- feols(LogEmployment ~ Treat_alt | Industry_factor + YearMonth_factor + State_factor,
                 data = df_analysis,
                 cluster = ~State_factor + Industry_factor)

cat("\nRobustness 2: Alternative Treatment Date (Jan 2023)\n")
print(summary(robust2))

# Robustness 3: Placebo test (fake treatment in 2019)
df_analysis <- df_analysis %>%
  mutate(
    Post_placebo = ifelse(Year >= 2019, 1, 0),
    Treat_placebo = Post_placebo * HighExposure
  )

df_pre_treatment <- df_analysis %>%
  filter(Date < "2022-11-01")

robust3 <- feols(LogEmployment ~ Treat_placebo | Industry_factor + YearMonth_factor + State_factor,
                 data = df_pre_treatment,
                 cluster = ~State_factor + Industry_factor)

cat("\nRobustness 3: Placebo Test (Fake Treatment in Jan 2019)\n")
print(summary(robust3))

# Robustness 4: National level only
df_national <- df_analysis %>%
  filter(State == "Total")

robust4 <- feols(LogEmployment ~ Treat | Industry_factor + YearMonth_factor,
                 data = df_national,
                 cluster = ~Industry_factor)

cat("\nRobustness 4: National Level Only\n")
print(summary(robust4))

# Create robustness table
robustness_models <- list(
  "Excl. COVID" = robust1,
  "Alt. Date" = robust2,
  "Placebo 2019" = robust3,
  "National Only" = robust4
)

modelsummary(
  robustness_models,
  output = "paper/tables/robustness.tex",
  stars = c('*' = .1, '**' = .05, '***' = .01),
  coef_map = c(
    "Treat" = "Treat",
    "Treat_alt" = "Treat (Alt. Date)",
    "Treat_placebo" = "Treat (Placebo)"
  ),
  gof_map = c("nobs", "r.squared"),
  title = "Robustness Checks",
  notes = c(
    "Notes: Dependent variable is log employment.",
    "All models include industry and time fixed effects.",
    "* p < 0.10, ** p < 0.05, *** p < 0.01"
  )
)

cat("\nRobustness table saved to: paper/tables/robustness.tex\n")

# -----------------------------------------------------------------------------
# 8. Statistical and Practical Significance
# -----------------------------------------------------------------------------

cat("\n" , rep("=", 60), "\n")
cat("STATISTICAL AND PRACTICAL SIGNIFICANCE\n")
cat(rep("=", 60), "\n\n")

# Get main coefficient from preferred specification (Model 2)
main_coef <- coef(model2)["Treat"]
main_se <- sqrt(vcov(model2)["Treat", "Treat"])
main_pvalue <- 2 * (1 - pnorm(abs(main_coef / main_se)))

cat(sprintf("Main Treatment Effect (Preferred Specification - Model 2):\n"))
cat(sprintf("  Coefficient: %.4f\n", main_coef))
cat(sprintf("  Standard Error: %.4f\n", main_se))
cat(sprintf("  t-statistic: %.3f\n", main_coef / main_se))
cat(sprintf("  p-value: %.4f\n", main_pvalue))
cat(sprintf("  95%% CI: [%.4f, %.4f]\n", main_coef - 1.96*main_se, main_coef + 1.96*main_se))

# Interpretation
cat(sprintf("\nInterpretation:\n"))
cat(sprintf("  The coefficient of %.4f indicates that following ChatGPT's release,\n", main_coef))
cat(sprintf("  employment in high AI-exposure industries changed by approximately\n"))
cat(sprintf("  %.2f%% relative to low AI-exposure industries.\n", main_coef * 100))

# Cohen's d calculation
pooled_sd <- sd(df_analysis$LogEmployment)
cohens_d <- main_coef / pooled_sd

cat(sprintf("\nEffect Size (Cohen's d): %.3f\n", cohens_d))
if (abs(cohens_d) < 0.2) {
  cat("  Interpretation: Small effect size\n")
} else if (abs(cohens_d) < 0.5) {
  cat("  Interpretation: Small to medium effect size\n")
} else if (abs(cohens_d) < 0.8) {
  cat("  Interpretation: Medium effect size\n")
} else {
  cat("  Interpretation: Large effect size\n")
}

# Convert to jobs
avg_employment_high <- df_analysis %>%
  filter(HighExposure == 1) %>%
  summarise(mean_emp = mean(Employment)) %>%
  pull(mean_emp)

jobs_effect <- avg_employment_high * main_coef * 1000  # Convert from thousands

cat(sprintf("\nSubstantive Effect:\n"))
cat(sprintf("  Average employment in high-exposure industries: %.0f thousand\n", avg_employment_high))
cat(sprintf("  Implied job change: approximately %.0f jobs\n", jobs_effect))

# -----------------------------------------------------------------------------
# 9. Summary Statistics Table for LaTeX
# -----------------------------------------------------------------------------

# Create a proper summary statistics table
summary_table <- df_analysis %>%
  summarise(
    across(
      c(Employment, LogEmployment, Post, HighExposure, Treat, 
        AI_Exposure_Score, Teleworkability, RoutineTaskIndex, 
        SkillIntensity, AutomationRisk_PreAI),
      list(
        mean = ~mean(., na.rm = TRUE),
        sd = ~sd(., na.rm = TRUE),
        min = ~min(., na.rm = TRUE),
        max = ~max(., na.rm = TRUE)
      ),
      .names = "{.col}_{.fn}"
    ),
    N = n()
  )

# Format and save
cat("\nSummary statistics table created.\n")

# -----------------------------------------------------------------------------
# 10. Create Parallel Trends Plot in R
# -----------------------------------------------------------------------------

# Aggregate data for plotting
parallel_trends_data <- df_analysis %>%
  group_by(Date, HighExposure) %>%
  summarise(Employment = sum(Employment), .groups = "drop") %>%
  group_by(HighExposure) %>%
  mutate(
    BaselineEmp = Employment[Date == min(Date)],
    NormalizedEmp = (Employment / BaselineEmp) * 100
  ) %>%
  ungroup()

p_parallel <- ggplot(parallel_trends_data, 
                     aes(x = Date, y = NormalizedEmp, 
                         color = factor(HighExposure), 
                         linetype = factor(HighExposure))) +
  geom_line(linewidth = 1.2) +
  geom_vline(xintercept = as.Date("2022-11-30"), linetype = "dashed", 
             color = "black", linewidth = 1) +
  annotate("rect", xmin = min(parallel_trends_data$Date), 
           xmax = as.Date("2022-11-30"),
           ymin = -Inf, ymax = Inf, alpha = 0.1, fill = "green") +
  annotate("rect", xmin = as.Date("2022-11-30"), 
           xmax = max(parallel_trends_data$Date),
           ymin = -Inf, ymax = Inf, alpha = 0.1, fill = "red") +
  scale_color_manual(
    values = c("0" = "#E94F37", "1" = "#2E86AB"),
    labels = c("Low AI Exposure (Control)", "High AI Exposure (Treatment)")
  ) +
  scale_linetype_manual(
    values = c("0" = "dashed", "1" = "solid"),
    labels = c("Low AI Exposure (Control)", "High AI Exposure (Treatment)")
  ) +
  labs(
    x = "Date",
    y = "Employment Index (Jan 2015 = 100)",
    title = "Parallel Trends: High vs Low AI Exposure Industries",
    color = "Group",
    linetype = "Group",
    caption = "Notes: Vertical dashed line marks ChatGPT release (Nov 2022)."
  ) +
  theme(
    legend.position = "bottom",
    plot.caption = element_text(hjust = 0)
  )

ggsave("paper/figures/parallel_trends_R.pdf", p_parallel, width = 12, height = 7, dpi = 300)
ggsave("paper/figures/parallel_trends_R.png", p_parallel, width = 12, height = 7, dpi = 300)

cat("\nParallel trends plot saved to: paper/figures/parallel_trends_R.pdf\n")

# -----------------------------------------------------------------------------
# 11. Final Output Summary
# -----------------------------------------------------------------------------

cat("\n", rep("=", 60), "\n")
cat("ANALYSIS COMPLETE!\n")
cat(rep("=", 60), "\n\n")

cat("Output files created:\n")
cat("  Tables:\n")
cat("    - paper/tables/main_results.tex\n")
cat("    - paper/tables/main_results.html\n")
cat("    - paper/tables/robustness.tex\n")
cat("  Figures:\n")
cat("    - paper/figures/event_study.pdf\n")
cat("    - paper/figures/parallel_trends_R.pdf\n")

cat("\n\nKey Results Summary:\n")
cat(sprintf("  Main DiD Effect: %.4f (%.2f%%)\n", main_coef, main_coef * 100))
cat(sprintf("  Statistical Significance: p = %.4f\n", main_pvalue))
cat(sprintf("  Cohen's d: %.3f\n", cohens_d))
cat(sprintf("  Observations: %d\n", nrow(df_analysis)))
