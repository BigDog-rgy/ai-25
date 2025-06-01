import json
from collections import defaultdict

def analyze_contexts(companies):
    report = []
    keyword_sentence_totals = defaultdict(int)

    for company in companies:
        phrase_contexts = company.get('phrase_contexts', {})
        total_sentences = 0
        total_characters = 0

        for keyword, sentences in phrase_contexts.items():
            count = len(sentences)
            total_sentences += count
            total_characters += sum(len(s) for s in sentences)
            keyword_sentence_totals[keyword] += count

        report.append({
            "company": company.get('name', 'Unknown'),
            "ticker": company.get('ticker'),
            "total_sentences": total_sentences,
            "total_characters": total_characters
        })

    # Sort descending by total_characters for company report
    report.sort(key=lambda x: x['total_characters'], reverse=True)

    total_keyword_sentences = sum(keyword_sentence_totals.values())

    # Convert keyword totals to list of dicts sorted by descending count,
    # and add percentage of total sentences
    keyword_report = []
    for kw, count in sorted(keyword_sentence_totals.items(), key=lambda x: x[1], reverse=True):
        pct = (count / total_keyword_sentences) * 100 if total_keyword_sentences > 0 else 0
        keyword_report.append({
            "keyword": kw,
            "total_sentences": count,
            "percent_of_total_sentences": round(pct, 2)
        })

    return report, keyword_report, total_keyword_sentences

def main():
    with open('keyword_context.json', 'r', encoding='utf-8') as f:
        companies = json.load(f)

    context_report, keyword_report, total_keyword_sentences = analyze_contexts(companies)

    with open('context_report.json', 'w', encoding='utf-8') as f:
        json.dump(context_report, f, indent=2)

    # Save keyword report with total count as metadata
    output = {
        "total_keyword_sentences": total_keyword_sentences,
        "keywords": keyword_report
    }
    with open('keyword_sentence_report.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)

    print(f"Context report generated for {len(companies)} companies in 'context_report.json'.")
    print(f"Keyword sentence report generated in 'keyword_sentence_report.json' with total {total_keyword_sentences} sentences.")

if __name__ == "__main__":
    main()
