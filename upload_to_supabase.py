#!/usr/bin/env python3
# scripts/upload_to_supabase.py

import json, os
from supabase import create_client
from dotenv import load_dotenv
from collections import Counter
import re

load_dotenv()

SUPA_URL = os.environ["NEXT_PUBLIC_SUPABASE_URL"]
SUPA_KEY = os.environ["NEXT_PUBLIC_SUPABASE_ANON_KEY"]
supabase = create_client(SUPA_URL, SUPA_KEY)

# Load parsed reports
reports = json.load(open("./parsed/companyReports.json"))

def normalize_company_name(name: str) -> str:
    return re.sub(r'\W+', '', name).strip().lower()  # remove punctuation and lowercase

latest = {}
raw_name_map = {}  # maps normalized name → real name
for r in reports:
    raw = r.get("company", "")
    norm = normalize_company_name(raw)
    if not norm:
        print("⚠️ Skipping row with empty or bad company name:", r)
        continue
    latest[norm] = r
    raw_name_map[norm] = raw  # save original for logging

deduped = list(latest.values())

# Log what got deduped
dupes = [raw_name_map[n] for n, count in Counter(
    normalize_company_name(r.get("company", "")) for r in reports
).items() if count > 1]

if dupes:
    print(f"⚠️ Resolved {len(dupes)} company name conflicts: {dupes}")


# 🚀 Upload
resp = supabase.table("company_ai_readiness") \
    .upsert(deduped, on_conflict="company") \
    .execute()

print(f"✅ Inserted or updated {len(resp.data)} unique rows.")
