library(fixest)
library(dplyr)
library(ggplot2)
library(broom)

# Treatment timing
df <- df %>%
  mutate(
    post_2023 = as.integer(Year == 2023),
    post_2024 = as.integer(Year == 2024),
    rel_year  = Year - 2023
  )


#continuous event study
m_event_cont <- feols(
  LogEmployment ~
    i(rel_year, AI_Exposure_Score, ref = -1) +
    Teleworkability +
    AutomationRisk_PreAI |
    unit_id + Year,
  data = df,
  cluster = ~unit_id
)

event_df_cont <- broom::tidy(m_event_cont) %>%
  filter(grepl("AI_Exposure_Score", term)) %>%
  mutate(
    rel_year = as.integer(sub("rel_year::(-?[0-9]+):.*", "\\1", term))
  )


#event study plot
ggplot(event_df_cont, aes(x = rel_year, y = estimate)) +
  geom_point(size = 2) +
  geom_errorbar(
    aes(
      ymin = estimate - 1.96 * std.error,
      ymax = estimate + 1.96 * std.error
    ),
    width = 0.2
  ) +
  geom_hline(yintercept = 0) +
  geom_vline(xintercept = 0, linetype = "dashed") +
  labs(
    title = "Event Study: AI Exposure and Employment",
    subtitle = "Effects relative to 2022 (pre-treatment year)",
    x = "Years relative to AI introduction (2023)",
    y = "Effect of AI Exposure on Log Employment"
  ) +
  theme_minimal()


#quartile based event study
baseline_exposure <- df %>%
  filter(Year <= 2022) %>%
  group_by(unit_id) %>%
  summarise(AI_base = mean(AI_Exposure_Score), .groups = "drop")

df_q <- df %>%
  left_join(baseline_exposure, by = "unit_id") %>%
  mutate(
    exposure_q = ntile(AI_base, 4)
  )
df_q_plot <- df_q %>%
  group_by(Year, exposure_q) %>%
  summarise(mean_log_emp = mean(LogEmployment), .groups = "drop") %>%
  group_by(exposure_q) %>%
  mutate(
    baseline = mean(mean_log_emp[Year == 2019]),
    norm_log_emp = mean_log_emp - baseline
  ) %>%
  ungroup()

ggplot(df_q_plot,
       aes(x = Year, y = norm_log_emp, color = factor(exposure_q))) +
  geom_line(linewidth = 1.1) +
  geom_point(size = 2) +
  geom_vline(xintercept = 2023, linetype = "dashed") +
  labs(
    title = "Employment Trends by AI Exposure Quartile",
    subtitle = "Normalized to 2019",
    x = "Year",
    y = "Change in Log Employment",
    color = "AI Exposure Quartile"
  ) +
  theme_minimal()


#robustness: unit specific linear trends
df <- df %>%
  mutate(time = Year - min(Year))

m_trends <- feols(
  LogEmployment ~
    AI_Exposure_Score:post_2023 +
    AI_Exposure_Score:post_2024 +
    Teleworkability +
    AutomationRisk_PreAI |
    unit_id + Year + unit_id[time],
  data = df,
  cluster = ~unit_id
)

etable(m_baseline, m_trends, se = "cluster")

#placebo event study
df_placebo <- df %>%
  filter(Year <= 2021) %>%
  mutate(placebo_rel_year = Year - 2019)

m_placebo <- feols(
  LogEmployment ~
    i(placebo_rel_year, AI_Exposure_Score, ref = -1) +
    Teleworkability +
    AutomationRisk_PreAI |
    unit_id + Year,
  data = df_placebo,
  cluster = ~unit_id
)

event_df_placebo <- broom::tidy(m_placebo) %>%
  filter(grepl("AI_Exposure_Score", term)) %>%
  mutate(
    placebo_rel_year = as.integer(sub("placebo_rel_year::(-?[0-9]+):.*", "\\1", term))
  )

#placebo plot
ggplot(event_df_placebo, aes(x = placebo_rel_year, y = estimate)) +
  geom_point(size = 2) +
  geom_errorbar(
    aes(
      ymin = estimate - 1.96 * std.error,
      ymax = estimate + 1.96 * std.error
    ),
    width = 0.2
  ) +
  geom_hline(yintercept = 0) +
  geom_vline(xintercept = 0, linetype = "dashed") +
  labs(
    title = "Placebo Event Study (Artificial Treatment in 2019)",
    subtitle = "Pre-2022 data only",
    x = "Years Relative to Placebo Treatment",
    y = "Effect of AI Exposure on Log Employment"
  ) +
  theme_minimal()


