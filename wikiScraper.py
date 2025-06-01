import requests
from bs4 import BeautifulSoup
import json
import time
import random
import re


BASE_WIKI = 'https://en.wikipedia.org'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/114.0.0.0 Safari/537.36',
}

def extract_money_text(td):
    spans = td.find_all('span')
    money_text = None

    # Find first span starting with 'US$'
    for span in spans:
        text = span.get_text(strip=True)
        if text.startswith('US$'):
            money_text = text
            break

    # Append tail text after the last span inside td, if any
    if spans:
        last_span = spans[-1]
        tail_text = ''
        sibling = last_span.next_sibling
        while sibling:
            if isinstance(sibling, str):
                tail_text += sibling.strip()
            sibling = sibling.next_sibling

        if tail_text:
            money_text = (money_text or '') + ' ' + tail_text
            money_text = money_text.strip()

    return money_text or td.get_text(strip=True)

def clean_money_string(money_str):
    if not money_str:
        return None

    money_str = re.sub(r'\([^)]*\)', '', money_str)
    money_str = money_str.replace('\u00a0', ' ').strip()

    pattern = r'US\$\s*([\d.,]+)\s*(billion|million|thousand)?'
    match = re.search(pattern, money_str, re.IGNORECASE)

    if not match:
        return None

    number_str = match.group(1).replace(',', '')
    scale_word = match.group(2).lower() if match.group(2) else ''

    try:
        number = float(number_str)
    except ValueError:
        return None

    scale_factors = {
        'billion': 1e9,
        'million': 1e6,
        'thousand': 1e3,
        '': 1
    }

    multiplier = scale_factors.get(scale_word, 1)
    return number * multiplier

def scrape_financials(wiki_path):
    try:
        full_url = BASE_WIKI + wiki_path
        resp = requests.get(full_url, headers=headers)
        if resp.status_code != 200:
            print(f"Failed to fetch wiki page {full_url}: {resp.status_code}")
            return None
        soup = BeautifulSoup(resp.text, 'html.parser')
        tbody = soup.find('tbody')
        if not tbody:
            print(f"No tbody on wiki page {full_url}")
            return None

        rows = tbody.find_all('tr')

        financial_keys = [
            'revenue',
            'operating income',
            'net income',
            'total assets',
            'total equity',
            'number of employees'
        ]

        results = {key: None for key in financial_keys}
        results['subsidiaries'] = []

        revenue_row_idx = None
        for idx, tr in enumerate(rows):
            th = tr.find('th')
            if th and 'revenue' in th.text.lower():
                revenue_row_idx = idx
                break
        if revenue_row_idx is None:
            print(f"No revenue row found on wiki page {full_url}")
            return results

        for key in financial_keys:
            for idx in range(revenue_row_idx, len(rows)):
                tr = rows[idx]
                th = tr.find('th')
                if th and key in th.text.lower():
                    td = tr.find('td')
                    if td:
                        val = extract_money_text(td)
                        cleaned_val = clean_money_string(val)
                        results[key] = cleaned_val if cleaned_val is not None else val
                    break

        # Subsidiaries extraction (unchanged)
        for idx in range(revenue_row_idx, len(rows)):
            tr = rows[idx]
            th = tr.find('th')
            if th and 'subsidiaries' in th.text.lower():
                td = tr.find('td')
                if td:
                    div = td.find('div', class_='plainlist')
                    if not div:
                        divs = td.find_all('div')
                        div = None
                        for d in divs:
                            classes = d.get('class', [])
                            if any('collapsible-list' in c for c in classes):
                                div = d
                                break
                    if div:
                        if 'collapsible-list' in ' '.join(div.get('class', [])):
                            children = list(div.children)
                            ul = None
                            for child in children:
                                if child.name == 'ul':
                                    ul = child
                                    break
                                if child.name == 'div':
                                    ul = child.find('ul')
                                    if ul:
                                        break
                        else:
                            ul = div.find('ul')

                        if ul:
                            lis = ul.find_all('li')
                            for li in lis:
                                a_tag = li.find('a')
                                if a_tag:
                                    results['subsidiaries'].append(a_tag.text.strip())
                                else:
                                    results['subsidiaries'].append(li.text.strip())
                    break

        return results

    except Exception as e:
        print(f"Error scraping wiki {wiki_path}: {e}")
        return None

def scrape_company_description(wiki_path):
    try:
        full_url = BASE_WIKI + wiki_path
        resp = requests.get(full_url, headers=headers)
        if resp.status_code != 200:
            print(f"Failed to fetch wiki page {full_url}: {resp.status_code}")
            return None
        soup = BeautifulSoup(resp.text, 'html.parser')
        toc_anchor = soup.find('meta', {'property': 'mw:PageProp/toc'})
        if toc_anchor:
            description_paragraphs = []
            sibling = toc_anchor.find_previous_sibling()
            while sibling:
                if sibling.name == 'p':
                    description_paragraphs.append(sibling.get_text(strip=True))
                sibling = sibling.find_previous_sibling()
            return "\n".join(reversed(description_paragraphs)).strip()
        else:
            print(f"TOC anchor not found on {full_url}")
            # Fallback to getting the first paragraph if TOC is not found
            first_paragraph = soup.find('div', {'id': 'mw-content-text'}).find('div', class_='mw-parser-output').find('p')
            return first_paragraph.get_text(strip=True) if first_paragraph else None
    except Exception as e:
        print(f"Error scraping description for {wiki_path}: {e}")
        return None

url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'

response = requests.get(url, headers=headers)
if response.status_code != 200:
    print(f"Failed to fetch page: status {response.status_code}")
    exit(1)

soup = BeautifulSoup(response.text, 'html.parser')
tbody = soup.find('tbody')
if not tbody:
    print("No tbody found on main page!")
    exit(1)

companies_data = []
missing_description_companies = []
rows = tbody.find_all('tr')

for i, row in enumerate(rows[1:505], start=1): # Limit to first 10 companies
    tds = row.find_all('td')
    if len(tds) >= 8:
        ticker = tds[0].find('a').text.strip() if tds[0].find('a') else tds[0].text.strip()
        name_tag = tds[1].find('a')
        name = name_tag.text.strip() if name_tag else tds[1].text.strip()
        wiki_link = name_tag['href'] if name_tag and name_tag.has_attr('href') else None

        gics_sector = tds[2].text.strip()
        gics_sub_industry = tds[3].text.strip()
        hq_location = tds[4].text.strip()
        cik = tds[6].text.strip()
        founded = tds[7].text.strip()

        financials = scrape_financials(wiki_link) if wiki_link else {}
        if financials is None:
            financials = {}

        description = scrape_company_description(wiki_link) if wiki_link else None

        # Check for missing or short description
        if not description or len(description) < 50:
            missing_description_companies.append(name)

        # Polite delay between requests
        time.sleep(0.25 + random.uniform(0, 0.8))

        companies_data.append({
            'index': i,
            'ticker': ticker,
            'name': name,
            'wiki_link': BASE_WIKI + wiki_link if wiki_link else None,
            'gics_sector': gics_sector,
            'gics_sub_industry': gics_sub_industry,
            'hq_location': hq_location,
            'cik': cik,
            'founded': founded,
            'revenue': financials.get('revenue'),
            'operating_income': financials.get('operating income'),
            'net_income': financials.get('net income'),
            'total_assets': financials.get('total assets'),
            'total_equity': financials.get('total equity'),
            'number_of_employees': financials.get('number of employees'),
            'subsidiaries': financials.get('subsidiaries', []),
            'description': description
        })
    else:
        print(f"Row {i} missing expected columns")

output_data = {
    'companies_with_missing_or_short_description': missing_description_companies,
    'companies_data': companies_data
}

with open('wiki_expansion.json', 'w', encoding='utf-8') as f:
    json.dump(output_data, f, indent=2)

print(f"Saved data for first 10 companies with financial and description data to wiki_expansion.json")
print(f"Companies with missing or short descriptions: {missing_description_companies}")