import json

# -- Update with your actual data files --
RAW_COMPANY_DATA = "filtered_context.json"     # Or your actual data source
WIKI_DATA_FILE = "wiki_expansion.json"

BATCH_READY_FILE = "batch_input.json"
COMPANY_CAP = 5000  # cap for 10-K context

def combine_contexts(phrase_contexts, char_cap=COMPANY_CAP):
    texts = []
    for phrase, sentences in phrase_contexts.items():
        texts.append(f"Keyword: {phrase}")
        texts.extend(sentences)
    full_text = "\n".join(texts)
    if len(full_text) > char_cap:
        return full_text[:char_cap] + "\n... [TRUNCATED AT 5,000 CHARS]"
    return full_text

DESC_CAP = 1000
SUBS_CAP = 1000

def cap_description(desc):
    return desc[:DESC_CAP] if isinstance(desc, str) else ""

def cap_subs_descriptions_and_names(subs):
    used = 0
    capped_subs = []
    if not isinstance(subs, list):
        return capped_subs
    for sub in subs:
        sub_name = sub.get("name", "")
        wiki_link = sub.get("wiki_link", "")
        desc = sub.get("description", "")
        desc_len = len(desc) if isinstance(desc, str) else 0

        if used < SUBS_CAP:
            remaining = SUBS_CAP - used
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
    return capped_subs

def format_wiki_context(wiki_info):
    if not wiki_info:
        return "No supplementary information available."

    context_parts = []

    # Cap and add company description
    capped_desc = cap_description(wiki_info.get('description', ''))
    if capped_desc:
        context_parts.append(f"Company Description: {capped_desc}")

    if wiki_info.get('gics_sector'):
        context_parts.append(f"Industry Sector: {wiki_info['gics_sector']}")

    if wiki_info.get('gics_sub_industry'):
        context_parts.append(f"Sub-Industry: {wiki_info['gics_sub_industry']}")

    if wiki_info.get('founded'):
        context_parts.append(f"Founded: {wiki_info['founded']}")

    if wiki_info.get('hq_location'):
        context_parts.append(f"Headquarters: {wiki_info['hq_location']}")

    financial_info = []
    num_employees = wiki_info.get("number_of_employees")
    if num_employees:
        financial_info.append(f"Employees: {num_employees}")

    if financial_info:
        context_parts.append("Financial Profile: " + ", ".join(financial_info))


    # Cap subsidiaries descriptions, but list all names
    capped_subs = cap_subs_descriptions_and_names(wiki_info.get('subsidiaries', []))
    if capped_subs:
        # Always list all subsidiary names; include description only if present
        subs_lines = []
        for sub in capped_subs:
            sub_line = f"- {sub['name']}"
            if sub.get('wiki_link'):
                sub_line += f" ({sub['wiki_link']})"
            if sub.get('description'):
                sub_line += f": {sub['description']}"
            subs_lines.append(sub_line)
        context_parts.append("Key Subsidiaries:\n" + "\n".join(subs_lines[:10]))  # Show up to 10

    return "\n".join(context_parts)

def find_wiki_data_for_company(wiki_data, ticker):
    for company in wiki_data:
        if company.get('ticker', '').upper() == ticker.upper():
            return company
    return None

def main():
    # Load raw data
    with open(RAW_COMPANY_DATA, 'r', encoding='utf-8') as f:
        filtered_data = json.load(f)
    with open(WIKI_DATA_FILE, 'r', encoding='utf-8') as f:
        wiki_file_data = json.load(f)
    wiki_companies = wiki_file_data.get("companies_data", wiki_file_data)  # adapt to your structure

    # If your filtered_data is like: {"companies": [...]}
    companies = filtered_data["companies"]

    out_list = []

    for company in companies:
        phrase_contexts = company.get("phrase_contexts", {})
        combined_10k = combine_contexts(phrase_contexts, char_cap=COMPANY_CAP)
        name = company.get("name", "Unknown")
        ticker = company.get("ticker", "")

        wiki_info = find_wiki_data_for_company(wiki_companies, ticker)
        wiki_context = format_wiki_context(wiki_info) if wiki_info else ""

        out_list.append({
            "name": name,
            "combined_10k": combined_10k,
            "wiki_context": wiki_context
        })

    # Just grab the first 10 for your first test run
    out_list = out_list[:505]

    with open(BATCH_READY_FILE, "w", encoding="utf-8") as f:
        json.dump(out_list, f, indent=2)

    print(f"Wrote {len(out_list)} companies to {BATCH_READY_FILE}")

if __name__ == "__main__":
    main()
