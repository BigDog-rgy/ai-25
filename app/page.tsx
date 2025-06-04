import Link from "next/link";
import { createClient } from "@supabase/supabase-js";

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
          {rows?.map((r, idx) => (
            <tr key={r.id}>
              <td style={{ textAlign: "right", paddingRight: 12 }}>{idx + 1}</td>
              <td>
                <Link href={`/${r.id}`}>
                  {r.company}
                  {r.market_cap ? ` (${r.market_cap})` : ""}
                </Link>
              </td>
              <td style={{ textAlign: "right" }}>{r.overall?.toFixed(2)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </main>
  );
}
