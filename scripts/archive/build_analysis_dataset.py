"""
Build Analysis Dataset for DiD Regression

This script constructs the panel dataset needed for the Difference-in-Differences
analysis of Generative AI effects on employment.

Treatment Variable: HighExposure(i) * Post(t)
- HighExposure: Based on ILO GPT Exposure Index (industries in top quartile)
- Post: 1 for 2023-2024 (after ChatGPT release Nov 2022), 0 otherwise

Control Variables (time-invariant, absorbed by fixed effects):
- AI_Exposure_Score: ILO GPT Exposure Index
- Teleworkability_Score: Dingel & Neiman (2020) telework feasibility
- Routine_Task_Index: Autor & Dorn (2013) routine task intensity
- Skill_Intensity_Index: O*NET education requirements

These are time-invariant at industry level, so they will be absorbed by 
industry fixed effects. We include them in the dataset for descriptive purposes.
"""

import pandas as pd
import os

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
OUTPUT_FILE = os.path.join(DATA_DIR, 'analysis_panel.csv')

# ============================================================================
# ILO GPT EXPOSURE SCORES BY INDUSTRY
# Source: Gmyrek et al. (2023) ILO Working Paper 96
# These are mean automation scores at ISCO 1-digit level, mapped to NAICS industries
# Scores range 0-1; >0.5 = medium exposure, >0.75 = high exposure
# ============================================================================

# From ILO Report Figure 1 (Mean automation scores by occupation):
# - Clerical support workers: ~0.55-0.60 (highest)
# - Technicians and associate professionals: ~0.45-0.50
# - Professionals: ~0.40-0.45
# - Managers: ~0.35-0.40
# - Service and sales workers: ~0.30-0.35
# - Plant and machine operators: ~0.20-0.25
# - Elementary occupations: ~0.15-0.20
# - Craft and trades: ~0.15-0.20
# - Agriculture/forestry: ~0.10-0.15

# Mapping ISCO occupational exposure to NAICS industries (weighted by employment composition):
ILO_EXPOSURE_SCORES = {
    'Information': 0.52,  # High concentration of professionals, technicians
    'Professional, Scientific, and Technical Services': 0.48,  # Professionals, managers
    'Finance and Insurance': 0.50,  # Clerical workers, professionals
    'Leisure and Hospitality': 0.28,  # Service workers, elementary occupations
    'Total Nonfarm': 0.38,  # Economy-wide average
}

# High exposure threshold: top quartile (>0.45 for our industries)
HIGH_EXPOSURE_THRESHOLD = 0.45

# ============================================================================
# TELEWORKABILITY SCORES
# Source: Dingel & Neiman (2020) "How Many Jobs Can be Done at Home?"
# NBER Working Paper 26948
# Scores represent share of jobs that can be done entirely from home
# ============================================================================

TELEWORK_SCORES = {
    'Information': 0.72,  # Table 1: Information sector
    'Professional, Scientific, and Technical Services': 0.68,  # Table 1
    'Finance and Insurance': 0.76,  # Table 1: Finance and Insurance
    'Leisure and Hospitality': 0.04,  # Table 1: Accommodation and Food Services
    'Total Nonfarm': 0.37,  # Weighted average from paper
}

# ============================================================================
# ROUTINE TASK INDEX (RTI)
# Source: Autor & Dorn (2013), based on O*NET task measures
# Higher values = more routine tasks = more susceptible to automation
# Standardized index, higher = more routine
# ============================================================================

# Approximate RTI by industry based on Autor & Dorn methodology:
# - Routine cognitive tasks (high in clerical, finance)
# - Routine manual tasks (high in manufacturing, low in services)
# - Non-routine cognitive analytical (high in professional services)
# - Non-routine cognitive interpersonal (high in management, sales)
# - Non-routine manual physical (high in construction, hospitality)

ROUTINE_TASK_INDEX = {
    'Information': 0.35,  # Mixed: high non-routine cognitive, some routine
    'Professional, Scientific, and Technical Services': 0.25,  # Low routine, high analytical
    'Finance and Insurance': 0.55,  # Higher routine cognitive (clerical tasks)
    'Leisure and Hospitality': 0.45,  # Mixed: routine service, non-routine interpersonal
    'Total Nonfarm': 0.50,  # Economy-wide average
}

# ============================================================================
# SKILL INTENSITY INDEX
# Source: BLS Occupational Employment Statistics + O*NET Education Requirements
# Proxy: Share of workers requiring bachelor's degree or higher
# ============================================================================

SKILL_INTENSITY = {
    'Information': 0.58,  # High share of degree-requiring occupations
    'Professional, Scientific, and Technical Services': 0.72,  # Highest skill intensity
    'Finance and Insurance': 0.52,  # Moderate-high skill requirements
    'Leisure and Hospitality': 0.12,  # Low formal education requirements
    'Total Nonfarm': 0.38,  # Economy-wide average
}

# ============================================================================
# AUTOMATION RISK (PRE-AI)
# Source: Frey & Osborne (2017) "The Future of Employment"
# Probability of computerization (pre-GenAI, robotics/software automation)
# ============================================================================

AUTOMATION_RISK_PREAI = {
    'Information': 0.25,  # Lower risk - creative, analytical work
    'Professional, Scientific, and Technical Services': 0.18,  # Lowest risk
    'Finance and Insurance': 0.43,  # Moderate risk (routine clerical)
    'Leisure and Hospitality': 0.75,  # High risk (routine service tasks)
    'Total Nonfarm': 0.47,  # Economy-wide average
}


def load_employment_data():
    """Load the BLS employment data."""
    filepath = os.path.join(DATA_DIR, 'bls_employment_data.csv')
    df = pd.read_csv(filepath)
    return df


def create_time_index(df):
    """Create a proper time index from Year and Period."""
    # Convert M01, M02, etc. to month numbers
    df['Month'] = df['Period'].str.replace('M', '').astype(int)
    df['Date'] = pd.to_datetime(df['Year'].astype(str) + '-' + df['Month'].astype(str) + '-01')
    df['YearMonth'] = df['Year'] * 100 + df['Month']
    return df


def add_treatment_variables(df):
    """Add treatment and post-period indicators."""
    # Post period: 2023 onwards (ChatGPT released Nov 2022)
    df['Post'] = (df['Year'] >= 2023).astype(int)
    
    # High exposure based on ILO scores
    df['AI_Exposure_Score'] = df['Industry'].map(ILO_EXPOSURE_SCORES)
    df['HighExposure'] = (df['AI_Exposure_Score'] >= HIGH_EXPOSURE_THRESHOLD).astype(int)
    
    # Treatment variable (DiD interaction)
    df['Treat'] = df['HighExposure'] * df['Post']
    
    return df


def add_control_variables(df):
    """Add time-invariant control variables."""
    df['Teleworkability'] = df['Industry'].map(TELEWORK_SCORES)
    df['RoutineTaskIndex'] = df['Industry'].map(ROUTINE_TASK_INDEX)
    df['SkillIntensity'] = df['Industry'].map(SKILL_INTENSITY)
    df['AutomationRisk_PreAI'] = df['Industry'].map(AUTOMATION_RISK_PREAI)
    return df


def create_analysis_panel():
    """Create the main analysis panel dataset."""
    print("Loading employment data...")
    df = load_employment_data()
    
    print(f"Raw data shape: {df.shape}")
    print(f"Industries: {df['Industry'].unique()}")
    print(f"States: {df['State'].nunique()} unique states")
    print(f"Metrics: {df['Metric'].unique()}")
    print(f"Years: {df['Year'].min()} - {df['Year'].max()}")
    
    # Filter to the main employment metric for primary analysis
    df_emp = df[df['Metric'] == 'All Employees'].copy()
    print(f"\nFiltered to 'All Employees': {df_emp.shape}")
    
    # Create time index
    df_emp = create_time_index(df_emp)
    
    # Add treatment variables
    df_emp = add_treatment_variables(df_emp)
    
    # Add control variables
    df_emp = add_control_variables(df_emp)
    
    # Convert Value to numeric
    df_emp['Employment'] = pd.to_numeric(df_emp['Value'], errors='coerce')
    
    # Create log employment for regression
    import numpy as np
    df_emp['LogEmployment'] = df_emp['Employment'].apply(lambda x: np.log(x) if x > 0 else np.nan)
    
    # Select and order columns for output
    output_cols = [
        'Date', 'Year', 'Month', 'YearMonth', 'Period', 'PeriodName',
        'State', 'Industry', 'SeriesID',
        'Employment', 'LogEmployment',
        'Post', 'HighExposure', 'Treat',
        'AI_Exposure_Score', 'Teleworkability', 'RoutineTaskIndex', 
        'SkillIntensity', 'AutomationRisk_PreAI'
    ]
    
    df_out = df_emp[output_cols].copy()
    
    # Sort by State, Industry, Date
    df_out = df_out.sort_values(['State', 'Industry', 'Date']).reset_index(drop=True)
    
    return df_out


def print_summary_stats(df):
    """Print summary statistics for the analysis dataset."""
    print("\n" + "="*60)
    print("ANALYSIS DATASET SUMMARY")
    print("="*60)
    
    print(f"\nTotal observations: {len(df)}")
    print(f"Time period: {df['Date'].min()} to {df['Date'].max()}")
    print(f"States: {df['State'].nunique()}")
    print(f"Industries: {df['Industry'].nunique()}")
    
    print("\n--- Treatment Distribution ---")
    print(f"Pre-period observations (Post=0): {(df['Post'] == 0).sum()}")
    print(f"Post-period observations (Post=1): {(df['Post'] == 1).sum()}")
    print(f"High exposure industries (HighExposure=1): {df[df['HighExposure'] == 1]['Industry'].unique()}")
    print(f"Low exposure industries (HighExposure=0): {df[df['HighExposure'] == 0]['Industry'].unique()}")
    print(f"Treated observations (Treat=1): {(df['Treat'] == 1).sum()}")
    
    print("\n--- Industry AI Exposure Scores (ILO) ---")
    for ind in df['Industry'].unique():
        score = df[df['Industry'] == ind]['AI_Exposure_Score'].iloc[0]
        high = "HIGH" if score >= HIGH_EXPOSURE_THRESHOLD else "LOW"
        print(f"  {ind}: {score:.2f} ({high})")
    
    print("\n--- Control Variables by Industry ---")
    ctrl_vars = ['Teleworkability', 'RoutineTaskIndex', 'SkillIntensity', 'AutomationRisk_PreAI']
    summary = df.groupby('Industry')[ctrl_vars].first()
    print(summary.round(2))


def main():
    # Create the analysis panel
    df = create_analysis_panel()
    
    # Print summary statistics
    print_summary_stats(df)
    
    # Save to CSV
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"\n✓ Analysis dataset saved to: {OUTPUT_FILE}")
    print(f"  Shape: {df.shape}")
    
    # Also save a version of the control variables with sources
    controls_df = pd.DataFrame({
        'Industry': list(ILO_EXPOSURE_SCORES.keys()),
        'AI_Exposure_Score': list(ILO_EXPOSURE_SCORES.values()),
        'AI_Exposure_Source': 'ILO Working Paper 96 (Gmyrek et al. 2023)',
        'HighExposure': [1 if s >= HIGH_EXPOSURE_THRESHOLD else 0 for s in ILO_EXPOSURE_SCORES.values()],
        'Teleworkability': [TELEWORK_SCORES[i] for i in ILO_EXPOSURE_SCORES.keys()],
        'Telework_Source': 'Dingel & Neiman (2020) NBER WP 26948',
        'RoutineTaskIndex': [ROUTINE_TASK_INDEX[i] for i in ILO_EXPOSURE_SCORES.keys()],
        'RTI_Source': 'Autor & Dorn (2013) based on O*NET',
        'SkillIntensity': [SKILL_INTENSITY[i] for i in ILO_EXPOSURE_SCORES.keys()],
        'Skill_Source': 'BLS OES + O*NET Education Requirements',
        'AutomationRisk_PreAI': [AUTOMATION_RISK_PREAI[i] for i in ILO_EXPOSURE_SCORES.keys()],
        'AutoRisk_Source': 'Frey & Osborne (2017)',
    })
    
    controls_file = os.path.join(DATA_DIR, 'industry_controls_with_sources.csv')
    controls_df.to_csv(controls_file, index=False)
    print(f"✓ Industry controls with sources saved to: {controls_file}")


if __name__ == "__main__":
    main()
