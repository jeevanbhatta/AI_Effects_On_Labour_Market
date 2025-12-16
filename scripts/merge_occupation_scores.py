#!/usr/bin/env python3
"""
Merge Occupation-Level Scores into Panel Data

This script merges teleworkability and automation risk scores into occupation_panel.csv.

Data Sources:
- Dingel & Neiman (2020) - Teleworkability (from GitHub replication package)
- Frey & Osborne (2017) - Pre-AI Automation Risk (from published paper)

Matching Strategy:
- 2015-2017: Match on SOC codes (Occupation_Code column)
- 2018-2024: Match on occupation names (Occupation column)

Author: Data pipeline
Date: 2024
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json
from datetime import datetime

# File paths
BASE_DIR = Path(__file__).parent.parent
PANEL_PATH = BASE_DIR / "data" / "occupation_panel.csv"
SCORES_PATH = BASE_DIR / "data" / "occupation_telework_automation.csv"
OUTPUT_PATH = BASE_DIR / "data" / "occupation_panel.csv"
METADATA_PATH = BASE_DIR / "data" / "occupation_panel_metadata.json"

# Occupation name mappings for 2018-2024 data
OCCUPATION_NAME_MAPPINGS = {
    # Management Occupations
    "Chief executives": ["Chief Executives"],
    "General and operations managers": ["General and Operations Managers"],
    "Advertising and promotions managers": ["Advertising and Promotions Managers"],
    "Marketing managers": ["Marketing Managers"],
    "Sales managers": ["Sales Managers"],
    "Public relations and fundraising managers": ["Public Relations and Fundraising Managers", "Public Relations Managers"],
    "Administrative services managers": ["Administrative Services Managers"],
    "Computer and information systems managers": ["Computer and Information Systems Managers"],
    "Financial managers": ["Financial Managers", "Treasurers and Controllers"],
    "Industrial production managers": ["Industrial Production Managers"],
    
    # Business and Financial Operations
    "Accountants and auditors": ["Accountants and Auditors"],
    "Financial analysts": ["Financial Analysts"],
    "Personal financial advisors": ["Personal Financial Advisors"],
    "Market research analysts and marketing specialists": ["Market Research Analysts and Marketing Specialists"],
    "Human resources specialists": ["Human Resources Specialists"],
    "Management analysts": ["Management Analysts"],
    
    # Computer and Mathematical Occupations
    "Computer systems analysts": ["Computer Systems Analysts"],
    "Information security analysts": ["Information Security Analysts"],
    "Computer programmers": ["Computer Programmers"],
    "Software developers": ["Software Developers, Applications", "Software Developers, Systems Software"],
    "Web developers": ["Web Developers"],
    "Database administrators": ["Database Administrators"],
    "Network and computer systems administrators": ["Network and Computer Systems Administrators"],
    "Computer network architects": ["Computer Network Architects"],
    "Computer support specialists": ["Computer Support Specialists"],
    "Operations research analysts": ["Operations Research Analysts"],
    "Actuaries": ["Actuaries"],
    "Mathematicians": ["Mathematicians"],
    "Statisticians": ["Statisticians"],
    
    # Architecture and Engineering
    "Architects, except landscape and naval": ["Architects, Except Landscape and Naval"],
    "Civil engineers": ["Civil Engineers"],
    "Mechanical engineers": ["Mechanical Engineers"],
    "Electrical engineers": ["Electrical Engineers"],
    "Electronics engineers, except computer": ["Electronics Engineers, Except Computer"],
    "Industrial engineers": ["Industrial Engineers"],
    "Aerospace engineers": ["Aerospace Engineers"],
    "Computer hardware engineers": ["Computer Hardware Engineers"],
    
    # Life, Physical, and Social Science Occupations
    "Medical scientists, except epidemiologists": ["Medical Scientists, Except Epidemiologists"],
    "Chemists": ["Chemists"],
    "Economists": ["Economists"],
    "Psychologists": ["Psychologists", "Clinical, Counseling, and School Psychologists"],
    
    # Legal Occupations
    "Lawyers": ["Lawyers"],
    "Paralegals and legal assistants": ["Paralegals and Legal Assistants"],
    
    # Education, Training, and Library Occupations
    "Postsecondary teachers": ["Postsecondary Teachers"],
    "Elementary and middle school teachers": ["Elementary School Teachers, Except Special Education", "Middle School Teachers, Except Special and Career/Technical Education"],
    "Secondary school teachers": ["Secondary School Teachers, Except Special and Career/Technical Education"],
    "Special education teachers": ["Special Education Teachers"],
    "Librarians": ["Librarians"],
    
    # Healthcare Practitioners and Technical Occupations
    "Physicians and surgeons": ["Physicians and Surgeons"],
    "Dentists": ["Dentists"],
    "Pharmacists": ["Pharmacists"],
    "Physician assistants": ["Physician Assistants"],
    "Registered nurses": ["Registered Nurses"],
    "Physical therapists": ["Physical Therapists"],
    "Occupational therapists": ["Occupational Therapists"],
    "Diagnostic related technologists and technicians": ["Radiologic Technologists and Technicians"],
    
    # Healthcare Support Occupations
    "Nursing assistants": ["Nursing Assistants"],
    "Medical assistants": ["Medical Assistants"],
    
    # Protective Service Occupations
    "First-line supervisors of police and detectives": ["First-Line Supervisors of Police and Detectives"],
    "Police and sheriff's patrol officers": ["Police and Sheriff's Patrol Officers"],
    "Firefighters": ["Firefighters"],
    
    # Food Preparation and Serving Related Occupations
    "Chefs and head cooks": ["Chefs and Head Cooks"],
    "Cooks, restaurant": ["Cooks, Restaurant"],
    "Food preparation workers": ["Food Preparation Workers"],
    "Waiters and waitresses": ["Waiters and Waitresses"],
    "Bartenders": ["Bartenders"],
    
    # Building and Grounds Cleaning and Maintenance
    "Janitors and cleaners, except maids and housekeeping cleaners": ["Janitors and Cleaners, Except Maids and Housekeeping Cleaners"],
    "Maids and housekeeping cleaners": ["Maids and Housekeeping Cleaners"],
    "Grounds maintenance workers": ["Grounds Maintenance Workers"],
    
    # Personal Care and Service Occupations
    "Hairdressers, hairstylists, and cosmetologists": ["Hairdressers, Hairstylists, and Cosmetologists"],
    "Childcare workers": ["Childcare Workers"],
    
    # Sales and Related Occupations
    "First-line supervisors of retail sales workers": ["First-Line Supervisors of Retail Sales Workers"],
    "Cashiers": ["Cashiers"],
    "Retail salespersons": ["Retail Salespersons"],
    "Insurance sales agents": ["Insurance Sales Agents"],
    "Securities, commodities, and financial services sales agents": ["Securities, Commodities, and Financial Services Sales Agents"],
    "Sales representatives, wholesale and manufacturing": ["Sales Representatives, Wholesale and Manufacturing, Technical and Scientific Products", "Sales Representatives, Wholesale and Manufacturing, Except Technical and Scientific Products"],
    "Real estate sales agents": ["Real Estate Sales Agents"],
    "Telemarketers": ["Telemarketers"],
    
    # Office and Administrative Support Occupations
    "First-line supervisors of office and administrative support workers": ["First-Line Supervisors of Office and Administrative Support Workers"],
    "Bookkeeping, accounting, and auditing clerks": ["Bookkeeping, Accounting, and Auditing Clerks"],
    "Customer service representatives": ["Customer Service Representatives"],
    "Receptionists and information clerks": ["Receptionists and Information Clerks"],
    "Secretaries and administrative assistants": ["Secretaries and Administrative Assistants", "Executive Secretaries and Executive Administrative Assistants"],
    "Data entry keyers": ["Data Entry Keyers"],
    "Office clerks, general": ["Office Clerks, General"],
    
    # Construction and Extraction Occupations
    "First-line supervisors of construction trades and extraction workers": ["First-Line Supervisors of Construction Trades and Extraction Workers"],
    "Carpenters": ["Carpenters"],
    "Construction laborers": ["Construction Laborers"],
    "Electricians": ["Electricians"],
    "Plumbers, pipefitters, and steamfitters": ["Plumbers, Pipefitters, and Steamfitters"],
    
    # Installation, Maintenance, and Repair Occupations
    "First-line supervisors of mechanics, installers, and repairers": ["First-Line Supervisors of Mechanics, Installers, and Repairers"],
    "Automotive service technicians and mechanics": ["Automotive Service Technicians and Mechanics"],
    "Industrial machinery mechanics": ["Industrial Machinery Mechanics"],
    "Maintenance and repair workers, general": ["Maintenance and Repair Workers, General"],
    
    # Production Occupations
    "First-line supervisors of production and operating workers": ["First-Line Supervisors of Production and Operating Workers"],
    "Assemblers and fabricators": ["Assemblers and Fabricators"],
    "Machinists": ["Machinists"],
    "Welders, cutters, solderers, and brazers": ["Welders, Cutters, Solderers, and Brazers"],
    "Inspectors, testers, sorters, samplers, and weighers": ["Inspectors, Testers, Sorters, Samplers, and Weighers"],
    
    # Transportation and Material Moving Occupations
    "Driver/sales workers": ["Driver/Sales Workers"],
    "Heavy and tractor-trailer truck drivers": ["Heavy and Tractor-Trailer Truck Drivers"],
    "Light truck or delivery services drivers": ["Light Truck or Delivery Services Drivers"],
    "Laborers and freight, stock, and material movers, hand": ["Laborers and Freight, Stock, and Material Movers, Hand"],
    "Packers and packagers, hand": ["Packers and Packagers, Hand"],
    "Stockers and order fillers": ["Stockers and Order Fillers"],
}


def create_reverse_mapping(mappings):
    """Create reverse mapping from SOC titles to panel occupation names."""
    reverse = {}
    for panel_name, soc_titles in mappings.items():
        for title in soc_titles:
            # Normalize title for matching
            normalized = title.lower().strip()
            reverse[normalized] = panel_name
    return reverse


def normalize_occupation_name(name):
    """Normalize occupation name for matching."""
    if pd.isna(name):
        return ""
    return str(name).lower().strip()


def match_on_soc_code(panel_df, scores_df):
    """Match scores to panel data using SOC codes (for 2015-2017)."""
    # Extract 7-character SOC code from Occupation_Code
    panel_df = panel_df.copy()
    panel_df['SOC_Code_Match'] = panel_df['Occupation_Code'].str[:7]
    
    # Create scores dict for matching
    scores_dict = {}
    for _, row in scores_df.iterrows():
        soc = row['SOC_Code']
        scores_dict[soc] = {
            'Teleworkable': row['Teleworkable'],
            'AutomationRisk_PreAI': row['AutomationRisk_PreAI']
        }
    
    # Map scores using SOC codes
    panel_df['Teleworkable'] = panel_df['SOC_Code_Match'].map(lambda x: scores_dict.get(x, {}).get('Teleworkable', np.nan))
    panel_df['AutomationRisk_PreAI'] = panel_df['SOC_Code_Match'].map(lambda x: scores_dict.get(x, {}).get('AutomationRisk_PreAI', np.nan))
    
    return panel_df


def match_on_occupation_name(panel_df, scores_df, reverse_mapping):
    """Match scores to panel data using occupation names (for 2018-2024)."""
    # Create normalized occupation name column
    panel_df['Occupation_Normalized'] = panel_df['Occupation'].apply(normalize_occupation_name)
    
    # Create SOC title to scores mapping
    scores_by_title = {}
    for _, row in scores_df.iterrows():
        title_normalized = normalize_occupation_name(row['Occupation_Title'])
        scores_by_title[title_normalized] = {
            'Teleworkable': row['Teleworkable'],
            'AutomationRisk_PreAI': row['AutomationRisk_PreAI']
        }
    
    # Try direct matching first
    def get_scores(occ_name):
        occ_normalized = normalize_occupation_name(occ_name)
        
        # Direct match
        if occ_normalized in scores_by_title:
            return pd.Series(scores_by_title[occ_normalized])
        
        # Try reverse mapping
        if occ_normalized in reverse_mapping:
            panel_name = reverse_mapping[occ_normalized]
            # Find in scores data
            if panel_name.lower() in scores_by_title:
                return pd.Series(scores_by_title[panel_name.lower()])
        
        # No match
        return pd.Series({'Teleworkable': np.nan, 'AutomationRisk_PreAI': np.nan})
    
    scores = panel_df['Occupation'].apply(get_scores)
    panel_df['Teleworkable'] = scores['Teleworkable']
    panel_df['AutomationRisk_PreAI'] = scores['AutomationRisk_PreAI']
    
    return panel_df


def main():
    """Main execution function."""
    print("=" * 80)
    print("MERGING OCCUPATION SCORES INTO PANEL DATA")
    print("=" * 80)
    print()
    
    # Load data
    print("Loading data files...")
    panel_df = pd.read_csv(PANEL_PATH)
    scores_df = pd.read_csv(SCORES_PATH)
    
    print(f"✓ Panel data: {len(panel_df):,} rows, {len(panel_df['Occupation'].unique())} unique occupations")
    print(f"✓ Scores data: {len(scores_df):,} SOC codes")
    print()
    
    # Create reverse mapping for occupation names
    reverse_mapping = create_reverse_mapping(OCCUPATION_NAME_MAPPINGS)
    
    # Identify year range for each matching strategy
    print("Splitting data by year...")
    panel_2015_2017 = panel_df[panel_df['Year'].isin([2015, 2016, 2017])].copy()
    panel_2018_2024 = panel_df[panel_df['Year'] >= 2018].copy()
    
    print(f"✓ 2015-2017 (SOC code matching): {len(panel_2015_2017):,} rows")
    print(f"✓ 2018-2024 (Name matching): {len(panel_2018_2024):,} rows")
    print()
    
    # Match 2015-2017 data on SOC codes
    print("=" * 80)
    print("Matching 2015-2017 data on SOC codes...")
    print("=" * 80)
    merged_2015_2017 = match_on_soc_code(panel_2015_2017, scores_df)
    
    telework_coverage_1517 = merged_2015_2017['Teleworkable'].notna().sum() / len(merged_2015_2017) * 100
    automation_coverage_1517 = merged_2015_2017['AutomationRisk_PreAI'].notna().sum() / len(merged_2015_2017) * 100
    
    print(f"✓ Teleworkable coverage: {telework_coverage_1517:.1f}%")
    print(f"✓ AutomationRisk_PreAI coverage: {automation_coverage_1517:.1f}%")
    print()
    
    # Match 2018-2024 data on occupation names
    print("=" * 80)
    print("Matching 2018-2024 data on occupation names...")
    print("=" * 80)
    merged_2018_2024 = match_on_occupation_name(panel_2018_2024, scores_df, reverse_mapping)
    
    telework_coverage_1824 = merged_2018_2024['Teleworkable'].notna().sum() / len(merged_2018_2024) * 100
    automation_coverage_1824 = merged_2018_2024['AutomationRisk_PreAI'].notna().sum() / len(merged_2018_2024) * 100
    
    print(f"✓ Teleworkable coverage: {telework_coverage_1824:.1f}%")
    print(f"✓ AutomationRisk_PreAI coverage: {automation_coverage_1824:.1f}%")
    print()
    
    # Combine data
    print("=" * 80)
    print("Combining matched data...")
    print("=" * 80)
    
    # Select columns to keep from merged data
    cols_to_keep = [col for col in panel_df.columns if col not in ['Teleworkable', 'AutomationRisk_PreAI']]
    
    # Add score columns from merged data
    merged_2015_2017_final = merged_2015_2017[cols_to_keep + ['Teleworkable', 'AutomationRisk_PreAI']]
    merged_2018_2024_final = merged_2018_2024[cols_to_keep + ['Teleworkable', 'AutomationRisk_PreAI']]
    
    # Combine
    final_panel = pd.concat([merged_2015_2017_final, merged_2018_2024_final], ignore_index=True)
    
    # Sort by year and occupation
    final_panel = final_panel.sort_values(['Year', 'Occupation'])
    
    # Overall coverage statistics
    telework_overall = final_panel['Teleworkable'].notna().sum() / len(final_panel) * 100
    automation_overall = final_panel['AutomationRisk_PreAI'].notna().sum() / len(final_panel) * 100
    
    print(f"✓ Final dataset: {len(final_panel):,} rows")
    print(f"✓ Overall Teleworkable coverage: {telework_overall:.1f}%")
    print(f"✓ Overall AutomationRisk_PreAI coverage: {automation_overall:.1f}%")
    print()
    
    # Save updated panel
    print("=" * 80)
    print("Saving updated occupation panel...")
    print("=" * 80)
    final_panel.to_csv(OUTPUT_PATH, index=False)
    print(f"✓ Saved to: {OUTPUT_PATH}")
    print()
    
    # Update metadata
    print("Updating metadata...")
    if METADATA_PATH.exists():
        with open(METADATA_PATH, 'r') as f:
            metadata = json.load(f)
    else:
        metadata = {}
    
    # Add score information
    metadata['scores_update'] = {
        'date': datetime.now().isoformat(),
        'teleworkable': {
            'source': 'Dingel & Neiman (2020)',
            'citation': 'Dingel, J. I., & Neiman, B. (2020). How many jobs can be done at home? Journal of Public Economics, 189, 104235.',
            'coverage_overall': f"{telework_overall:.1f}%",
            'coverage_2015_2017': f"{telework_coverage_1517:.1f}%",
            'coverage_2018_2024': f"{telework_coverage_1824:.1f}%",
            'description': 'Binary indicator (0/1) of whether occupation can be performed remotely'
        },
        'automation_risk_preai': {
            'source': 'Frey & Osborne (2017)',
            'citation': 'Frey, C. B., & Osborne, M. A. (2017). The future of employment: How susceptible are jobs to computerisation? Technological Forecasting and Social Change, 114, 254-280.',
            'coverage_overall': f"{automation_overall:.1f}%",
            'coverage_2015_2017': f"{automation_coverage_1517:.1f}%",
            'coverage_2018_2024': f"{automation_coverage_1824:.1f}%",
            'description': 'Probability (0-1) of occupation being automated by pre-AI technologies'
        }
    }
    
    with open(METADATA_PATH, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"✓ Updated metadata: {METADATA_PATH}")
    print()
    
    # Display sample with scores
    print("=" * 80)
    print("Sample Data (First 20 rows with scores)")
    print("=" * 80)
    sample = final_panel[final_panel['Teleworkable'].notna() | final_panel['AutomationRisk_PreAI'].notna()].head(20)
    print(sample[['Year', 'Occupation', 'Teleworkable', 'AutomationRisk_PreAI']].to_string())
    print()
    
    print("=" * 80)
    print("✓ MERGE COMPLETE")
    print("=" * 80)
    print()
    print("The occupation panel now includes:")
    print("  - Teleworkable: Remote work feasibility (Dingel & Neiman 2020)")
    print("  - AutomationRisk_PreAI: Pre-AI automation exposure (Frey & Osborne 2017)")
    print()


if __name__ == "__main__":
    main()
