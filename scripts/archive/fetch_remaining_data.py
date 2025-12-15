import requests
import json
import csv
import os
import time

# Load .env file manually to avoid dependencies
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                try:
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value.strip("'").strip('"')
                except ValueError:
                    pass # Skip lines that don't match key=value format

# Configuration (Same as fetch_bls_data.py)
API_URL = 'https://api.bls.gov/publicAPI/v2/timeseries/data/'
START_YEAR = '2015'
END_YEAR = '2025'
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
DOCS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'docs')
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

# Industries Configuration
INDUSTRIES = [
    {'ces_code': '00000000', 'jolts_code': '000000', 'name': 'Total Nonfarm', 'jolts_name': 'Total Nonfarm'},
    {'ces_code': '51000000', 'jolts_code': '510000', 'name': 'Information', 'jolts_name': 'Information'},
    {'ces_code': '60540000', 'jolts_code': '540000', 'name': 'Professional, Scientific, and Technical Services', 'jolts_name': 'Professional and Business Services'},
    {'ces_code': '55520000', 'jolts_code': '520000', 'name': 'Finance and Insurance', 'jolts_name': 'Finance and Insurance'},
    {'ces_code': '70000000', 'jolts_code': '700000', 'name': 'Leisure and Hospitality', 'jolts_name': 'Leisure and Hospitality'},
]

# Metrics Configuration
METRICS_CES = [
    {'code': '01', 'name': 'All Employees', 'unit': 'Thousands'},
    {'code': '02', 'name': 'Avg Weekly Hours', 'unit': 'Hours'},
    {'code': '03', 'name': 'Avg Hourly Earnings', 'unit': 'Dollars'}
]

METRICS_JOLTS = [
    {'code': 'JOL', 'name': 'Job Openings', 'unit': 'Level'},
    {'code': 'HIL', 'name': 'Hires', 'unit': 'Level'}
]

def generate_series_def():
    series_def = []
    
    # --- National Data ---
    for ind in INDUSTRIES:
        # CES National
        for met in METRICS_CES:
            series_id = f"CES{ind['ces_code']}{met['code']}"
            series_def.append({
                'id': series_id,
                'industry': ind['name'],
                'metric': met['name'],
                'source': 'CES',
                'unit': met['unit'],
                'state': 'Total'
            })
        
        # JOLTS National
        for met in METRICS_JOLTS:
            series_id = f"JTS{ind['jolts_code']}00000000{met['code']}"
            series_def.append({
                'id': series_id,
                'industry': ind['jolts_name'],
                'metric': met['name'],
                'source': 'JOLTS',
                'unit': met['unit'],
                'state': 'Total'
            })

    # --- State Data ---
    for state_code, state_name in STATES.items():
        for ind in INDUSTRIES:
            for met in METRICS_CES:
                series_id = f"SMS{state_code}00000{ind['ces_code']}{met['code']}"
                series_def.append({
                    'id': series_id,
                    'industry': ind['name'],
                    'metric': met['name'],
                    'source': 'CES',
                    'unit': met['unit'],
                    'state': state_name
                })
    
    return series_def

def get_existing_series_ids(filepath):
    existing_ids = set()
    if not os.path.exists(filepath):
        return existing_ids
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('SeriesID'):
                    existing_ids.add(row['SeriesID'])
    except Exception as e:
        print(f"Error reading existing file: {e}")
    
    return existing_ids

def fetch_bls_data(series_ids, start_year, end_year):
    headers = {'Content-type': 'application/json'}
    payload = {
        "seriesid": series_ids,
        "startyear": start_year,
        "endyear": end_year
    }
    
    if BLS_API_KEY:
        payload["registrationkey"] = BLS_API_KEY

    data = json.dumps(payload)

    print(f"Requesting data for {len(series_ids)} series...")
    try:
        response = requests.post(API_URL, data=data, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error: {e}")
        return None

def process_data(json_data, meta_dict):
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
    print(f"Checking existing data in {EXISTING_DATA_FILE}...")
    existing_ids = get_existing_series_ids(EXISTING_DATA_FILE)
    print(f"Found {len(existing_ids)} existing series.")

    series_def = generate_series_def()
    meta_dict = {item['id']: item for item in series_def}
    
    # Identify missing series
    all_ids = [item['id'] for item in series_def]
    missing_ids = [sid for sid in all_ids if sid not in existing_ids]
    
    print(f"Total series defined: {len(all_ids)}")
    print(f"Missing series to fetch: {len(missing_ids)}")
    
    if not missing_ids:
        print("All data already fetched!")
        return

    # Batching
    BATCH_SIZE = 50 if BLS_API_KEY else 25
    if not BLS_API_KEY:
        print("WARNING: No BLS_API_KEY found. Rate limits may apply.")

    new_rows = []
    
    for i in range(0, len(missing_ids), BATCH_SIZE):
        batch_ids = missing_ids[i:i + BATCH_SIZE]
        print(f"Processing batch {i // BATCH_SIZE + 1} / {(len(missing_ids) + BATCH_SIZE - 1) // BATCH_SIZE}")
        
        result = fetch_bls_data(batch_ids, START_YEAR, END_YEAR)
        rows = process_data(result, meta_dict)
        new_rows.extend(rows)
        
        # Append immediately to file to save progress
        if rows:
            file_exists = os.path.exists(EXISTING_DATA_FILE)
            keys = ['SeriesID', 'State', 'Industry', 'Metric', 'Source', 'Unit', 'Year', 'Period', 'PeriodName', 'Value', 'Footnotes']
            
            with open(EXISTING_DATA_FILE, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                # If file didn't exist (unlikely here), write header
                if not file_exists:
                    writer.writeheader()
                writer.writerows(rows)
            print(f"  Appended {len(rows)} rows to {EXISTING_DATA_FILE}")
        
        time.sleep(1)

    print("Done fetching missing data.")

if __name__ == "__main__":
    main()
