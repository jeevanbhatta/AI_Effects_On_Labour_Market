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

# Define Series with Metadata
# We will use this to generate the request and the metadata documentation
SERIES_DEF = [
    # --- Total Nonfarm ---
    {'id': 'CES0000000001', 'industry': 'Total Nonfarm', 'metric': 'All Employees', 'source': 'CES', 'unit': 'Thousands'},
    {'id': 'CES0000000002', 'industry': 'Total Nonfarm', 'metric': 'Avg Weekly Hours', 'source': 'CES', 'unit': 'Hours'},
    {'id': 'CES0000000003', 'industry': 'Total Nonfarm', 'metric': 'Avg Hourly Earnings', 'source': 'CES', 'unit': 'Dollars'},
    {'id': 'JTS000000000000000JOL', 'industry': 'Total Nonfarm', 'metric': 'Job Openings', 'source': 'JOLTS', 'unit': 'Level'},
    {'id': 'JTS000000000000000HIL', 'industry': 'Total Nonfarm', 'metric': 'Hires', 'source': 'JOLTS', 'unit': 'Level'},

    # --- Information (High AI Exposure) ---
    {'id': 'CES5100000001', 'industry': 'Information', 'metric': 'All Employees', 'source': 'CES', 'unit': 'Thousands'},
    {'id': 'CES5100000002', 'industry': 'Information', 'metric': 'Avg Weekly Hours', 'source': 'CES', 'unit': 'Hours'},
    {'id': 'CES5100000003', 'industry': 'Information', 'metric': 'Avg Hourly Earnings', 'source': 'CES', 'unit': 'Dollars'},
    {'id': 'JTS510000000000000JOL', 'industry': 'Information', 'metric': 'Job Openings', 'source': 'JOLTS', 'unit': 'Level'},
    {'id': 'JTS510000000000000HIL', 'industry': 'Information', 'metric': 'Hires', 'source': 'JOLTS', 'unit': 'Level'},

    # --- Professional, Scientific, and Technical Services (High AI Exposure) ---
    {'id': 'CES6054000001', 'industry': 'Professional, Scientific, and Technical Services', 'metric': 'All Employees', 'source': 'CES', 'unit': 'Thousands'},
    {'id': 'CES6054000002', 'industry': 'Professional, Scientific, and Technical Services', 'metric': 'Avg Weekly Hours', 'source': 'CES', 'unit': 'Hours'},
    {'id': 'CES6054000003', 'industry': 'Professional, Scientific, and Technical Services', 'metric': 'Avg Hourly Earnings', 'source': 'CES', 'unit': 'Dollars'},
    {'id': 'JTS540000000000000JOL', 'industry': 'Professional and Business Services', 'metric': 'Job Openings', 'source': 'JOLTS', 'unit': 'Level'}, # Note: JOLTS often aggregates to Prof & Bus Services or specific sectors. 54 is Prof/Sci/Tech
    {'id': 'JTS540000000000000HIL', 'industry': 'Professional and Business Services', 'metric': 'Hires', 'source': 'JOLTS', 'unit': 'Level'},

    # --- Finance and Insurance (High AI Exposure) ---
    {'id': 'CES5552000001', 'industry': 'Finance and Insurance', 'metric': 'All Employees', 'source': 'CES', 'unit': 'Thousands'},
    {'id': 'CES5552000002', 'industry': 'Finance and Insurance', 'metric': 'Avg Weekly Hours', 'source': 'CES', 'unit': 'Hours'},
    {'id': 'CES5552000003', 'industry': 'Finance and Insurance', 'metric': 'Avg Hourly Earnings', 'source': 'CES', 'unit': 'Dollars'},
    {'id': 'JTS520000000000000JOL', 'industry': 'Finance and Insurance', 'metric': 'Job Openings', 'source': 'JOLTS', 'unit': 'Level'},
    {'id': 'JTS520000000000000HIL', 'industry': 'Finance and Insurance', 'metric': 'Hires', 'source': 'JOLTS', 'unit': 'Level'},

    # --- Leisure and Hospitality (Control / Low AI Exposure) ---
    {'id': 'CES7000000001', 'industry': 'Leisure and Hospitality', 'metric': 'All Employees', 'source': 'CES', 'unit': 'Thousands'},
    {'id': 'CES7000000002', 'industry': 'Leisure and Hospitality', 'metric': 'Avg Weekly Hours', 'source': 'CES', 'unit': 'Hours'},
    {'id': 'CES7000000003', 'industry': 'Leisure and Hospitality', 'metric': 'Avg Hourly Earnings', 'source': 'CES', 'unit': 'Dollars'},
    {'id': 'JTS700000000000000JOL', 'industry': 'Leisure and Hospitality', 'metric': 'Job Openings', 'source': 'JOLTS', 'unit': 'Level'},
    {'id': 'JTS700000000000000HIL', 'industry': 'Leisure and Hospitality', 'metric': 'Hires', 'source': 'JOLTS', 'unit': 'Level'},
]

def fetch_bls_data(series_ids, start_year, end_year):
    headers = {'Content-type': 'application/json'}
    data = json.dumps({
        "seriesid": series_ids,
        "startyear": start_year,
        "endyear": end_year
    })

    print(f"Requesting data for {len(series_ids)} series...")
    try:
        response = requests.post(API_URL, data=data, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error: {e}")
        return None

def save_metadata():
    metadata_path = os.path.join(DOCS_DIR, 'metadata.json')
    os.makedirs(DOCS_DIR, exist_ok=True)
    
    # Create a dictionary for easier lookup
    meta_dict = {item['id']: item for item in SERIES_DEF}
    
    with open(metadata_path, 'w') as f:
        json.dump(meta_dict, f, indent=4)
    print(f"Metadata saved to {metadata_path}")
    return meta_dict

def process_data(json_data, meta_dict):
    rows = []
    if not json_data or json_data.get('status') != 'REQUEST_SUCCEEDED':
        print("API Request Failed:", json_data.get('message'))
        return rows

    series_list = json_data.get('Results', {}).get('series', [])
    for series in series_list:
        series_id = series['seriesID']
        info = meta_dict.get(series_id, {})
        
        for item in series.get('data', []):
            rows.append({
                'SeriesID': series_id,
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
    
    # 1. Save Metadata
    meta_dict = save_metadata()
    
    # 2. Fetch Data
    # Extract just the IDs list
    ids_list = [item['id'] for item in SERIES_DEF]
    
    # BLS limits (check if we need batching, currently 20 < 25 so one batch is fine)
    result = fetch_bls_data(ids_list, START_YEAR, END_YEAR)
    
    # 3. Process and Save
    rows = process_data(result, meta_dict)
    
    if rows:
        rows.sort(key=lambda x: (x['Industry'], x['Metric'], x['Year'], x['Period']))
        
        output_file = os.path.join(OUTPUT_DIR, 'bls_employment_data.csv')
        keys = ['SeriesID', 'Industry', 'Metric', 'Source', 'Unit', 'Year', 'Period', 'PeriodName', 'Value', 'Footnotes']
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(rows)
        print(f"Saved {len(rows)} rows to {output_file}")
    else:
        print("No data to save.")

if __name__ == "__main__":
    main()
