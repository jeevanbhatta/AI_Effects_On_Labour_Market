# =============================================================================
# SS154 Final Project: Difference-in-Differences Analysis
# Effect of Generative AI Availability on Employment
# Using Complete Occupation Panel Data
# =============================================================================

# Clear environment
rm(list = ls())

# -----------------------------------------------------------------------------
# 1. Setup and Load Packages
# -----------------------------------------------------------------------------

packages <- c("tidyverse", "fixest", "modelsummary", "kableExtra")

install_if_missing <- function(pkg) {
  if (!require(pkg, character.only = TRUE)) {
    install.packages(pkg, dependencies = TRUE)
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
theme_set(theme_minimal(base_size = 12))

# -----------------------------------------------------------------------------
# 2. Load and Prepare Data
# -----------------------------------------------------------------------------

# Load the complete occupation panel (only rows with complete data)
df <- read.csv("data/occupation_panel_complete.csv")

cat("="*80, "\n")
cat("OCCUPATION PANEL DATA LOADED\n")
cat("="*80, "\n\n")
cat(sprintf("Total observations: %d\n", nrow(df)))
cat(sprintf("Unique occupations: %d\n", n_distinct(df$Occupation)))
cat(sprintf("Unique states: %d\n", n_distinct(df$State)))
cat(sprintf("Unique industries: %d\n", n_distinct(df$Industry)))
cat(sprintf("Years: %d to %d\n", min(df$Year), max(df$Year)))
cat("\nNote: Complete dataset = 42.93% of original (3,051,972 of 7,108,826 rows)\n")
cat("Contains only rows with complete AI_Exposure_Score, Teleworkability, AutomationRisk_PreAI\n\n")

# Create analysis variables
df <- df %>%
  mutate(
    # Factor variables for fixed effects
    Industry_factor = factor(Industry),
    State_factor = factor(State),
    Year_factor = factor(Year),
    Occupation_factor = factor(Occupation),
    
    # Treatment: High AI exposure (top 33%) × Post period (2023+)
    AI_threshold = quantile(AI_Exposure_Score, 0.67, na.rm=TRUE),
    HighAIExposure = as.integer(AI_Exposure_Score >= AI_threshold),
    Treat = HighAIExposure * Post,
    
    # Event study: Years relative to 2023
    EventTime = Year - 2023,
    EventTime_factor = factor(EventTime)
  )

# Summary of treatment groups
cat("Treatment Group Definition:\n")
cat(sprintf("  AI Exposure threshold (67th percentile): %.3f\n", 
            unique(df$AI_threshold)))
cat(sprintf("  High exposure observations: %d (%.1f%%)\n", 
            sum(df$HighAIExposure), mean(df$HighAIExposure)*100))
cat(sprintf("  Low exposure observations: %d (%.1f%%)\n\n",
            sum(1-df$HighAIExposure), mean(1-df$HighAIExposure)*100))

# -----------------------------------------------------------------------------
# 3. Summary Statistics
# -----------------------------------------------------------------------------

cat("="*80, "\n")
cat("SUMMARY STATISTICS\n")
cat("="*80, "\n\n")

# Overall summary
summary_stats <- df %>%
  summarise(
    N = n(),
    Mean_Employment = mean(Employment, na.rm=TRUE),
    SD_Employment = sd(Employment, na.rm=TRUE),
    Mean_LogEmp = mean(LogEmployment, na.rm=TRUE),
    SD_LogEmp = sd(LogEmployment, na.rm=TRUE),
    Mean_AI_Score = mean(AI_Exposure_Score, na.rm=TRUE),
    SD_AI_Score = sd(AI_Exposure_Score, na.rm=TRUE),
    Mean_Telework = mean(Teleworkability, na.rm=TRUE),
    Mean_AutoRisk = mean(AutomationRisk_PreAI, na.rm=TRUE)
  )

print(summary_stats)

# Summary by treatment group
summary_by_group <- df %>%
  group_by(HighAIExposure, Post) %>%
  summarise(
    N = n(),
    Mean_Employment = mean(Employment, na.rm=TRUE),
    Mean_LogEmp = mean(LogEmployment, na.rm=TRUE),
    .groups = "drop"
  ) %>%
  mutate(
    Group = ifelse(HighAIExposure == 1, "High AI Exposure", "Low AI Exposure"),
    Period = ifelse(Post == 1, "Post (2023-2024)", "Pre (2015-2022)")
  )

cat("\nSummary by Treatment Group and Period:\n")
print(summary_by_group)

# -----------------------------------------------------------------------------
# 4. Main DiD Regressions
# -----------------------------------------------------------------------------

cat("\n", rep("=", 80), "\n")
cat("MAIN DIFFERENCE-IN-DIFFERENCES RESULTS\n")
cat(rep("=", 80), "\n\n")

# Model 1: Basic DiD with Occupation and Year FE
model1 <- feols(LogEmployment ~ Treat | Occupation_factor + Year_factor, 
                data = df,
                cluster = ~Occupation)

# Model 2: Add State FE
model2 <- feols(LogEmployment ~ Treat | Occupation_factor + Year_factor + State_factor,
                data = df,
                cluster = ~Occupation)

# Model 3: Add Industry FE (full specification)
model3 <- feols(LogEmployment ~ Treat | Occupation_factor + Year_factor + State_factor + Industry_factor,
                data = df,
                cluster = ~Occupation)

# Model 4: Continuous treatment (AI Score × Post)
model4 <- feols(LogEmployment ~ AI_Exposure_Score:Post | Occupation_factor + Year_factor + State_factor + Industry_factor,
                data = df,
                cluster = ~Occupation)

# Display results
cat("Model 1: Basic DiD (Occupation + Year FE)\n")
print(summary(model1))

cat("\nModel 2: Add State FE\n")
print(summary(model2))

cat("\nModel 3: Full Specification (+ Industry FE)\n")
print(summary(model3))

cat("\nModel 4: Continuous Treatment (AI Score × Post)\n")
print(summary(model4))

# -----------------------------------------------------------------------------
# 5. Create Regression Table
# -----------------------------------------------------------------------------

models <- list(
  "(1) Basic" = model1,
  "(2) + State FE" = model2,
  "(3) + Industry FE" = model3,
  "(4) Continuous" = model4
)

# LaTeX table
modelsummary(
  models,
  output = "paper/tables/main_results_complete.tex",
  title = "Effect of AI Exposure on Employment (Complete Data)",
  stars = c('*' = 0.10, '**' = 0.05, '***' = 0.01),
  gof_map = c("nobs", "r.squared", "adj.r.squared", "FE: Occupation_factor", 
              "FE: Year_factor", "FE: State_factor", "FE: Industry_factor"),
  coef_rename = c("Treat" = "High AI Exposure × Post",
                  "AI_Exposure_Score:Post" = "AI Exposure Score × Post"),
  notes = "Standard errors clustered at occupation level."
)

cat("\n✓ Regression table saved to: paper/tables/main_results_complete.tex\n")

# -----------------------------------------------------------------------------
# 6. Event Study Analysis
# -----------------------------------------------------------------------------

cat("\n", rep("=", 80), "\n")
cat("EVENT STUDY ANALYSIS\n")
cat(rep("=", 80), "\n\n")

# Event study regression (omit -1 as reference)
event_study <- feols(
  LogEmployment ~ i(EventTime, HighAIExposure, ref = -1) | 
    Occupation_factor + Year_factor + State_factor + Industry_factor,
  data = df,
  cluster = ~Occupation
)

cat("Event Study Results:\n")
print(summary(event_study))

# Extract coefficients for plotting
es_coefs <- broom::tidy(event_study, conf.int = TRUE) %>%
  filter(grepl("EventTime", term)) %>%
  mutate(
    EventTime = as.numeric(gsub(".*EventTime::(.*?)::.*", "\\1", term)),
    EventTime = ifelse(is.na(EventTime), -1, EventTime)  # Reference period
  )

# Add reference period (coefficient = 0)
es_coefs <- bind_rows(
  es_coefs,
  data.frame(EventTime = -1, estimate = 0, std.error = 0, 
             conf.low = 0, conf.high = 0)
) %>%
  arrange(EventTime)

# Event study plot
p_event_study <- ggplot(es_coefs, aes(x = EventTime, y = estimate)) +
  geom_point(size = 3, color = "#2E86AB") +
  geom_errorbar(aes(ymin = conf.low, ymax = conf.high), width = 0.2, color = "#2E86AB") +
  geom_hline(yintercept = 0, linetype = "dashed", color = "red") +
  geom_vline(xintercept = -0.5, linestyle = "dashed", color = "gray", alpha = 0.5) +
  labs(
    title = "Event Study: Effect of AI Exposure on Employment",
    subtitle = "Years Relative to ChatGPT Release (2023)",
    x = "Years Relative to Treatment",
    y = "Effect on Log Employment",
    caption = "Note: 95% confidence intervals. Clustered SEs at occupation level."
  ) +
  theme_minimal() +
  theme(plot.title = element_text(face = "bold"))

ggsave("paper/figures/event_study_complete.pdf", p_event_study, width = 10, height = 6, dpi = 300)
ggsave("paper/figures/event_study_complete.png", p_event_study, width = 10, height = 6, dpi = 300)

cat("\n✓ Event study figure saved to: paper/figures/event_study_complete.pdf\n")

# -----------------------------------------------------------------------------
# 7. Parallel Trends Visualization
# -----------------------------------------------------------------------------

# Calculate group means by year
parallel_trends_data <- df %>%
  group_by(Year, HighAIExposure) %>%
  summarise(
    Mean_LogEmp = mean(LogEmployment, na.rm=TRUE),
    .groups = "drop"
  ) %>%
  mutate(Group = ifelse(HighAIExposure == 1, "High AI Exposure", "Low AI Exposure"))

p_parallel <- ggplot(parallel_trends_data, aes(x = Year, y = Mean_LogEmp, 
                                                color = Group, linetype = Group)) +
  geom_line(size = 1.2) +
  geom_point(size = 3) +
  geom_vline(xintercept = 2022.5, linetype = "dashed", color = "black", size = 1) +
  annotate("text", x = 2022.5, y = max(parallel_trends_data$Mean_LogEmp), 
           label = "ChatGPT Release", vjust = -0.5, hjust = 0.5) +
  labs(
    title = "Parallel Trends: Employment by AI Exposure",
    x = "Year",
    y = "Mean Log Employment",
    color = "Group",
    linetype = "Group"
  ) +
  scale_color_manual(values = c("High AI Exposure" = "#E94F37", 
                                 "Low AI Exposure" = "#2E86AB")) +
  theme_minimal() +
  theme(
    plot.title = element_text(face = "bold"),
    legend.position = "bottom"
  )

ggsave("paper/figures/parallel_trends_complete.pdf", p_parallel, width = 12, height = 7, dpi = 300)
ggsave("paper/figures/parallel_trends_complete.png", p_parallel, width = 12, height = 7, dpi = 300)

cat("✓ Parallel trends plot saved to: paper/figures/parallel_trends_complete.pdf\n")

# -----------------------------------------------------------------------------
# 8. Statistical Significance Summary
# -----------------------------------------------------------------------------

cat("\n", rep("=", 80), "\n")
cat("STATISTICAL SIGNIFICANCE SUMMARY\n")
cat(rep("=", 80), "\n\n")

# Get main coefficient from preferred specification (Model 3)
main_coef <- coef(model3)["Treat"]
main_se <- sqrt(vcov(model3)["Treat", "Treat"])
main_tstat <- main_coef / main_se
main_pvalue <- 2 * (1 - pnorm(abs(main_tstat)))

cat(sprintf("Main Treatment Effect (Preferred Specification - Model 3):\n"))
cat(sprintf("  Coefficient: %.4f\n", main_coef))
cat(sprintf("  Standard Error: %.4f\n", main_se))
cat(sprintf("  t-statistic: %.3f\n", main_tstat))
cat(sprintf("  p-value: %.4f\n", main_pvalue))
cat(sprintf("  95%% CI: [%.4f, %.4f]\n", main_coef - 1.96*main_se, main_coef + 1.96*main_se))

cat(sprintf("\nInterpretation:\n"))
cat(sprintf("  Following ChatGPT's release, employment in high AI-exposure occupations\n"))
cat(sprintf("  changed by approximately %.2f%% relative to low AI-exposure occupations.\n", main_coef * 100))

# Effect size (Cohen's d)
pooled_sd <- sd(df$LogEmployment)
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

cat("\n", rep("=", 80), "\n")
cat("ANALYSIS COMPLETE\n")
cat(rep("=", 80), "\n")
cat("\nOutput files saved to:\n")
cat("  - paper/tables/main_results_complete.tex\n")
cat("  - paper/figures/event_study_complete.pdf\n")
cat("  - paper/figures/parallel_trends_complete.pdf\n")
