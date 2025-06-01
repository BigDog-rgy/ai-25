import json

JSON_FILE = 'wiki.json'
OUTPUT_FILE = 'wikiMissing.json'

FIELDS_TO_CHECK = [
    'cik',
    'revenue',
    'operating_income',
    'net_income',
    'total_assets',
    'total_equity',
    'number_of_employees'
]

def is_missing(value):
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() == ''
    if isinstance(value, list):
        return len(value) == 0 or all(not s.strip() for s in value if isinstance(s, str))
    return False

def check_missing_fields(companies):
    missing_report = []

    for company in companies:
        missing_fields = []
        for field in FIELDS_TO_CHECK:
            val = company.get(field)
            if is_missing(val):
                missing_fields.append(field)
        if missing_fields:
            missing_report.append({
                'index': company.get('index'),
                'ticker': company.get('ticker'),
                'name': company.get('name'),
                'missing_fields': missing_fields
            })

    return missing_report

def main():
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        companies = json.load(f)

    report = check_missing_fields(companies)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    print(f"Missing fields report saved to {OUTPUT_FILE}. Found {len(report)} companies with missing data.")

if __name__ == "__main__":
    main()
