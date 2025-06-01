import json
import requests
from bs4 import BeautifulSoup
import re
import time
import nltk

# Configure NLTK data path
nltk.data.path.append(r'C:\Users\cvrol\AppData\Roaming\nltk_data')
# nltk.download('punkt_tab')  # Uncomment if needed
from nltk.tokenize import sent_tokenize

# Configuration
HEADERS = {
    'User-Agent': 'YourName cvrolson@gmail.com',
}

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

    # Cloud Computing
    "cloud computing",
    "cloud services",
    "cloud platforms",
    "aws",  # Amazon Web Services
    "azure", # Microsoft Azure
    "gcp",  # Google Cloud Platform
    "cloud infrastructure",
    "serverless",
    "kubernetes",
    "docker",
    "cloud native",
    "data lakes",
    "data warehouses",
    "hybrid cloud",
    "multi-cloud",

    # Data Engineering & Management (Related to Cloud and AI)
    "data pipelines",
    "etl",  # Extract, Transform, Load
    "data integration",
    "data governance", # Included before but worth emphasizing here
    "data management",
    "feature engineering",

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
    "robotic surgery",
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
    "robo-advisors",
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
    "autonomous vehicles",
    "self-driving cars",
    "adas",
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
    "robotics",
    "digital twins",
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

def extract_contexts(text, phrases, window=50):
    """
    For each phrase, find occurrences and get the full sentence containing the phrase.
    Returns dict: phrase -> list of context sentences (original case preserved)
    """
    contexts = {}
    sentences = sent_tokenize(text)
    text_lower = text.lower()
    
    # Create regex patterns for each phrase
    phrase_patterns = {
        phrase: re.compile(r'\b' + re.escape(phrase.lower()) + r'\b') 
        for phrase in phrases
    }

    for phrase, pattern in phrase_patterns.items():
        matched_sentences = []
        
        for sentence in sentences:
            if pattern.search(sentence.lower()):
                matched_sentences.append(sentence.strip())
        
        if matched_sentences:
            contexts[phrase] = matched_sentences
    
    return contexts

def remove_duplicate_contexts(contexts_dict):
    """
    Remove duplicate sentences within each phrase's context list.
    Also removes duplicate sentences across all phrases globally.
    """
    all_seen_sentences = set()
    cleaned_contexts = {}
    
    for phrase, sentences in contexts_dict.items():
        unique_sentences = []
        
        for sentence in sentences:
            # Normalize sentence for comparison (strip whitespace, convert to lowercase)
            normalized = sentence.strip().lower()
            
            if normalized not in all_seen_sentences and normalized:
                unique_sentences.append(sentence.strip())  # Keep original case
                all_seen_sentences.add(normalized)
        
        if unique_sentences:  # Only include phrases that have contexts after deduplication
            cleaned_contexts[phrase] = unique_sentences
    
    return cleaned_contexts

def categorize_ai_readiness(total_hits):
    """Categorize companies based on AI keyword frequency."""
    if total_hits == 0:
        return "nothing"
    elif 1 <= total_hits <= 4:
        return "culled"
    elif 5 <= total_hits <= 50:
        return "middle of pack"
    else:
        return "crushing it"

def get_latest_10k_html(cik, start_date='2025-01-01', end_date='2025-05-22'):
    """Fetch the latest 10-K filing HTML for a given CIK within date range."""
    cik_padded = cik.zfill(10)
    submissions_url = f"https://data.sec.gov/submissions/CIK{cik_padded}.json"
    
    try:
        resp = requests.get(submissions_url, headers=HEADERS)
        if resp.status_code != 200:
            print(f"Failed to get submissions JSON for CIK {cik}: HTTP {resp.status_code}")
            return None

        data = resp.json()
        filings = data.get('filings', {}).get('recent', {})
        forms = filings.get('form', [])
        accession_numbers = filings.get('accessionNumber', [])
        filing_dates = filings.get('filingDate', [])
        primary_docs = filings.get('primaryDocument', [])

        # Look for 10-K filings in date range
        for form, acc_num, fdate, prim_doc in zip(forms, accession_numbers, filing_dates, primary_docs):
            if form == "10-K" and start_date <= fdate <= end_date:
                acc_no_nodash = acc_num.replace('-', '')
                filing_base_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc_no_nodash}/"
                filing_url = filing_base_url + prim_doc

                filing_resp = requests.get(filing_url, headers=HEADERS)
                if filing_resp.status_code != 200:
                    print(f"Failed to download filing HTML for CIK {cik}: HTTP {filing_resp.status_code}")
                    return None

                return filing_resp.text

        print(f"No 10-K filing found in date range {start_date} to {end_date} for CIK {cik}.")
        return None

    except Exception as e:
        print(f"Exception for CIK {cik}: {e}")
        return None

def fetch_with_fallback(cik):
    """Try to fetch 10-K with current year, fallback to extended date range."""
    result = get_latest_10k_html(cik, start_date='2025-01-01', end_date='2025-05-22')
    if result is None:
        print(f"Retrying with extended date range for CIK {cik}")
        result = get_latest_10k_html(cik, start_date='2024-01-01', end_date='2025-05-22')
    return result

def extract_text_from_html(html):
    """Extract and clean text from HTML, removing noise elements."""
    soup = BeautifulSoup(html, 'html.parser')

    # Remove noisy elements
    for elem in soup(['script', 'style', 'table', 'noscript']):
        elem.decompose()

    text = soup.get_text(separator=' ', strip=True)
    return text  # Keep original case for context extraction

def count_phrases(text, phrases):
    """Count occurrences of each phrase in text (case-insensitive)."""
    text_lower = text.lower()
    counts = {}
    
    for phrase in phrases:
        pattern = r'\b' + re.escape(phrase.lower()) + r'\b'
        matches = re.findall(pattern, text_lower)
        if matches:
            counts[phrase] = len(matches)
    
    return counts

def analyze_text_for_phrases(text):
    """Main analysis function that counts phrases and extracts contexts."""
    phrase_counts = count_phrases(text, REVISED_KEYWORD_LIST_V2)
    total_hits = sum(phrase_counts.values())
    
    # Extract contexts for phrases that had hits
    phrases_with_hits = list(phrase_counts.keys())
    phrase_contexts = extract_contexts(text, phrases_with_hits)
    
    # Remove duplicate contexts (this is the key fix)
    phrase_contexts = remove_duplicate_contexts(phrase_contexts)

    return {
        "phrase_counts": phrase_counts,
        "phrase_contexts": phrase_contexts,
        "total_hits": total_hits,
        "category": categorize_ai_readiness(total_hits)
    }

def main():
    """Main processing function."""
    # Load company data
    with open('wiki.json', 'r', encoding='utf-8') as f:
        companies = json.load(f)

    results = []
    missing_reports = []

    # Process companies (currently limited to first 5)
    for idx, company in enumerate(companies, 1):
        cik = company.get('cik')
        ticker = company.get('ticker')
        name = company.get('name')

        # Skip companies without CIK
        if not cik:
            print(f"[{idx}] Skipping {name} ({ticker}) due to missing CIK")
            missing_reports.append({
                'ticker': ticker,
                'name': name,
                'cik': cik,
                'reason': 'Missing CIK'
            })
            continue

        print(f"[{idx}] Fetching 10-K for {name} ({ticker}), CIK {cik}")
        
        # Fetch 10-K HTML
        html = fetch_with_fallback(cik)
        if html is None:
            print(f"[{idx}] No 10-K found or failed download for {name} ({ticker})")
            missing_reports.append({
                'ticker': ticker,
                'name': name,
                'cik': cik,
                'reason': 'No 10-K found or download failed'
            })
            continue

        # Extract and analyze text
        text = extract_text_from_html(html)
        analysis_results = analyze_text_for_phrases(text)

        # Store results
        results.append({
            'index': idx,
            'ticker': ticker,
            'name': name,
            'cik': cik,
            'phrase_counts': analysis_results['phrase_counts'],
            'phrase_contexts': analysis_results['phrase_contexts'],
            'total_hits': analysis_results['total_hits'],
            'ai_readiness_category': analysis_results['category']
        })

        # Be polite to SEC servers
        time.sleep(1)

    # Save results
    with open('keyword_context.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

    with open('missing_reports.json', 'w', encoding='utf-8') as f:
        json.dump(missing_reports, f, indent=2)

    print(f"Processed {len(results)} companies, {len(missing_reports)} missing or failed.")

if __name__ == "__main__":
    main()