// ai-25/app/page.tsx
import Link from "next/link";
import { createClient } from "@supabase/supabase-js";

export default async function MainPage() {
  const supabase = createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  );
  const { data: rows } = await supabase
    .from("company_ai_readiness")
    .select("company, overall")
    .order("overall", { ascending: false });

  return (
    <main style={{ maxWidth: 700, margin: "2rem auto" }}>
      <h1>AI-Readiness: S&P 500</h1>
      <table style={{ width: "100%", borderCollapse: "collapse", marginTop: 24 }}>
        <thead>
          <tr>
            <th style={{ textAlign: "left" }}>Company</th>
            <th style={{ textAlign: "right" }}>Overall Score</th>
          </tr>
        </thead>
        <tbody>
          {rows?.map(r => (
            <tr key={r.company}>
              <td>
                <Link href={`/${encodeURIComponent(encodeURIComponent(r.company))}`}>
  {r.company}
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
