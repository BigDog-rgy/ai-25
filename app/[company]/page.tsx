// ai-25/app/[company]/page.tsx
import { createClient } from "@supabase/supabase-js";
import Link from "next/link";

export default async function CompanyPage({ params }: { params: { company: string } }) {
  const supabase = createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  );

  // Get the company param
  const encodedCompany = params.company;

  // Double decode
  const companyName = decodeURIComponent(decodeURIComponent(encodedCompany));

  const { data } = await supabase
    .from("company_ai_readiness")
    .select("*")
    .eq("company", companyName)
    .single();

  if (!data) return <div>Company not found.</div>;

  return (
    <main style={{ maxWidth: 700, margin: "2rem auto" }}>
      <Link href="/">&larr; Back to list</Link>
      <h1>{data.company}</h1>
      <p>
        <b>Sector:</b> {data.sector} <br />
        <b>Industry:</b> {data.industry} <br />
        <b>Overall AI-Readiness Score:</b> {data.overall?.toFixed(2)}
      </p>
      <hr />
      <h2>Dimension Scores</h2>
      <ul>
        <li>D1: {data.dim1}</li>
        <li>D2: {data.dim2}</li>
        <li>D3: {data.dim3}</li>
        <li>D4: {data.dim4}</li>
        <li>D5: {data.dim5}</li>
      </ul>
      <h2>Key Evidence</h2>
      <pre style={{ whiteSpace: "pre-wrap" }}>{data.evidence}</pre>
      <h3>Strategic AI Positioning</h3>
      <p>{data.strategic}</p>
      <h3>Contextual Considerations</h3>
      <p>{data.context}</p>
      <h3>Confidence Level</h3>
      <p>{data.confidence}</p>
    </main>
  );
}
