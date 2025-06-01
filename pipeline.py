import json
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()  # loads variables from .env into environment

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

PROMPT_TEMPLATE = """
# AI-Readiness Scorecard for S&P 500 Annual Report Analysis

Analyze the following 10-K report and rate the company's AI readiness based on the scorecard defined below. Provide a score (1-5) for each dimension and an overall weighted average score.

## Scoring Instructions

- **Be specific and provide EVIDENCE**: For **every** score you assign to each dimension, you **must** explicitly cite the exact phrases, sentences, or specific sections from the provided 10-K report excerpts that directly support your rating. If no direct evidence is found, state that clearly.
- **Look for concrete initiatives and investments**: Prioritize ratings based on mentions of specific AI projects, financial commitments to AI, established data science teams, concrete examples of AI applications, and measurable outcomes. Avoid being swayed by general or aspirational statements.
- **Consider the comprehensiveness and strategic importance**: Evaluate the scale and ambition of the company's AI-related activities. A score of 5 should represent a truly leading position where AI is deeply integrated and a core competitive advantage.
- **Utilize the full 1-5 scale with clear differentiation**: Do not cluster scores in the middle. A rating of 3 indicates a developing stage. Ratings of 1 and 2 should be reserved for minimal or emerging efforts, while 4 and 5 signify advanced and leading positions, respectively. Justify why a company deserves a particular score, especially at the extremes (1 or 5).

---

## **Dimension 1: AI Strategy and Vision (Weighting: 35%)**

**What to look for:** Explicit mentions of artificial intelligence, machine learning, automation (with AI context), algorithmic decision-making, intelligent systems, generative AI, AI transformation initiatives, and the strategic role of AI in the company's future.

- **Rating 1 (Minimal):** No or negligible mention of AI, ML, or intelligent automation as a strategic element. Digital transformation discussion, if any, focuses on basic digitization or outdated systems. **Provide evidence if this rating is given.**
- **Rating 2 (Emerging):** Very few, scattered references to AI/ML or automation without a discernible strategic framework. May include vague statements like "exploring AI opportunities" without any specific details or commitments. **Quote the emerging references if this rating is given.**
- **Rating 3 (Developing):** Clear acknowledgment of AI as a strategically important area, with some specific examples of pilot programs, initial implementations, or stated intentions. Integration may be limited to a few business units or functions. **Cite the examples or stated intentions if this rating is given.**
- **Rating 4 (Advanced):** AI/ML is explicitly positioned as a significant strategic priority with multiple specific use cases clearly described, dedicated investments mentioned (even if not quantified), and a defined impact on business operations. Evidence of AI being integrated across several business functions. **Quote the descriptions of use cases and investments if this rating is given.**
- **Rating 5 (Leading):** A comprehensive and well-articulated AI strategy is evident, including a detailed roadmap, significant and quantified financial commitments to AI, measurable results of AI initiatives, and AI positioned as a core driver of competitive advantage and business model evolution. **Provide strong evidence, including any quantified results or strategic roadmap details, if this rating is given.**

---

## **Dimension 2: Data Infrastructure and Analytics Maturity (Weighting: 25%)**

**What to look for:** Discussion of data platforms designed for advanced analytics, capabilities in areas like big data processing, data science teams and their specific skills, real-time data processing, robust data governance policies, deployment of predictive analytics, and sophisticated business intelligence tools beyond basic reporting.

- **Rating 1 (Basic):** Limited discussion of data, primarily focused on compliance or basic operational reporting. No mention of advanced analytics capabilities or a data-driven culture. **Provide evidence if this rating is given.**
- **Rating 2 (Foundational):** Basic data collection and reporting are mentioned. May reference standard market research or customer surveys, but no indication of advanced analytics being utilized for strategic insights. **Quote any references to data collection or reporting if this rating is given.**
- **Rating 3 (Intermediate):** The company describes having business intelligence and some basic analytics capabilities. Mentions the use of data for gaining insights or understanding customer behavior, and references basic data governance policies. **Cite the descriptions of analytics capabilities or data governance if this rating is given.**
- **Rating 4 (Sophisticated):** Evidence of advanced analytics capabilities, such as the use of predictive modeling, real-time data processing for decision-making, or customer personalization driven by data. A clear data strategy with investments in data infrastructure (data lakes, modern platforms) is discussed. Mentions of dedicated data science or analytics teams with specific expertise. **Quote evidence of advanced capabilities or data strategy if this rating is given.**
- **Rating 5 (Cutting-edge):** The company possesses a comprehensive and sophisticated data ecosystem that enables AI/ML-powered analytics at scale. Demonstrates real-time decision engines, highly advanced personalization strategies, and potentially even data monetization initiatives. Evidence of proprietary data advantages and highly skilled data science teams pushing the boundaries of modeling. **Provide strong evidence of this sophisticated data ecosystem if this rating is given.**

---

## **Dimension 3: Technology Infrastructure and Digital Capabilities (Weighting: 20%)**

**What to look for:** Extent of cloud adoption (mentioning specific cloud providers like AWS, Azure, GCP can be a strong indicator), discussion of API strategies enabling integration, descriptions of modern platform architectures, strategic technology partnerships (especially with cloud and AI leaders), presence of robust digital platforms for customer engagement or internal operations, and the degree of automation of core business processes leveraging modern technologies.

- **Rating 1 (Legacy):** Minimal to no discussion of modern technology infrastructure. Focus appears to be on maintaining outdated, on-premise systems rather than embracing digital innovation. **Provide evidence if this rating is given.**
- **Rating 2 (Transitioning):** Some mention of initial steps towards cloud adoption or ongoing system modernization projects, but the focus seems to be primarily on cost reduction or basic efficiency improvements rather than enabling advanced capabilities. **Quote any mentions of cloud or modernization if this rating is given.**
- **Rating 3 (Modernizing):** The company articulates a clear strategy for cloud migration or hybrid infrastructure. Mentions the use of APIs for integration, discusses the development of some digital platforms, and highlights partnerships aimed at enhancing digital capabilities. **Cite the cloud strategy, API mentions, or partnership details if this rating is given.**
- **Rating 4 (Advanced):** Demonstrates a comprehensive adoption of cloud-native or well-integrated hybrid infrastructure. Describes platform-based architectures that facilitate rapid development and deployment of digital services. Mentions strategic technology partnerships with major cloud and AI providers. Automation of significant core processes is evident. **Quote evidence of cloud adoption, platform architectures, or key partnerships if this rating is given.**
- **Rating 5 (Next-generation):** The company's technology stack is state-of-the-art and highly optimized for supporting AI/ML workloads at scale. Discusses real-time data processing capabilities, potentially mentions edge computing or other advanced infrastructure elements, and positions its technology infrastructure as a significant competitive advantage. **Provide strong evidence of this next-generation infrastructure if this rating is given.**

---

## **Dimension 4: Human Capital and AI Skills Development (Weighting: 15%)**

**What to look for:** Specific mentions of hiring data scientists, AI/ML engineers, and other AI-related roles. Discussion of dedicated AI/ML training programs for employees, initiatives to develop broader digital literacy across the workforce, strategies for attracting and retaining technology talent, formal reskilling programs focused on AI and related skills, and the establishment of AI literacy programs for non-technical staff.

- **Rating 1 (Traditional):** The annual report lacks any discussion about talent acquisition or skills development programs specifically related to technology or advanced analytics. **Provide evidence if this rating is given.**
- **Rating 2 (Awareness):** General statements about the importance of employee development are made, but there is no specific focus on building digital, analytical, or AI-related skills within the organization. **Quote any general statements about employee development if this rating is given.**
- **Rating 3 (Building):** Some references are made to technology training initiatives or programs aimed at improving digital skills. The company might mention efforts to hire technology professionals or provide some upskilling opportunities for the existing workforce in digital areas. **Cite any references to technology training or hiring initiatives if this rating is given.**
- **Rating 4 (Investing):** The company outlines specific strategies for acquiring AI/ML talent, including recruitment efforts or partnerships. Comprehensive digital skills training programs are described, and there might be mentions of collaborations with universities for AI research or to build a talent pipeline. **Quote evidence of specific AI talent strategies or comprehensive training programs if this rating is given.**
- **Rating 5 (Leading):** The company has a significant and well-established AI/data science team (potentially with numbers or specific team structures mentioned). Company-wide initiatives to promote AI literacy are in place. Centers of excellence dedicated to AI/ML research and application are highlighted. The company demonstrates strategic talent partnerships and strong programs for retaining critical AI skills. **Provide strong evidence of a leading human capital strategy in AI if this rating is given.**

---

## **Dimension 5: AI Governance and Responsible Implementation (Weighting: 5%)**

**What to look for:** Explicit articulation of AI ethics policies or principles, discussion of measures to ensure algorithmic fairness and prevent bias in AI systems, frameworks for AI risk management and compliance, commitments to responsible AI development and deployment, procedures for ensuring transparency in how AI systems function, and efforts to audit AI systems for ethical and fairness considerations.

- **Rating 1 (Absent):** The annual report contains no discussion whatsoever about AI-related governance, ethical considerations, or risk management practices beyond standard cybersecurity protocols. **Provide evidence if this rating is given.**
- **Rating 2 (Basic):** General statements about data privacy and cybersecurity are included, but there is no specific governance framework or policies addressing the unique ethical challenges and risks associated with artificial intelligence. **Quote any general statements about data privacy or cybersecurity if this rating is given.**
- **Rating 3 (Developing):** The company shows some level of awareness regarding the potential risks or ethical considerations related to AI. Mentions of basic governance structures for data and technology projects might be present, potentially touching upon AI. **Cite any mentions of AI risks or relevant governance structures if this rating is given.**
- **Rating 4 (Structured):** A clear and defined AI governance framework is outlined, including specific policies or guidelines for the responsible development and deployment of AI systems. Board-level oversight of AI initiatives from an ethical and risk perspective might be mentioned. **Quote evidence of a specific AI governance framework or board oversight if this rating is given.**
- **Rating 5 (Exemplary):** The company demonstrates a comprehensive and leading-edge responsible AI program. This includes detailed ethics guidelines that are actively enforced, established procedures for testing and mitigating bias in algorithms, clear transparency requirements for AI systems, and regular auditing processes to ensure ethical and fair AI implementation. The company might be seen as an industry leader in this space, contributing to best practices in AI governance. **Provide strong evidence of this exemplary responsible AI program if this rating is given.**

---

## **Output Format Requirements**

Provide your analysis in exactly this format:

**Company:** [Company Name]

**Dimension Scores:**
- Dimension 1 (AI Strategy and Vision): X/5
- Dimension 2 (Data Infrastructure and Analytics): X/5
- Dimension 3 (Technology Infrastructure and Digital Capabilities): X/5
- Dimension 4 (Human Capital and AI Skills): X/5
- Dimension 5 (AI Governance and Responsible Implementation): X/5

**Overall AI-Readiness Score:** X.XX/5.00
(Calculated as: D1×0.35 + D2×0.25 + D3×0.20 + D4×0.15 + D5×0.05)

**Key Evidence Summary:**
- **Dimension 1 Evidence:** [Specific phrase or section from the report]
- **Dimension 2 Evidence:** [Specific phrase or section from the report]
- **Dimension 3 Evidence:** [Specific phrase or section from the report]
- **Dimension 4 Evidence:** [Specific phrase or section from the report]
- **Dimension 5 Evidence:** [Specific phrase or section from the report]
- **Strategic AI Positioning:** [1-2 sentences on how AI fits into their business strategy, based on the report]

**Confidence Level:** [High/Medium/Low] - based on the specificity and depth of AI-related disclosures in the report
"""

def combine_contexts(phrase_contexts):
    texts = []
    for phrase, sentences in phrase_contexts.items():
        texts.append(f"Keyword: {phrase}")
        texts.extend(sentences)
    return "\n".join(texts)

def analyze_ai_readiness(text, company_name):
    messages = [
        {"role": "system", "content": "You are a helpful assistant expert in analyzing AI readiness of companies based on annual reports."},
        {"role": "user", "content": PROMPT_TEMPLATE + "\n\n" + f"### 10-K Report Excerpts for {company_name}:\n\n{text}"}
    ]
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        max_tokens=700,
        temperature=0.3,
    )
    return response.choices[0].message.content

def main():
    with open('filtered_context.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    companies = data["companies"]

    results = []

    # Just pick the first company for now
    company = companies[39]
    phrase_contexts = company.get('phrase_contexts', {})
    combined_text = combine_contexts(phrase_contexts)
    company_name = company.get('name', 'Unknown')

    print(f"Processing {company_name}...")
    analysis = analyze_ai_readiness(combined_text, company_name)

    result_entry = {
        "company": company_name,
        "ticker": company.get('ticker'),
        "analysis": analysis
    }
    results.append(result_entry)

    # Save results for this one company
    with open('chat_responses.json', 'w', encoding='utf-8') as out_f:
        json.dump(results, out_f, indent=2)

    print(f"Processed 1 company: {company_name}")

if __name__ == "__main__":
    main()
