import json

INPUT_FILE = "wiki_expansion.json"
OUTPUT_FILE = "wiki_expansion_report_capped_full_subs.json"
DESC_CAP = 1000
SUBS_CAP = 1000

def char_count(text):
    return len(text) if isinstance(text, str) else 0

def cap_description(desc):
    return desc[:DESC_CAP] if isinstance(desc, str) else ""

def cap_subs_descriptions_and_names(subs):
    used = 0
    capped_subs = []
    if not isinstance(subs, list):
        return capped_subs, 0
    for sub in subs:
        sub_name = sub.get("name", "")
        wiki_link = sub.get("wiki_link", "")
        desc = sub.get("description", "")
        desc_len = char_count(desc)

        if used < SUBS_CAP:
            remaining = SUBS_CAP - used
            # If there's still room for some or all of the description
            if desc_len <= remaining:
                capped_desc = desc
                used += desc_len
            else:
                capped_desc = desc[:remaining]
                used += remaining
        else:
            capped_desc = ""

        capped_subs.append({
            "name": sub_name,
            "wiki_link": wiki_link,
            "description": capped_desc
        })
    return capped_subs, used

def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    companies = data.get("companies_data", [])

    results = []
    for company in companies:
        name = company.get("name", "[NO NAME]")
        desc = company.get("description", "")
        subs = company.get("subsidiaries", [])

        capped_desc = cap_description(desc)
        desc_chars = char_count(capped_desc)

        capped_subs, subs_chars = cap_subs_descriptions_and_names(subs)
        total_chars = desc_chars + subs_chars

        results.append({
            "name": name,
            "total_chars": total_chars,
            "description_chars": desc_chars,
            "subsidiaries_chars": subs_chars,
            "capped_description": capped_desc,
            "capped_subsidiaries": capped_subs
        })

    # Sort as before
    results.sort(key=lambda x: x["total_chars"], reverse=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"Capped full-subsidiary report generated! {len(results)} companies written to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
