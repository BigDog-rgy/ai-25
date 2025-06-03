import json

INPUT_FILE = "wiki_expansion.json"
OUTPUT_FILE = "wiki_expansion_report.json"

def char_count(text):
    return len(text) if isinstance(text, str) else 0

def count_subs_chars(subs):
    if not isinstance(subs, list):
        return 0
    return sum(char_count(sub.get("description", "")) for sub in subs if isinstance(sub, dict))

def main():
    # Load input
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    companies = data.get("companies_data", [])

    results = []
    for company in companies:
        name = company.get("name", "[NO NAME]")
        desc = company.get("description", "")
        subs = company.get("subsidiaries", [])

        desc_chars = char_count(desc)
        subs_chars = count_subs_chars(subs)
        # Total chars: description + all subsidiary descriptions
        total_chars = desc_chars + subs_chars

        results.append({
            "name": name,
            "total_chars": total_chars,
            "description_chars": desc_chars,
            "subsidiaries_chars": subs_chars
        })

    # Sort descending by total_chars
    results.sort(key=lambda x: x["total_chars"], reverse=True)

    # Save to output file
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"Report generated! {len(results)} companies written to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
