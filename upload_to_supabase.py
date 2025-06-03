# scripts/upload_to_supabase.py
import json, os
from supabase import create_client
from dotenv import load_dotenv
load_dotenv()             # pulls key/value lines from .env into os.environ

SUPA_URL = os.environ["NEXT_PUBLIC_SUPABASE_URL"]
SUPA_KEY = os.environ["NEXT_PUBLIC_SUPABASE_ANON_KEY"]
supabase = create_client(SUPA_URL, SUPA_KEY)


reports = json.load(open("./parsed/companyReports.json"))

# scrub keys that aren’t in the table, if any
payload = [
    {k: v for k, v in r.items()
        if k in (
           "company","sector","industry",
           "dim1","dim2","dim3","dim4","dim5",
           "overall","evidence","evidence_dim1","evidence_dim2",
           "evidence_dim3","evidence_dim4","evidence_dim5",
           "strategic","context","confidence")}
    for r in reports
]

# upsert on company name
resp = supabase.table("company_ai_readiness") \
        .upsert(payload, on_conflict="company") \
        .execute()

print("inserted / updated rows:", len(resp.data))
