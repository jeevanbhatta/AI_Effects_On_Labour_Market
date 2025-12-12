import requests
import json
import csv
import os
import time

# Configuration
API_URL = 'https://api.bls.gov/publicAPI/v2/timeseries/data/'
START_YEAR = '2015'
END_YEAR = '2025'
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
DOCS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'docs')
BLS_API_KEY = os.environ.get('BLS_API_KEY')

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
            # JOLTS ID: JTS + Industry(6) + Region(2=00) + Size(2=00) + Metric(3)
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
    # We will fetch CES data for all states
    for state_code, state_name in STATES.items():
        for ind in INDUSTRIES:
            for met in METRICS_CES:
                # SMS + State(2) + Area(5=00000) + Industry(8) + Metric(2)
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

def save_metadata(series_def):
    metadata_path = os.path.join(DOCS_DIR, 'metadata.json')
    os.makedirs(DOCS_DIR, exist_ok=True)
    
    # Create a dictionary for easier lookup
    meta_dict = {item['id']: item for item in series_def}
    
    with open(metadata_path, 'w') as f:
        json.dump(meta_dict, f, indent=4)
    print(f"Metadata saved to {metadata_path}")
    return meta_dict

def process_data(json_data, meta_dict):
    rows = []
    if not json_data:
        return rows
        
    if json_data.get('status') != 'REQUEST_SUCCEEDED':
        print("API Request Failed:", json_data.get('message'))
        # Sometimes partial success returns REQUEST_SUCCEEDED but with errors in message?
        # BLS API returns status per series usually?
        # Actually, the top level status is for the request.
        # If we have partial errors, they might be in the series results.
    
    series_list = json_data.get('Results', {}).get('series', [])
    for series in series_list:
        series_id = series['seriesID']
        info = meta_dict.get(series_id, {})
        
        data_points = series.get('data', [])
        if not data_points:
            # print(f"No data for {series_id}")
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
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 1. Generate Series Definitions
    series_def = generate_series_def()
    meta_dict = save_metadata(series_def)
    
    # 2. Fetch Data in Batches
    all_rows = []
    ids_list = [item['id'] for item in series_def]
    
    # Batch size: 50 is the limit for registered users, 25 for unregistered.
    # To be safe and robust, we'll use 25 if no key, 50 if key.
    BATCH_SIZE = 50 if BLS_API_KEY else 25
    
    # If no key, we might hit daily limits very fast (25 series total per day?).
    # If the user doesn't have a key, fetching 700+ series will fail after the first batch.
    # We should probably warn or limit if no key.
    if not BLS_API_KEY:
        print("WARNING: No BLS_API_KEY found. Unregistered users have a daily limit of 25 series.")
        print("Fetching all states will likely fail or be incomplete.")
        # We will proceed, but maybe the user should know.
    
    for i in range(0, len(ids_list), BATCH_SIZE):
        batch_ids = ids_list[i:i + BATCH_SIZE]
        print(f"Processing batch {i // BATCH_SIZE + 1} / {(len(ids_list) + BATCH_SIZE - 1) // BATCH_SIZE}")
        
        result = fetch_bls_data(batch_ids, START_YEAR, END_YEAR)
        rows = process_data(result, meta_dict)
        all_rows.extend(rows)
        
        # Sleep to avoid hitting rate limits (e.g. requests per second)
        time.sleep(1) 
    
    # 3. Save to CSV
    if all_rows:
        # Sort: State (Total first), Industry, Metric, Year, Period
        # We want 'Total' to be at the top or bottom? Usually top.
        # We can sort by State, but 'Total' starts with T.
        # Let's use a custom sort key for state.
        
        def sort_key(x):
            state_rank = 0 if x['State'] == 'Total' else 1
            return (state_rank, x['State'], x['Industry'], x['Metric'], x['Year'], x['Period'])

        all_rows.sort(key=sort_key)
        
        output_file = os.path.join(OUTPUT_DIR, 'bls_employment_data.csv')
        keys = ['SeriesID', 'State', 'Industry', 'Metric', 'Source', 'Unit', 'Year', 'Period', 'PeriodName', 'Value', 'Footnotes']
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(all_rows)
        print(f"Saved {len(all_rows)} rows to {output_file}")
    else:
        print("No data to save.")

if __name__ == "__main__":
    main()
