import json
import re
from collections import defaultdict

REVISED_KEYWORD_LIST_V2 = [
    # Core AI Terms
    "artificial intelligence",
    "ai",
    "machine learning",
    "ml",
    "deep learning",
    "neural networks",
    "natural language processing",
    "nlp",
    "computer vision",
    "predictive analytics",
    "autonomous systems",
    "algorithmic",
    "cognitive computing",
    "reinforcement learning",
    "generative ai",
    "foundation models",
    "large language models",
    "llm",
    "transformers",
    "ai ethics",
    "explainable ai",
    "ai governance",
    "conversational ai",
    "robotic process automation",
    "rpa",
    "intelligent automation",
    "ai platforms",
    "mlops",
    "data science",
    "ai chips",
    "gpus",
    "npus",
    "accelerators",
    "edge computing",
    "neuromorphic computing",
    "quantum computing",
    "cloud computing",
    "cloud services",
    "cloud platforms",
    "cloud infrastructure",
    "cloud native",
    "data lakes",
    "data warehouses",
    "hybrid cloud",
    "multi-cloud",
    "feature engineering",
    "robotic surgery",
    "robo-advisors",
    "autonomous vehicles",
    "adas",
    "robotics",
    "digital twins",

    # Cloud Computing
    "aws",  # Amazon Web Services
    "azure", # Microsoft Azure
    "gcp",  # Google Cloud Platform
    "serverless",
    "kubernetes",
    "docker",

    # Data Engineering & Management (Related to Cloud and AI)
    "data pipelines",
    "etl",  # Extract, Transform, Load
    "data integration",
    "data governance", # Included before but worth emphasizing here
    "data management",

    # Cybersecurity (Increasingly Relevant for AI and Cloud)
    "ai security",
    "security of machine learning",
    "data security", # Included before but worth emphasizing here
    "cybersecurity",
    "threat detection ai",

    # Developer Tools & Frameworks (Often Used in AI)
    "tensorflow",
    "pytorch",
    "keras",
    "scikit-learn",
    "hugging face",
    "langchain",
    "vector databases",

    # Healthcare
    "drug discovery",
    "target identification",
    "clinical trials",
    "genomics",
    "ai-powered diagnostics",
    "precision medicine",
    "personalized medicine",
    "computational biology",
    "ai-enabled medical devices",
    "smart prosthetics",
    "medical imaging",
    "radiology",
    "pathology",
    "digital health",
    "patient monitoring",
    "telehealth",
    "hospital management",
    "claims processing healthcare",
    "chatbots patient support",
    "predictive analytics for disease",

    # Financials
    "fraud detection",
    "anomaly detection",
    "risk assessment",
    "credit risk modeling",
    "algorithmic trading",
    "regulatory compliance",
    "regtech",
    "chatbots customer service finance",
    "virtual assistants finance",
    "portfolio management",
    "market analysis finance",
    "sentiment analysis finance",
    "underwriting",
    "claims management insurance",
    "predictive modeling for insurance",

    # Consumer Discretionary
    "personalization e-commerce",
    "recommendation engines",
    "virtual try-on",
    "chatbots customer service retail",
    "supply chain optimization",
    "inventory management",
    "demand forecasting",
    "content recommendation",
    "game development",
    "personalized entertainment",
    "self-driving cars",
    "vehicle diagnostics",
    "manufacturing automotive",

    # Consumer Staples
    "supply chain optimization",
    "predictive maintenance",
    "quality control manufacturing",
    "demand forecasting",
    "personalized product recommendations",

    # Industrials
    "predictive maintenance",
    "quality control",
    "process optimization",
    "autonomous drones",
    "mission planning",
    "simulation and training aerospace",
    "route optimization",
    "autonomous vehicles transportation",

    # Energy
    "seismic data analysis",
    "predictive maintenance",
    "reservoir management",
    "energy grid management",
    "predicting energy demand",
    "optimizing wind turbines",
    "optimizing solar panels",

    # Materials
    "process optimization",
    "quality control",
    "supply chain optimization",
    "predictive maintenance",

    # Real Estate
    "predictive maintenance",
    "energy optimization buildings",
    "tenant experience",
    "property valuation",
    "real estate market analysis",

    # Utilities
    "smart grid optimization",
    "predicting energy demand",
    "outage prediction",
    "predictive maintenance utilities"
]

CORE_AI_TERMS = {
    "artificial intelligence",
    "ai",
    "machine learning",
    "ml",
    "deep learning",
    "neural networks",
    "natural language processing",
    "nlp",
    "computer vision",
    "predictive analytics",
    "autonomous systems",
    "algorithmic",
    "cognitive computing",
    "reinforcement learning",
    "generative ai",
    "foundation models",
    "large language models",
    "llm",
    "transformers",
    "ai ethics",
    "explainable ai",
    "ai governance",
    "conversational ai",
    "robotic process automation",
    "rpa",
    "intelligent automation",
    "ai platforms",
    "mlops",
    "data science",
    "ai chips",
    "gpus",
    "npus",
    "accelerators",
    "edge computing",
    "neuromorphic computing",
    "quantum computing",
    "cloud computing",
    "cloud services",
    "cloud platforms",
    "cloud infrastructure",
    "cloud native",
    "data lakes",
    "data warehouses",
    "hybrid cloud",
    "multi-cloud",
    "feature engineering",
    "robotic surgery",
    "robo-advisors",
    "autonomous vehicles",
    "adas",
    "robotics",
    "digital twins"
}

def contains_other_keyword(sentence, current_keyword, keywords_set):
    sentence_lower = sentence.lower()
    for kw in keywords_set:
        if kw == current_keyword:
            continue
        if re.search(r'\b' + re.escape(kw.lower()) + r'\b', sentence_lower):
            return True
    return False

def filter_sentences(companies, keywords, core_terms):
    results = []
    global_keyword_counts = defaultdict(lambda: {"before": 0, "after": 0})

    keywords_set = set(keywords)

    for company in companies:
        phrase_contexts = company.get('phrase_contexts', {})
        phrase_counts = company.get('phrase_counts', {})
        total_hits = company.get('total_hits', 0)
        ai_category = company.get('ai_readiness_category', "")

        company_keyword_counts = {}
        filtered_contexts = {}

        for kw, sentences in phrase_contexts.items():
            before_count = len(sentences)
            global_keyword_counts[kw]["before"] += before_count

            if kw in core_terms:
                filtered = sentences
            else:
                filtered = [
                    s for s in sentences
                    if contains_other_keyword(s, kw, keywords_set)
                ]

            after_count = len(filtered)
            global_keyword_counts[kw]["after"] += after_count

            company_keyword_counts[kw] = {
                "before": before_count,
                "after": after_count
            }
            filtered_contexts[kw] = filtered

        # Recalculate total_hits after filtering (sum of after counts)
        new_total_hits = sum(c['after'] for c in company_keyword_counts.values())

        results.append({
            'index': company.get('index'),
            'ticker': company.get('ticker'),
            'name': company.get('name'),
            'cik': company.get('cik'),
            'phrase_counts': company_keyword_counts,          # updated counts
            'phrase_contexts': filtered_contexts,             # filtered sentences
            'total_hits': new_total_hits,                      # updated total hits
            'ai_readiness_category': ai_category               # keep original category
        })

    return results, global_keyword_counts

def main():
    with open('keyword_context.json', 'r', encoding='utf-8') as f:
        companies = json.load(f)

    filtered_results, global_keyword_counts = filter_sentences(companies, REVISED_KEYWORD_LIST_V2, CORE_AI_TERMS)

    output = {
        "summary": {
            "global_keyword_counts": global_keyword_counts
        },
        "companies": filtered_results
    }

    with open('filtered_context.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)

    print(f"Filtered context saved to 'filtered_context.json'")

if __name__ == "__main__":
    main()
