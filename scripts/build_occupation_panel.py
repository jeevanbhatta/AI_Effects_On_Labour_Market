"""
Build Occupation-Level Analysis Panel from BLS OES Data
========================================================

This script processes BLS Occupational Employment Statistics (OES) Research
Estimates data to create a comprehensive occupation-level panel for studying
the effects of Generative AI on labor markets.

Data Source: BLS OES Research Estimates by State and Industry (2015-2024)
URL: https://www.bls.gov/oes/oessrcres.htm

Panel Structure:
- State (52: 50 states + DC + national)
- Industry (NAICS sectors)
- Occupation (SOC codes, ~800 detailed occupations)
- Year (2015-2024, annual May reference period)

Output: data/occupation_panel.csv

Author: SS154 Final Project
Date: December 2025
"""

import os
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime
import json
import time

# Configuration
OES_RAW_DIR = Path(__file__).parent.parent / 'data' / 'oes_raw'
OUTPUT_DIR = Path(__file__).parent.parent / 'data'

# Test mode: set to True to process only one year for testing
TEST_MODE = '--test' in sys.argv
if TEST_MODE:
    YEARS = [2024]  # Process only 2024 for testing
    print("*** TEST MODE: Processing only 2024 ***", flush=True)
else:
    YEARS = range(2015, 2025)  # 2015-2024

# Treatment definition
CHATGPT_RELEASE_YEAR = 2022  # Nov 2022, so 2023 is first full post-treatment year
POST_TREATMENT_YEAR = 2023

print("="*70)
print("OCCUPATION-LEVEL PANEL CONSTRUCTION")
print("="*70)
print(f"Source: BLS OES Research Estimates (State × Industry × Occupation)")
print(f"Years: {min(YEARS)}-{max(YEARS)} (May reference period)")
print(f"Treatment: Post = 1 if Year >= {POST_TREATMENT_YEAR}")
print("="*70)


def load_oes_file(year):
    """
    Load and parse a single BLS OES research estimates file.
    
    Args:
        year (int): Year to load
        
    Returns:
        pd.DataFrame: Parsed OES data
    """
    filepath = OES_RAW_DIR / f"oes_research_{year}_allsectors.xlsx"
    
    if not filepath.exists():
        print(f"ERROR: File not found: {filepath}", flush=True)
        return None
    
    print(f"\n{'='*70}", flush=True)
    print(f"PROCESSING {year}", flush=True)
    print(f"{'='*70}", flush=True)
    print(f"File: {filepath.name} ({filepath.stat().st_size / 1024 / 1024:.1f} MB)", flush=True)
    
    try:
        # This is the slow part - reading large Excel files
        print(f"Reading Excel file (this may take 30-60 seconds for large files)...", flush=True)
        start_time = time.time()
        
        # Read Excel file (may have multiple sheets)
        xl_file = pd.ExcelFile(filepath, engine='openpyxl')
        print(f"  ✓ Excel file opened in {time.time() - start_time:.1f}s", flush=True)
        print(f"  Sheets found: {len(xl_file.sheet_names)}", flush=True)
        
        # Read first sheet
        print(f"  Reading sheet: {xl_file.sheet_names[0]}...", flush=True)
        read_start = time.time()
        df = pd.read_excel(xl_file, sheet_name=0, engine='openpyxl')
        print(f"  ✓ Sheet read in {time.time() - read_start:.1f}s", flush=True)
        
        print(f"  Raw shape: {df.shape[0]:,} rows × {df.shape[1]} columns", flush=True)
        print(f"  Sample columns: {list(df.columns[:5])}", flush=True)
        
        # Add year
        df['Year'] = year
        
        print(f"✓ Total time for {year}: {time.time() - start_time:.1f}s", flush=True)
        
        return df
        
    except Exception as e:
        print(f"ERROR loading file: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return None


def parse_oes_dataframe(df, year):
    """
    Parse and standardize OES dataframe structure.
    
    BLS OES files have varying column names across years. This function
    standardizes them.
    
    Expected columns (may vary by year):
    - AREA (or ST, STATE): State FIPS or name  
    - AREA_NAME (or STATE_NAME): State name
    - NAICS (or I_GROUP, INDUSTRY): Industry code
    - NAICS_TITLE (or INDUSTRY_TITLE): Industry name
    - OCC_CODE (or PRIM_STATE): Occupation SOC code
    - OCC_TITLE: Occupation title
    - TOT_EMP: Total employment
    - H_MEAN, A_MEAN: Hourly/Annual mean wage
    - And various percentile wages
    
    Args:
        df (pd.DataFrame): Raw OES data
        year (int): Year for logging
        
    Returns:
        pd.DataFrame: Standardized data
    """
    print(f"\n  Parsing {year} data...", flush=True)
    print(f"  All columns ({len(df.columns)}): {list(df.columns)}", flush=True)
    
    # Try to identify key columns (column names vary by year)
    col_mapping = {}
    
    # State columns
    for col in df.columns:
        col_lower = str(col).lower().strip()
        if col_lower in ['area', 'st', 'state', 'area_fips', 'st_fips']:
            col_mapping['State_Code'] = col
        elif col_lower in ['area_name', 'state_name', 'area_title', 'st_name']:
            col_mapping['State'] = col
        # Industry columns
        elif col_lower in ['naics', 'i_group', 'industry', 'naics_code']:
            col_mapping['Industry_Code'] = col
        elif col_lower in ['naics_title', 'industry_title', 'naics_desc', 'i_group_title']:
            col_mapping['Industry'] = col
        # Occupation columns
        elif col_lower in ['occ_code', 'occ code', 'prim_state', 'o_group']:
            col_mapping['Occupation_Code'] = col
        elif col_lower in ['occ_title', 'occ title', 'occupation_title', 'o_group_title']:
            col_mapping['Occupation'] = col
        # Employment
        elif col_lower in ['tot_emp', 'total_emp', 'employment', 'emp', 'jobs_1000']:
            col_mapping['Employment'] = col
        # Wages
        elif col_lower in ['a_mean', 'annual_mean', 'mean_annual', 'a_mean_wage']:
            col_mapping['Annual_Mean_Wage'] = col
        elif col_lower in ['h_mean', 'hourly_mean', 'mean_hourly', 'h_mean_wage']:
            col_mapping['Hourly_Mean_Wage'] = col
    
    print(f"  Identified key columns: {list(col_mapping.keys())}", flush=True)
    
    if not col_mapping:
        print(f"  WARNING: No columns could be mapped! Using first few columns as-is.", flush=True)
        df['Year'] = year  # Make sure Year is added
        return df
    
    # Rename columns
    df_renamed = df.rename(columns={v: k for k, v in col_mapping.items()})
    
    # Select only columns we successfully mapped
    available_cols = [col for col in col_mapping.keys() if col in df_renamed.columns]
    df_clean = df_renamed[available_cols + ['Year']].copy()
    
    print(f"  ✓ Standardized to {df_clean.shape[0]:,} rows × {df_clean.shape[1]} columns", flush=True)
    print(f"  Columns: {list(df_clean.columns)}", flush=True)
    
    return df_clean


def load_all_oes_data():
    """
    Load and combine all OES files (2015-2024).
    
    Returns:
        pd.DataFrame: Combined panel data
    """
    all_data = []
    total_start = time.time()
    
    print(f"\n{'='*70}", flush=True)
    print(f"LOADING ALL OES FILES ({len(YEARS)} files)", flush=True)
    print(f"{'='*70}", flush=True)
    print(f"This will take approximately {len(YEARS) * 0.5}-{len(YEARS)} minutes...", flush=True)
    
    for i, year in enumerate(YEARS, 1):
        print(f"\n[{i}/{len(YEARS)}] Processing year {year}...", flush=True)
        
        df = load_oes_file(year)
        if df is not None:
            df_clean = parse_oes_dataframe(df, year)
            all_data.append(df_clean)
            print(f"  ✓ Added {len(df_clean):,} observations for {year}", flush=True)
            
            # Memory cleanup
            del df, df_clean
            
            elapsed = time.time() - total_start
            avg_time = elapsed / i
            remaining = avg_time * (len(YEARS) - i)
            print(f"  Progress: {i}/{len(YEARS)} ({i/len(YEARS)*100:.0f}%) | "
                  f"Elapsed: {elapsed/60:.1f}m | ETA: {remaining/60:.1f}m", flush=True)
        else:
            print(f"  ✗ Failed to load {year}", flush=True)
    
    if not all_data:
        print("\nERROR: No data loaded!", flush=True)
        return None
    
    # Combine all years
    print(f"\nCombining {len(all_data)} dataframes...", flush=True)
    combine_start = time.time()
    panel = pd.concat(all_data, ignore_index=True)
    print(f"  ✓ Combined in {time.time() - combine_start:.1f}s", flush=True)
    
    print(f"\n{'='*70}", flush=True)
    print(f"COMBINED PANEL SUMMARY", flush=True)
    print(f"{'='*70}", flush=True)
    print(f"Total observations: {len(panel):,}", flush=True)
    print(f"Years: {sorted(panel['Year'].unique())}", flush=True)
    print(f"Columns: {list(panel.columns)}", flush=True)
    print(f"Total time: {(time.time() - total_start)/60:.1f} minutes", flush=True)
    
    return panel


def clean_and_filter_panel(panel):
    """
    Clean and filter the panel data.
    
    Operations:
    1. Remove missing/invalid employment values
    2. Convert employment to numeric
    3. Remove totals and aggregates
    4. Standardize codes
    
    Args:
        panel (pd.DataFrame): Raw panel
        
    Returns:
        pd.DataFrame: Cleaned panel
    """
    print(f"\n{'='*70}")
    print(f"DATA CLEANING")
    print(f"{'='*70}")
    
    initial_size = len(panel)
    print(f"Initial size: {initial_size:,}")
    
    # Clean employment variable
    if 'Employment' in panel.columns:
        # Convert to numeric, coercing errors
        panel['Employment'] = pd.to_numeric(panel['Employment'], errors='coerce')
        
        # Remove missing or zero employment
        panel = panel[panel['Employment'].notna()]
        panel = panel[panel['Employment'] > 0]
        
        print(f"After removing missing/zero employment: {len(panel):,} ({len(panel)/initial_size*100:.1f}%)")
    
    # Remove aggregate occupations (codes ending in '0000')
    if 'Occupation_Code' in panel.columns:
        panel = panel[~panel['Occupation_Code'].astype(str).str.endswith('0000')]
        print(f"After removing aggregate occupations: {len(panel):,} ({len(panel)/initial_size*100:.1f}%)")
    
    # Create log employment
    panel['LogEmployment'] = np.log(panel['Employment'])
    
    print(f"\nFinal cleaned size: {len(panel):,}")
    print(f"Unique states: {panel['State'].nunique() if 'State' in panel.columns else 'N/A'}")
    print(f"Unique industries: {panel['Industry_Code'].nunique() if 'Industry_Code' in panel.columns else 'N/A'}")
    print(f"Unique occupations: {panel['Occupation_Code'].nunique() if 'Occupation_Code' in panel.columns else 'N/A'}")
    
    return panel


def add_treatment_variables(panel):
    """
    Add treatment variables for DiD analysis.
    
    Creates:
    - Post: Indicator for post-ChatGPT period (Year >= 2023)
    - (Occupation exposure scores will be added separately)
    
    Args:
        panel (pd.DataFrame): Cleaned panel
        
    Returns:
        pd.DataFrame: Panel with treatment variables
    """
    print(f"\n{'='*70}")
    print(f"ADDING TREATMENT VARIABLES")
    print(f"{'='*70}")
    
    # Post-treatment indicator
    panel['Post'] = (panel['Year'] >= POST_TREATMENT_YEAR).astype(int)
    
    post_count = (panel['Post'] == 1).sum()
    pre_count = (panel['Post'] == 0).sum()
    
    print(f"Post-treatment (Year >= {POST_TREATMENT_YEAR}): {post_count:,} observations")
    print(f"Pre-treatment (Year < {POST_TREATMENT_YEAR}): {pre_count:,} observations")
    
    return panel


def add_occupation_exposure_scores(panel):
    """
    Add occupation-level exposure scores.
    
    NOTE: This is a placeholder. In a full implementation, these would come from:
    1. AI_Exposure_Score: ILO Working Paper 96 (Gmyrek et al. 2023) - ISCO-08 codes
    2. Teleworkability: Dingel & Neiman (2020) - SOC codes
    3. RoutineTaskIndex: Autor & Dorn (2013) / O*NET - SOC codes
    4. SkillIntensity: O*NET education requirements - SOC codes
    5. AutomationRisk_PreAI: Frey & Osborne (2017) - SOC codes
    
    For now, we'll flag that these need to be added from external sources.
    
    Args:
        panel (pd.DataFrame): Panel data
        
    Returns:
        pd.DataFrame: Panel with exposure scores
    """
    print(f"\n{'='*70}")
    print(f"OCCUPATION EXPOSURE SCORES")
    print(f"{'='*70}")
    print("NOTE: Occupation-level exposure scores require external data sources.")
    print("These should be matched using SOC occupation codes.")
    print("\nRequired sources:")
    print("1. ILO GPT Exposure Index (ISCO-08 → SOC crosswalk needed)")
    print("2. Dingel & Neiman Teleworkability (SOC)")
    print("3. Autor & Dorn Routine Task Index (SOC via O*NET)")
    print("4. O*NET Skill Intensity (SOC)")
    print("5. Frey & Osborne Automation Risk (SOC)")
    
    # Add placeholder columns
    panel['AI_Exposure_Score'] = np.nan
    panel['Teleworkability'] = np.nan
    panel['RoutineTaskIndex'] = np.nan
    panel['SkillIntensity'] = np.nan
    panel['AutomationRisk_PreAI'] = np.nan
    
    print("\nPlaceholder columns added. To populate:")
    print("1. Download occupation-level scores from academic papers")
    print("2. Create crosswalk between ISCO-08 and SOC codes")
    print("3. Match scores to Occupation_Code in this panel")
    
    return panel


def generate_summary_statistics(panel):
    """
    Generate and display summary statistics.
    
    Args:
        panel (pd.DataFrame): Final panel
    """
    print(f"\n{'='*70}")
    print(f"FINAL PANEL SUMMARY STATISTICS")
    print(f"{'='*70}")
    
    print(f"\nPanel Structure:")
    print(f"- Total observations: {len(panel):,}")
    print(f"- Years: {panel['Year'].min()} to {panel['Year'].max()}")
    print(f"- States: {panel['State'].nunique() if 'State' in panel.columns else 'N/A'}")
    print(f"- Industries: {panel['Industry_Code'].nunique() if 'Industry_Code' in panel.columns else 'N/A'}")
    print(f"- Occupations: {panel['Occupation_Code'].nunique() if 'Occupation_Code' in panel.columns else 'N/A'}")
    
    print(f"\nEmployment Statistics:")
    print(panel[['Employment', 'LogEmployment']].describe())
    
    print(f"\nTreatment Distribution:")
    print(panel['Post'].value_counts().sort_index())
    
    # Top 10 occupations by total employment
    if 'Occupation' in panel.columns and 'Occupation_Code' in panel.columns:
        print(f"\nTop 10 Occupations by Total Employment:")
        top_occs = panel.groupby(['Occupation_Code', 'Occupation'])['Employment'].sum().sort_values(ascending=False).head(10)
        for (code, title), emp in top_occs.items():
            print(f"  {code} - {title[:50]}: {emp:,.0f}")
    
    # Missing values
    print(f"\nMissing Values:")
    print(panel.isnull().sum())


def save_panel(panel):
    """
    Save the panel to CSV with metadata.
    
    Args:
        panel (pd.DataFrame): Final panel
    """
    # Save main panel
    output_path = OUTPUT_DIR / 'occupation_panel.csv'
    panel.to_csv(output_path, index=False)
    print(f"\n{'='*70}")
    print(f"OUTPUT")
    print(f"{'='*70}")
    print(f"Panel saved to: {output_path}")
    print(f"File size: {output_path.stat().st_size / 1024 / 1024:.1f} MB")
    
    # Save metadata
    metadata = {
        'source': 'BLS Occupational Employment Statistics (OES) Research Estimates',
        'url': 'https://www.bls.gov/oes/oessrcres.htm',
        'creation_date': datetime.now().isoformat(),
        'years': list(range(min(YEARS), max(YEARS) + 1)),
        'post_treatment_year': POST_TREATMENT_YEAR,
        'n_observations': len(panel),
        'n_states': int(panel['State'].nunique()) if 'State' in panel.columns else None,
        'n_industries': int(panel['Industry_Code'].nunique()) if 'Industry_Code' in panel.columns else None,
        'n_occupations': int(panel['Occupation_Code'].nunique()) if 'Occupation_Code' in panel.columns else None,
        'columns': list(panel.columns),
        'notes': [
            'Annual data (May reference period)',
            'State × Industry × Occupation level',
            'Occupation exposure scores are placeholders - need to be populated from academic sources',
            'Employment is total employment, not FTE',
            'Some observations suppressed by BLS for confidentiality'
        ]
    }
    
    metadata_path = OUTPUT_DIR / 'occupation_panel_metadata.json'
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"Metadata saved to: {metadata_path}")


def main():
    """Main execution function."""
    
    # Step 1: Load all OES files
    print("\nSTEP 1: Loading OES files...")
    panel = load_all_oes_data()
    
    if panel is None:
        sys.exit(1)
    
    # Step 2: Clean and filter
    print("\nSTEP 2: Cleaning data...")
    panel = clean_and_filter_panel(panel)
    
    # Step 3: Add treatment variables
    print("\nSTEP 3: Adding treatment variables...")
    panel = add_treatment_variables(panel)
    
    # Step 4: Add occupation exposure scores (placeholders)
    print("\nSTEP 4: Adding occupation exposure scores...")
    panel = add_occupation_exposure_scores(panel)
    
    # Step 5: Generate summary statistics
    print("\nSTEP 5: Generating summary statistics...")
    generate_summary_statistics(panel)
    
    # Step 6: Save
    print("\nSTEP 6: Saving output...")
    save_panel(panel)
    
    print(f"\n{'='*70}")
    print(f"PROCESSING COMPLETE")
    print(f"{'='*70}")
    print(f"\nNext steps:")
    print(f"1. Obtain occupation-level exposure scores from academic sources")
    print(f"2. Create ISCO-08 to SOC crosswalk for AI exposure scores")
    print(f"3. Match scores to occupations in occupation_panel.csv")
    print(f"4. Run preliminary DiD analysis")


if __name__ == '__main__':
    main()
