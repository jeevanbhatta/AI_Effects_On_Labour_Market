"""
Fetch State-Level Economic Controls from BLS
=============================================

This script fetches time-varying state-level control variables from the 
BLS Local Area Unemployment Statistics (LAUS) API:

1. State Unemployment Rate
2. State Labor Force Participation Rate (calculated)
3. State Labor Force
4. State Civilian Noninstitutional Population

These controls are essential for the DiD analysis to account for 
state-level economic conditions that may correlate with AI adoption.

Data Source: BLS Local Area Unemployment Statistics (LAUS)
Time Period: January 2015 - September 2025
Geographic Coverage: 50 states + DC + National (52 units)

Author: SS154 Final Project
Date: December 2025
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime
import requests
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
BLS_API_KEY = os.getenv('BLS_API_KEY')

# BLS API Configuration
BLS_API_URL = 'https://api.bls.gov/publicAPI/v2/timeseries/data/'
START_YEAR = '2015'
END_YEAR = '2025'

# State FIPS codes (alphabetical order)
STATE_FIPS = {
    'Alabama': '01', 'Alaska': '02', 'Arizona': '04', 'Arkansas': '05',
    'California': '06', 'Colorado': '08', 'Connecticut': '09', 'Delaware': '10',
    'District of Columbia': '11', 'Florida': '12', 'Georgia': '13', 'Hawaii': '15',
    'Idaho': '16', 'Illinois': '17', 'Indiana': '18', 'Iowa': '19',
    'Kansas': '20', 'Kentucky': '21', 'Louisiana': '22', 'Maine': '23',
    'Maryland': '24', 'Massachusetts': '25', 'Michigan': '26', 'Minnesota': '27',
    'Mississippi': '28', 'Missouri': '29', 'Montana': '30', 'Nebraska': '31',
    'Nevada': '32', 'New Hampshire': '33', 'New Jersey': '34', 'New Mexico': '35',
    'New York': '36', 'North Carolina': '37', 'North Dakota': '38', 'Ohio': '39',
    'Oklahoma': '40', 'Oregon': '41', 'Pennsylvania': '42', 'Rhode Island': '44',
    'South Carolina': '45', 'South Dakota': '46', 'Tennessee': '47', 'Texas': '48',
    'Utah': '49', 'Vermont': '50', 'Virginia': '51', 'Washington': '53',
    'West Virginia': '54', 'Wisconsin': '55', 'Wyoming': '56',
    'Total': '00'  # National level
}

# LAUS Series ID suffixes
SERIES_SUFFIXES = {
    'unemployment_rate': '03',      # Unemployment rate (%)
    'labor_force': '06',             # Labor force (thousands)
    'employment': '05',              # Employment (thousands)
    'population': '00'               # Civilian noninstitutional population (thousands)
}


def build_series_ids():
    """
    Build BLS LAUS series IDs for all states and variables.
    
    Series ID format: LASST[FIPS][0000000000][SUFFIX]
    Example: LASST060000000003 = California unemployment rate
    Note: Must have exactly 10 zeros between FIPS and suffix
    
    Returns:
        dict: Mapping of (state, variable) to series ID
    """
    series_ids = {}
    
    for state, fips in STATE_FIPS.items():
        for var_name, suffix in SERIES_SUFFIXES.items():
            series_id = f"LASST{fips}00000000000{suffix}"  # 11 zeros
            series_ids[(state, var_name)] = series_id
    
    return series_ids


def fetch_bls_data(series_ids, api_key=None):
    """
    Fetch data from BLS API for given series IDs.
    
    Args:
        series_ids (list): List of BLS series IDs
        api_key (str): BLS API key (optional, but recommended)
    
    Returns:
        dict: Mapping of series ID to list of data points
    """
    headers = {'Content-type': 'application/json'}
    payload = {
        'seriesid': series_ids,
        'startyear': START_YEAR,
        'endyear': END_YEAR
    }
    
    if api_key:
        payload['registrationkey'] = api_key
    
    try:
        response = requests.post(BLS_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if data['status'] != 'REQUEST_SUCCEEDED':
            print(f"API Error: {data.get('message', 'Unknown error')}")
            return None
        
        results = {}
        for series in data['Results']['series']:
            series_id = series['seriesID']
            results[series_id] = series['data']
        
        return results
        
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None


def fetch_all_states():
    """
    Fetch state-level control variables for all states.
    Handles API rate limits by batching requests.
    
    Returns:
        pd.DataFrame: Panel data with state-level controls
    """
    series_mapping = build_series_ids()
    all_series_ids = list(series_mapping.values())
    
    print(f"Total series to fetch: {len(all_series_ids)}")
    print(f"Using API key: {'Yes' if BLS_API_KEY else 'No'}")
    
    # Batch size (BLS API limit: 50 series per request with key, 25 without)
    batch_size = 50 if BLS_API_KEY else 25
    
    all_data = []
    
    # Process in batches
    for i in range(0, len(all_series_ids), batch_size):
        batch = all_series_ids[i:i+batch_size]
        batch_num = i // batch_size + 1
        total_batches = (len(all_series_ids) + batch_size - 1) // batch_size
        
        print(f"\nFetching batch {batch_num}/{total_batches} ({len(batch)} series)...")
        
        results = fetch_bls_data(batch, BLS_API_KEY)
        
        if results is None:
            print(f"Failed to fetch batch {batch_num}")
            continue
        
        # Parse results
        for (state, var_name), series_id in series_mapping.items():
            if series_id not in results:
                continue
            
            data_points = results[series_id]
            if len(data_points) == 0:
                continue
            
            for datapoint in data_points:
                year = int(datapoint['year'])
                period = datapoint['period']
                
                # Skip annual averages and quarterly data
                if not period.startswith('M'):
                    continue
                
                month = int(period[1:])
                value = datapoint.get('value')
                
                if value in [None, '', '-']:
                    continue
                
                try:
                    value = float(value)
                except:
                    continue
                
                # Create date
                date = pd.Timestamp(year=year, month=month, day=1)
                
                all_data.append({
                    'Date': date,
                    'Year': year,
                    'Month': month,
                    'State': state,
                    'Variable': var_name,
                    'Value': value,
                    'SeriesID': series_id
                })
        
        parsed_count = len([sid for (s, v), sid in series_mapping.items() if sid in results and len(results[sid]) > 0])
        print(f"  Parsed {parsed_count} series with data from this batch")
        
        # Rate limiting
        if i + batch_size < len(all_series_ids):
            wait_time = 2 if BLS_API_KEY else 5
            print(f"  Waiting {wait_time} seconds before next request...")
            time.sleep(wait_time)
    
    # Convert to DataFrame
    df = pd.DataFrame(all_data)
    
    if df.empty:
        print("ERROR: No data retrieved!")
        return df
    
    print(f"\nTotal records retrieved: {len(df)}")
    
    return df


def reshape_and_calculate(df):
    """
    Reshape data from long to wide format and calculate derived variables.
    
    Args:
        df (pd.DataFrame): Long-format data
    
    Returns:
        pd.DataFrame: Wide-format with calculated variables
    """
    # Pivot to wide format
    df_wide = df.pivot_table(
        index=['Date', 'Year', 'Month', 'State'],
        columns='Variable',
        values='Value',
        aggfunc='first'
    ).reset_index()
    
    print(f"Available variables after pivot: {df_wide.columns.tolist()}")
    
    # Calculate Labor Force Participation Rate if population data is available
    if 'population' in df_wide.columns and 'labor_force' in df_wide.columns:
        df_wide['lfpr'] = (df_wide['labor_force'] / df_wide['population']) * 100
        has_lfpr = True
    else:
        print("WARNING: Population data not available, cannot calculate LFPR")
        has_lfpr = False
    
    # Rename columns for clarity
    rename_dict = {
        'unemployment_rate': 'UnemploymentRate',
        'labor_force': 'LaborForce',
        'employment': 'Employment_LAUS',  # Distinguish from CES employment
    }
    
    if 'population' in df_wide.columns:
        rename_dict['population'] = 'CivilianPopulation'
    if has_lfpr:
        rename_dict['lfpr'] = 'LFPR'
        
    df_wide = df_wide.rename(columns=rename_dict)
    
    # Select final columns (only those that exist)
    final_cols = ['Date', 'Year', 'Month', 'State']
    for col in ['UnemploymentRate', 'LFPR', 'LaborForce', 'Employment_LAUS', 'CivilianPopulation']:
        if col in df_wide.columns:
            final_cols.append(col)
    
    df_wide = df_wide[final_cols]
    
    # Sort by date and state
    df_wide = df_wide.sort_values(['Date', 'State']).reset_index(drop=True)
    
    return df_wide


def main():
    """Main execution function."""
    print("="*70)
    print("BLS State-Level Controls Data Fetch")
    print("="*70)
    print(f"Start Date: {START_YEAR}-01")
    print(f"End Date: {END_YEAR}-09")
    print(f"Geographic Units: {len(STATE_FIPS)} (50 states + DC + national)")
    print("="*70)
    
    # Fetch data
    df_long = fetch_all_states()
    
    if df_long.empty:
        print("\nNo data retrieved. Exiting.")
        sys.exit(1)
    
    # Reshape and calculate
    print("\nReshaping data and calculating derived variables...")
    df_wide = reshape_and_calculate(df_long)
    
    # Summary statistics
    print("\n" + "="*70)
    print("DATA SUMMARY")
    print("="*70)
    print(f"Date Range: {df_wide['Date'].min()} to {df_wide['Date'].max()}")
    print(f"States: {df_wide['State'].nunique()}")
    print(f"Total Observations: {len(df_wide)}")
    print(f"\nVariables: {[col for col in df_wide.columns if col not in ['Date', 'Year', 'Month', 'State']]}")
    
    print("\nSample statistics:")
    desc_cols = [col for col in ['UnemploymentRate', 'LaborForce', 'Employment_LAUS'] if col in df_wide.columns]
    print(df_wide[desc_cols].describe())
    
    # Check for missing values
    print("\nMissing values:")
    print(df_wide.isnull().sum())
    
    # Save to CSV
    output_path = Path(__file__).parent.parent / 'data' / 'state_controls.csv'
    df_wide.to_csv(output_path, index=False)
    print(f"\nData saved to: {output_path}")
    print(f"File size: {output_path.stat().st_size / 1024:.1f} KB")
    
    # Save metadata
    metadata = {
        'source': 'BLS Local Area Unemployment Statistics (LAUS)',
        'series_ids_sample': list(build_series_ids().values())[:5],
        'fetch_date': datetime.now().isoformat(),
        'start_period': f"{START_YEAR}-01",
        'end_period': f"{END_YEAR}-09",
        'n_states': df_wide['State'].nunique(),
        'n_observations': len(df_wide),
        'variables': {
            'UnemploymentRate': 'State unemployment rate (%)',
            'LFPR': 'Labor force participation rate (%) = (Labor Force / Population) * 100',
            'LaborForce': 'State labor force (thousands)',
            'Employment_LAUS': 'State employment from LAUS (thousands)',
            'CivilianPopulation': 'Civilian noninstitutional population 16+ (thousands)'
        }
    }
    
    metadata_path = Path(__file__).parent.parent / 'data' / 'state_controls_metadata.json'
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"Metadata saved to: {metadata_path}")
    
    print("\n" + "="*70)
    print("FETCH COMPLETE")
    print("="*70)


if __name__ == '__main__':
    main()
