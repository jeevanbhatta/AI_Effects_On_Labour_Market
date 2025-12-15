"""
Fetch Information Industry Data

The Information industry (NAICS 51) data was missing from the initial fetch.
This script fetches it specifically.

BLS Series ID format for State data (SMS):
SMS + State(2) + Area(5=00000 for statewide) + Industry(8) + DataType(2)

Information industry code: 51000000
"""

import requests
import json
import csv
import os
import time

# Load .env file
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                try:
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value.strip("'").strip('"')
                except ValueError:
                    pass

# Configuration
API_URL = 'https://api.bls.gov/publicAPI/v2/timeseries/data/'
START_YEAR = '2015'
END_YEAR = '2025'
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
BLS_API_KEY = os.environ.get('BLS_API_KEY')
EXISTING_DATA_FILE = os.path.join(OUTPUT_DIR, 'bls_employment_data.csv')

# State Codes (FIPS)
STATES = {
    '01': 'Alabama', '02': 'Alaska', '04': 'Arizona', '05': 'Arkansas', '06': 'California',
    '08': 'Colorado', '09': 'Connecticut', '10': 'Delaware', '11': 'District of Columbia',
    '12': 'Florida', '13': 'Georgia', '15': 'Hawaii', '16': 'Idaho', '17': 'Illinois',
    '18': 'Indiana', '19': 'Iowa', '20': 'Kansas', '21': 'Kentucky', '22': 'Louisiana',
    '23': 'Maine', '24': 'Maryland', '25': 'Massachusetts', '26': 'Michigan', '27': 'Minnesota',
    '28': 'Mississippi', '29': 'Missouri', '30': 'Montana', '31': 'Nebraska', '32': 'Nevada',
    '33': 'New Hampshire', '34': 'New Jersey', '35': 'New Mexico', '36': 'New York',
    '37': 'North Carolina', '38': 'North Dakota', '39': 'Ohio', '40': 'Oklahoma', '41': 'Oregon',
    '42': 'Pennsylvania', '44': 'Rhode Island', '45': 'South Carolina', '46': 'South Dakota',
    '47': 'Tennessee', '48': 'Texas', '49': 'Utah', '50': 'Vermont', '51': 'Virginia',
    '53': 'Washington', '54': 'West Virginia', '55': 'Wisconsin', '56': 'Wyoming'
}

# Information industry config
# Note: BLS uses supersector code 50 for Information in CES/SMS series
# (different from NAICS 51)
INFORMATION_INDUSTRY = {
    'ces_code': '50000000',  # CES supersector code for Information
    'jolts_code': '510000',
    'name': 'Information',
    'jolts_name': 'Information'
}

METRICS_CES = [
    {'code': '01', 'name': 'All Employees', 'unit': 'Thousands'},
]

def generate_information_series():
    """Generate series definitions for Information industry."""
    series_def = []
    
    # National CES data
    series_id = f"CES{INFORMATION_INDUSTRY['ces_code']}01"
    series_def.append({
        'id': series_id,
        'industry': INFORMATION_INDUSTRY['name'],
        'metric': 'All Employees',
        'source': 'CES',
        'unit': 'Thousands',
        'state': 'Total'
    })
    
    # National JOLTS data
    for metric_code, metric_name in [('JOL', 'Job Openings'), ('HIL', 'Hires')]:
        series_id = f"JTS{INFORMATION_INDUSTRY['jolts_code']}00000000{metric_code}"
        series_def.append({
            'id': series_id,
            'industry': INFORMATION_INDUSTRY['jolts_name'],
            'metric': metric_name,
            'source': 'JOLTS',
            'unit': 'Level',
            'state': 'Total'
        })
    
    # State-level CES data
    for state_code, state_name in STATES.items():
        series_id = f"SMS{state_code}00000{INFORMATION_INDUSTRY['ces_code']}01"
        series_def.append({
            'id': series_id,
            'industry': INFORMATION_INDUSTRY['name'],
            'metric': 'All Employees',
            'source': 'CES',
            'unit': 'Thousands',
            'state': state_name
        })
    
    return series_def


def fetch_bls_data(series_ids, start_year, end_year):
    """Fetch data from BLS API."""
    headers = {'Content-type': 'application/json'}
    payload = {
        "seriesid": series_ids,
        "startyear": start_year,
        "endyear": end_year
    }
    
    if BLS_API_KEY:
        payload["registrationkey"] = BLS_API_KEY

    print(f"Requesting data for {len(series_ids)} series...")
    try:
        response = requests.post(API_URL, data=json.dumps(payload), headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error: {e}")
        return None


def process_data(json_data, meta_dict):
    """Process API response into rows."""
    rows = []
    if not json_data:
        return rows
        
    if json_data.get('status') != 'REQUEST_SUCCEEDED':
        print("API Request Failed:", json_data.get('message'))
    
    series_list = json_data.get('Results', {}).get('series', [])
    for series in series_list:
        series_id = series['seriesID']
        info = meta_dict.get(series_id, {})
        
        data_points = series.get('data', [])
        if not data_points:
            continue

        for item in data_points:
            rows.append({
                'SeriesID': series_id,
                'State': info.get('state', 'Unknown'),
                'Industry': info.get('industry', 'Unknown'),
                'Metric': info.get('metric', 'Unknown'),
                'Source': info.get('source', 'Unknown'),
                'Unit': info.get('unit', 'Unknown'),
                'Year': item['year'],
                'Period': item['period'],
                'PeriodName': item['periodName'],
                'Value': item['value'],
                'Footnotes': "; ".join([f.get('text', '') for f in item.get('footnotes', []) if f])
            })
    return rows


def main():
    if not BLS_API_KEY:
        print("WARNING: No BLS_API_KEY found. Rate limits will apply.")
    else:
        print(f"Using BLS API Key: {BLS_API_KEY[:8]}...")

    # Generate series definitions
    series_def = generate_information_series()
    meta_dict = {item['id']: item for item in series_def}
    
    print(f"Total series to fetch: {len(series_def)}")
    
    # Fetch in batches
    all_rows = []
    ids_list = [item['id'] for item in series_def]
    BATCH_SIZE = 50 if BLS_API_KEY else 25
    
    for i in range(0, len(ids_list), BATCH_SIZE):
        batch_ids = ids_list[i:i + BATCH_SIZE]
        print(f"Processing batch {i // BATCH_SIZE + 1} / {(len(ids_list) + BATCH_SIZE - 1) // BATCH_SIZE}")
        
        result = fetch_bls_data(batch_ids, START_YEAR, END_YEAR)
        rows = process_data(result, meta_dict)
        all_rows.extend(rows)
        
        time.sleep(1)
    
    print(f"\nFetched {len(all_rows)} rows for Information industry")
    
    if all_rows:
        # Append to existing data file
        keys = ['SeriesID', 'State', 'Industry', 'Metric', 'Source', 'Unit', 'Year', 'Period', 'PeriodName', 'Value', 'Footnotes']
        
        with open(EXISTING_DATA_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writerows(all_rows)
        
        print(f"✓ Appended {len(all_rows)} rows to {EXISTING_DATA_FILE}")
    else:
        print("No data fetched.")


if __name__ == "__main__":
    main()
