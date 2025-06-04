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

function calculateTopIndexWithWeights(companies: CompanySummary[], indexN = 5, bucketTop = 2) {
  if (!companies || companies.length === 0) return {};

  // 1. Get top N by overall (AI-25)
  const topN = Math.min(indexN, companies.length);
  const topCompanies = companies
    .slice()
    .sort((a, b) => b.overall - a.overall)
    .slice(0, topN);

  // 2. Sort topN by market cap (parse to number!)
  const topCompaniesWithMC = topCompanies.map(c => ({
    ...c,
    mc: c.market_cap ? Number(String(c.market_cap).replace(/[^\d.]/g, "")) : 0,
  }));
  const bucketN = Math.min(bucketTop, topN);

  const sortedByMC = topCompaniesWithMC.slice().sort((a, b) => b.mc - a.mc);
  const topMCPool = sortedByMC.slice(0, bucketN);
  const bottomMCPool = sortedByMC.slice(bucketN);

  const topMCsum = topMCPool.reduce((sum, c) => sum + c.mc, 0);
  const bottomMCsum = bottomMCPool.reduce((sum, c) => sum + c.mc, 0);

  // 3. Assign weights to AI-25
  const out: Record<string, { index_weight: number; isTopIndex: boolean }> = {};
  topCompaniesWithMC.forEach((c) => {
    let w = 0;
    if (topMCPool.find(tc => tc.id === c.id)) {
      w = topMCsum > 0 ? (c.mc / topMCsum) * 0.8 : 0;
    } else {
      w = bottomMCsum > 0 ? (c.mc / bottomMCsum) * 0.2 : 0;
    }
    out[c.id] = { index_weight: w * 100, isTopIndex: true };
  });

  // 4. For companies NOT in the AI-25, isTopIndex false, weight 0
  companies.forEach(c => {
    if (!out[c.id]) out[c.id] = { index_weight: 0, isTopIndex: false };
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
            <th style={{ textAlign: "right", paddingRight: 10 }}>#</th>
            <th style={{ textAlign: "left", paddingLeft: 10 }}>Company</th>
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
              isTopIndex={!!topIndexMap[r.id]?.isTopIndex}
              indexWeight={topIndexMap[r.id]?.isTopIndex ? topIndexMap[r.id].index_weight : undefined}
            />
          ))}
        </tbody>
      </table>
    </main>
  );
}
