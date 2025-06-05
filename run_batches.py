import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

BATCH_SIZE   = 10   # we want 25 companies per chunk
MAX_BATCHES  = 2    

# Load data
with open("batch_input.json", "r", encoding="utf-8") as f:
    companies = json.load(f)
with open("rubric.txt", "r", encoding="utf-8") as f:
    instructions = f.read()

def build_batch_prompt(instructions, companies):
    prompt = (
        instructions
        + f"\n\n## Companies to Evaluate ({len(companies)} companies):\n"
        + "For EACH company, respond with a SEPARATE, clearly labeled report, following the required format below.\n"
        + "Do NOT skip or combine companies. Each section must begin with 'Company: [Company Name]'.\n"
    )
    for idx, company in enumerate(companies, 1):
        prompt += f"\n### Company {idx}: {company['name']}\n"
        prompt += f"10-K Report Excerpts:\n{company['combined_10k']}\n"
        prompt += f"Supplementary Company Information:\n{company['wiki_context']}\n"
    prompt += (
        "\nPlease respond for each company separately, labeling each response clearly with the company name."
    )
    return prompt

def batch_companies(companies, batch_size=BATCH_SIZE):
    for i in range(0, len(companies), batch_size):
        yield companies[i:i + batch_size]

for batch_num, batch in enumerate(batch_companies(companies, BATCH_SIZE), 1):
    if batch_num > MAX_BATCHES:
        break
    print(f"Processing batch {batch_num} with {len(batch)} companies...")
    user_prompt = build_batch_prompt(instructions, batch)
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant expert in analyzing AI readiness of companies based on annual reports and supplementary company information."
        },
        {
            "role": "user",
            "content": user_prompt
        }
    ]
    response = client.chat.completions.create(
        model="gpt-4o",  # or "gpt-4-turbo"
        messages=messages,
        max_tokens=750 * len(batch),  # room for output; tune as needed
        temperature=0.3,
    )
    result_text = response.choices[0].message.content

    # Save each batch result to its own file for review
    with open(f"batch_result_{batch_num:03}.txt", "w", encoding="utf-8") as out_f:
        out_f.write(result_text)

    print(f"Batch {batch_num} complete! Results saved to batch_result_{batch_num:03}.txt")
