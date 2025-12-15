#!/usr/bin/env python3
"""
Generate comprehensive data dictionary from occupation panel.
Uses efficient pandas operations for large files.
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_FILE = BASE_DIR / "data" / "occupation_panel.csv"
OUTPUT_FILE = BASE_DIR / "docs" / "DATA_DICTIONARY.md"

print(f"Loading data from: {DATA_FILE}")
print("This may take 30-60 seconds for large files...")

# Read without strict dtypes (BLS uses * for suppressed values)
df = pd.read_csv(DATA_FILE, low_memory=False)

# Convert numeric columns (handle BLS symbols like *, #, **)
numeric_cols = ['Employment', 'Hourly_Mean_Wage', 'Annual_Mean_Wage', 'LogEmployment']
for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

print(f"✓ Loaded {len(df):,} observations")

print("Generating data dictionary...")

with open(OUTPUT_FILE, 'w') as f:
    f.write('# Data Dictionary: Occupation Panel\n\n')
    f.write(f'Generated from: `data/occupation_panel.csv`\n\n')
    f.write(f'**Total Observations:** {len(df):,}\n\n')
    f.write(f'**Date Generated:** December 16, 2025\n\n')
    f.write('---\n\n')
    
    # === CATEGORICAL VARIABLES ===
    f.write('## Categorical Variables\n\n')
    
    # States
    print("  Processing states...")
    f.write('### States\n\n')
    states = df[['State_Code', 'State']].drop_duplicates().sort_values('State_Code')
    f.write(f'**Total unique states:** {len(states)}\n\n')
    f.write('<details>\n<summary>Click to expand state list ({} states)</summary>\n\n'.format(len(states)))
    f.write('| Code | State |\n')
    f.write('|------|-------|\n')
    for _, row in states.iterrows():
        f.write(f'| {row["State_Code"]} | {row["State"]} |\n')
    f.write('\n</details>\n\n')
    
    # Industries
    print("  Processing industries...")
    f.write('### Industries\n\n')
    industries = df[['Industry_Code', 'Industry']].drop_duplicates().sort_values('Industry_Code')
    f.write(f'**Total unique industries:** {len(industries)}\n\n')
    f.write('<details>\n<summary>Click to expand industry list ({} industries)</summary>\n\n'.format(len(industries)))
    f.write('| Industry |\n')
    f.write('|----------|\n')
    for _, row in industries.iterrows():
        f.write(f'| {row["Industry"]} |\n')
    f.write('\n</details>\n\n')
    
    # Occupations
    print("  Processing occupations...")
    f.write('### Occupations\n\n')
    # Get unique occupations efficiently
    occ_counts = df.groupby(['Occupation_Code', 'Occupation']).size().reset_index(name='obs_count')
    occ_counts = occ_counts.sort_values('Occupation_Code')
    
    f.write(f'**Total unique occupations:** {len(occ_counts)}\n\n')
    f.write('<details>\n<summary>Click to expand full occupation list ({} occupations)</summary>\n\n'.format(len(occ_counts)))
    f.write('| SOC Code | Occupation Title | Observations |\n')
    f.write('|----------|------------------|-------------|\n')
    for _, row in occ_counts.iterrows():
        occ_code = row['Occupation_Code'] if pd.notna(row['Occupation_Code']) else 'N/A'
        occ_title = row['Occupation'] if pd.notna(row['Occupation']) else 'N/A'
        f.write(f'| {occ_code} | {occ_title} | {row["obs_count"]:,} |\n')
    f.write('\n</details>\n\n')
    
    # Top 20 occupations by employment
    print("  Calculating top occupations...")
    f.write('### Top 20 Occupations by Total Employment\n\n')
    top_occs = df.groupby(['Occupation_Code', 'Occupation'], dropna=False)['Employment'].sum().sort_values(ascending=False).head(20)
    f.write('| Rank | SOC Code | Occupation | Total Employment |\n')
    f.write('|------|----------|------------|------------------|\n')
    for i, ((code, title), emp) in enumerate(top_occs.items(), 1):
        code_str = code if pd.notna(code) else 'N/A'
        title_str = title if pd.notna(title) else 'N/A'
        f.write(f'| {i} | {code_str} | {title_str} | {emp:,.0f} |\n')
    f.write('\n')
    
    # Years
    print("  Processing years...")
    f.write('### Years\n\n')
    years = sorted(df['Year'].unique())
    f.write(f'**Years:** {years[0]}-{years[-1]}\n\n')
    f.write(f'**Total years:** {len(years)}\n\n')
    
    # Observations by year
    year_counts = df['Year'].value_counts().sort_index()
    f.write('| Year | Observations |\n')
    f.write('|------|-------------|\n')
    for year, count in year_counts.items():
        f.write(f'| {year} | {count:,} |\n')
    f.write('\n')
    
    # Treatment
    print("  Processing treatment variable...")
    f.write('### Treatment Variable\n\n')
    f.write('**Post:** Indicator for post-ChatGPT period (Year >= 2023)\n\n')
    post_dist = df['Post'].value_counts().sort_index()
    f.write('| Post | Observations | Percent |\n')
    f.write('|------|--------------|----------|\n')
    for val, count in post_dist.items():
        label = "Pre-treatment" if val == 0 else "Post-treatment"
        f.write(f'| {val} ({label}) | {count:,} | {count/len(df)*100:.1f}% |\n')
    f.write('\n')
    
    # === NUMERIC VARIABLES ===
    f.write('---\n\n')
    f.write('## Numeric Variables\n\n')
    
    numeric_cols = ['Employment', 'Hourly_Mean_Wage', 'Annual_Mean_Wage', 'LogEmployment']
    
    for col in numeric_cols:
        print(f"  Processing {col}...")
        f.write(f'### {col}\n\n')
        
        # Basic stats
        stats = df[col].describe()
        f.write('| Statistic | Value |\n')
        f.write('|-----------|-------|\n')
        f.write(f'| Count | {stats["count"]:,.0f} |\n')
        f.write(f'| Mean | {stats["mean"]:,.2f} |\n')
        f.write(f'| Std Dev | {stats["std"]:,.2f} |\n')
        f.write(f'| Min | {stats["min"]:,.2f} |\n')
        f.write(f'| 25th % | {stats["25%"]:,.2f} |\n')
        f.write(f'| Median | {stats["50%"]:,.2f} |\n')
        f.write(f'| 75th % | {stats["75%"]:,.2f} |\n')
        f.write(f'| Max | {stats["max"]:,.2f} |\n')
        
        # Distribution bins
        f.write('\n**Distribution:**\n\n')
        if col == 'LogEmployment':
            bins = [0, 4, 5, 6, 7, 8, 100]
            labels = ['< 4', '4-5', '5-6', '6-7', '7-8', '> 8']
        elif col == 'Employment':
            bins = [0, 100, 500, 1000, 5000, 10000, 1000000000]
            labels = ['< 100', '100-500', '500-1K', '1K-5K', '5K-10K', '> 10K']
        elif 'Wage' in col:
            bins = [0, 15, 25, 35, 50, 75, 100000]
            labels = ['< 15', '15-25', '25-35', '35-50', '50-75', '> 75']
        
        dist = pd.cut(df[col], bins=bins, labels=labels).value_counts().sort_index()
        f.write('| Range | Count | Percent |\n')
        f.write('|-------|-------|----------|\n')
        for rng, count in dist.items():
            f.write(f'| {rng} | {count:,} | {count/len(df)*100:.1f}% |\n')
        f.write('\n')
    
    # === MISSING VALUES ===
    print("  Calculating missing values...")
    f.write('---\n\n')
    f.write('## Missing Values\n\n')
    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(1)
    
    f.write('| Variable | Missing Count | Missing % |\n')
    f.write('|----------|---------------|----------|\n')
    for col in df.columns:
        if missing[col] > 0:
            f.write(f'| {col} | {missing[col]:,} | {missing_pct[col]:.1f}% |\n')
        else:
            f.write(f'| {col} | 0 | 0.0% |\n')
    f.write('\n')
    
    # === PANEL STRUCTURE ===
    print("  Calculating panel structure...")
    f.write('---\n\n')
    f.write('## Panel Structure\n\n')
    f.write(f'**Dimensions:** State × Industry × Occupation × Year\n\n')
    
    n_states = df['State'].nunique()
    n_industries = df['Industry'].nunique()
    n_occupations = df['Occupation'].nunique()
    n_years = df['Year'].nunique()
    theoretical_max = n_states * n_industries * n_occupations * n_years
    
    f.write(f'- States: {n_states}\n')
    f.write(f'- Industries: {n_industries}\n')
    f.write(f'- Occupations: {n_occupations}\n')
    f.write(f'- Years: {n_years}\n')
    f.write(f'- **Theoretical max observations:** {n_states} × {n_industries} × {n_occupations} × {n_years} = {theoretical_max:,}\n')
    f.write(f'- **Actual observations:** {len(df):,} ({len(df) / theoretical_max * 100:.1f}% of theoretical max)\n\n')
    
    f.write('**Note:** Missing observations are due to:\n')
    f.write('- BLS suppression of cells with small employment counts\n')
    f.write('- Occupation-industry combinations that do not exist\n')
    f.write('- Data quality filters applied during processing\n\n')
    
    # Balance check
    f.write('### Panel Balance\n\n')
    obs_per_unit = df.groupby(['State', 'Industry', 'Occupation']).size()
    f.write(f'**State × Industry × Occupation units:** {len(obs_per_unit):,}\n\n')
    f.write('| Years per unit | Count | Percent |\n')
    f.write('|----------------|-------|----------|\n')
    balance = obs_per_unit.value_counts().sort_index()
    for years, count in balance.items():
        f.write(f'| {years} | {count:,} | {count/len(obs_per_unit)*100:.1f}% |\n')

print(f'\n✓ Data dictionary saved to: {OUTPUT_FILE}')
print(f'  File size: {OUTPUT_FILE.stat().st_size / 1024:.1f} KB')
