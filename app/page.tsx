import { createClient } from "@supabase/supabase-js";
import CompanyRow from "./CompanyRow";

type CompanySummary = {
  id: string;
  company: string;
  market_cap: string | null;
  overall: number;
  // These are added later, don't need to be here for DB fetch!
  index_weight?: number;
  isTopIndex?: boolean;
};

function calculateTopIndexWithWeights(companies: CompanySummary[], n: number) {
  if (!companies || companies.length === 0) return {};

  // Top N by overall
  const topN = Math.min(n, companies.length);

  // Sort and select topN by overall
  const topCompanies = companies
    .slice()
    .sort((a, b) => b.overall - a.overall)
    .slice(0, topN);

  // Now, within topN, find top X by MC
  const TOP_MC = Math.min(10, topN); // or 4 for demo, etc.
  const sortedByMC = topCompanies.slice().sort((a, b) => {
    const mca = Number(String(a.market_cap).replace(/[^\d.]/g, "")) || 0;
    const mcb = Number(String(b.market_cap).replace(/[^\d.]/g, "")) || 0;
    return mcb - mca;
  });
  const topMCPool = sortedByMC.slice(0, TOP_MC);
  const restPool = sortedByMC.slice(TOP_MC);

  const topMCTotal = topMCPool.reduce(
    (sum, c) => sum + (Number(String(c.market_cap).replace(/[^\d.]/g, "")) || 0), 0);
  const restTotal = restPool.reduce(
    (sum, c) => sum + (Number(String(c.market_cap).replace(/[^\d.]/g, "")) || 0), 0);

  // Build result as { [id]: { index_weight, isTopIndex } }
  const out: Record<string, { index_weight: number; isTopIndex: boolean }> = {};
  topCompanies.forEach((c) => {
    const mc = Number(String(c.market_cap).replace(/[^\d.]/g, "")) || 0;
    let w = 0;
    if (topMCPool.find(tc => tc.id === c.id)) {
      w = topMCTotal > 0 ? (mc / topMCTotal) * 0.8 : 0;
    } else {
      w = restTotal > 0 ? (mc / restTotal) * 0.2 : 0;
    }
    out[c.id] = { index_weight: w * 100, isTopIndex: true };
  });
  return out;
}

export default async function Page() {
  const supabase = createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  );
  const { data: rows } = await supabase
    .from("company_ai_readiness")
    .select("id, company, market_cap, overall")
    .order("overall", { ascending: false }) as { data: CompanySummary[] | null };

  // 1. Calculate "top index" weights for top N (use 25 for real, or 5/9 for test)
  const topIndexMap = calculateTopIndexWithWeights(rows || [], 5);

  return (
    <main style={{ maxWidth: 700, margin: "2rem auto" }}>
      <h1>AI-Readiness: S&P 500</h1>
      <table style={{ width: "100%", borderCollapse: "collapse", marginTop: 24 }}>
        <thead>
          <tr>
            <th style={{ textAlign: "right" }}>#</th>
            <th style={{ textAlign: "left" }}>Company</th>
            <th style={{ textAlign: "right" }}>Overall Score</th>
            <th style={{ textAlign: "right" }}>Index Weight</th>
          </tr>
        </thead>
        <tbody>
          {rows?.map((r, idx) => (
            <CompanyRow
              key={r.id}
              company={r}
              rank={idx + 1}
              isTopIndex={!!topIndexMap[r.id]}
              indexWeight={topIndexMap[r.id]?.index_weight ?? undefined}
            />
          ))}
        </tbody>
      </table>
    </main>
  );
}
