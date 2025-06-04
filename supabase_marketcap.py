from supabase import create_client, Client
import json

url = "https://lpnkmxmbsjbodncylfpk.supabase.co"  # <-- fill this in
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxwbmtteG1ic2pib2RuY3lsZnBrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDc3OTEyMzYsImV4cCI6MjA2MzM2NzIzNn0.nYxGzSwO2aKPG5ufEUfeX7Fh2m8aW3dkYAQNgFCBQhk"                         # <-- fill this in

supabase: Client = create_client(url, key)

with open('marketcap.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

success = 0
failures = []

def parse_market_cap(mc):
    if mc.endswith("B"):
        return float(mc[:-1]) * 1_000_000_000
    if mc.endswith("M"):
        return float(mc[:-1]) * 1_000_000
    return float(mc)

for entry in data:
    name = entry['name']                     # <-- Correct! inside the loop
    market_cap_str = entry['market_cap']
    # market_cap = parse_market_cap(market_cap_str)  # Uncomment if numeric column
    market_cap = market_cap_str               # Use as string if text column

    response = supabase.table("company_ai_readiness") \
        .update({"market_cap": market_cap}) \
        .eq("company", name) \
        .execute()

    if getattr(response, "status_code", None) == 200 and getattr(response, "data", None):
        print(f"Updated '{name}' with market cap {market_cap}")
        success += 1
    else:
        print(f"Failed to update '{name}': {getattr(response, 'data', response)}")
        failures.append(name)

print(f"\nUpdated {success} companies. {len(failures)} failures.")
if failures:
    print("The following names did not match any company in the DB:")
    for name in failures:
        print("  -", name)