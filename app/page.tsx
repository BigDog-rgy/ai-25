import { createClient } from "@supabase/supabase-js";
import CompanyRow from "./CompanyRow";

type CompanySummary = {
  id: string;
  company: string;
  market_cap: string | null;
  overall: number;
};

export default async function Page() {
  const supabase = createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  );
  const { data: rows } = await supabase
    .from("company_ai_readiness")
    .select("id, company, market_cap, overall")
    .order("overall", { ascending: false }) as { data: CompanySummary[] | null };

  return (
    <main style={{ maxWidth: 700, margin: "2rem auto" }}>
      <h1>AI-Readiness: S&P 500</h1>
      <table style={{ width: "100%", borderCollapse: "collapse", marginTop: 24 }}>
        <thead>
          <tr>
            <th style={{ textAlign: "right" }}>#</th>
            <th style={{ textAlign: "left" }}>Company</th>
            <th style={{ textAlign: "right" }}>Overall Score</th>
          </tr>
        </thead>
        <tbody>
  {rows?.map((r) => (
    <CompanyRow key={r.id} company={r} />
  ))}
</tbody>
      </table>
    </main>
  );
}
