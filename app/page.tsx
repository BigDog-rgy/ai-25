import { createClient } from "@supabase/supabase-js";
import CompanyRow from "./CompanyRow";

type CompanySummary = {
  id: string;
  company: string;
  market_cap: string | null;
  overall: number;
  isTopIndex?: boolean;
  index_weight?: number;
};

function calculateTopIndexWithWeights(companies: CompanySummary[]) {
  if (!companies || companies.length === 0) return [];

  // Only top 9 for now
  const topN = Math.min(9, companies.length);
  // Top 4 by MC, rest get 20%
  const topMC = Math.min(4, topN);
  const rest = topN - topMC;

  // Sort by overall score (desc)
  const topCompanies = companies
    .slice()
    .sort((a, b) => b.overall - a.overall)
    .slice(0, topN);

  // Convert market_cap to number
  const withMCNum = topCompanies.map(c => ({
    ...c,
    mc: c.market_cap ? Number(String(c.market_cap).replace(/[^\d.]/g, "")) : 0,
  }));

  // Sort by MC desc
  const sortedByMC = withMCNum.slice().sort((a, b) => b.mc - a.mc);

  const topMCPool = sortedByMC.slice(0, topMC);
  const restPool = sortedByMC.slice(topMC);

  const topMCTotal = topMCPool.reduce((sum, c) => sum + c.mc, 0);
  const restTotal = restPool.reduce((sum, c) => sum + c.mc, 0);

  // Assign weights
  return withMCNum.map(c => {
    let index_weight = 0;
    if (topMCPool.find(tc => tc.id === c.id)) {
      index_weight = topMCTotal > 0 ? (c.mc / topMCTotal) * 0.8 : 0;
    } else {
      index_weight = restTotal > 0 ? (c.mc / restTotal) * 0.2 : 0;
    }
    return {
      ...c,
      isTopIndex: true,
      index_weight: index_weight * 100, // as percent
    };
  });
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

  // Calculate weights for demo dataset
  const topIndexCompanies = calculateTopIndexWithWeights(rows || []);

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
          {topIndexCompanies.map((r, idx) => (
            <CompanyRow
              key={r.id}
              company={r}
              indexWeight={r.index_weight}
              isTopIndex={r.isTopIndex}
              rank={idx + 1}
            />
          ))}
        </tbody>
      </table>
    </main>
  );
}
