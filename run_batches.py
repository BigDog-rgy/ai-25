import os, json, time
from pathlib import Path   
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# -------- CONFIG ---------
BATCH_SIZE     = 4      # or 25 when ready
MAX_BATCHES    = 126
PAUSE_AFTER    = 2      # send 2 batches, then pause
SLEEP_SECONDS  = 60     # 60-second cooldown
# -------------------------

# ----- load data ----------
companies    = json.load(open("batch_input.json", "r", encoding="utf-8"))
instructions = open("rubric.txt", "r", encoding="utf-8").read()

def build_batch_prompt(instr, comps, first_batch=False):
    header = instr if first_batch else "Same rubric as previous batch."
    body   = ""
    for idx, c in enumerate(comps, 1):
        body += (
            f"\n### Company {idx}: {c['name']}\n"
            f"10-K Report Excerpts:\n{c['combined_10k']}\n"
            f"Supplementary Company Information:\n{c['wiki_context']}\n"
        )
    body += (
        "\nPlease respond for each company separately, labeling each response clearly with the company name."
    )
    return f"{header}\n\n## Companies to Evaluate ({len(comps)}):\n{body}"

def batch_companies(items, size):
    for i in range(0, len(items), size):
        yield items[i : i + size]

for batch_num, batch in enumerate(batch_companies(companies, BATCH_SIZE), 1):
    if batch_num > MAX_BATCHES:
        break

    # ------------- build prompt -------------
    prompt = build_batch_prompt(
        instructions, batch, first_batch=(batch_num == 1)
    )

    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant expert in analyzing AI readiness of "
                "companies based on annual reports and supplementary information."
            ),
        },
        {"role": "user", "content": prompt},
    ]

    # ------------- API call -----------------
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=750 * len(batch),
        temperature=0.3,
    )

    # ------------- save ---------------------
    Path(f"batch_result_{batch_num:03}.txt").write_text(
        response.choices[0].message.content, encoding="utf-8"
    )
    print(f"✅ Batch {batch_num} done ({len(batch)} companies)")

    # ------------- cooldown every N batches -
    if batch_num % PAUSE_AFTER == 0 and batch_num < MAX_BATCHES:
        print(f"Sleeping {SLEEP_SECONDS}s to avoid throttling…")
        time.sleep(SLEEP_SECONDS)
