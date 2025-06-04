"use client";
import { useState } from "react";
import { createClient } from "@supabase/supabase-js";

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
);

type CompanySummary = {
  id: string;
  company: string;
  market_cap: string | null;
  overall: number;
};

type CompanyDetail = {
  sector?: string | null;
  industry?: string | null;
  dim1?: number | null;
  dim2?: number | null;
  dim3?: number | null;
  dim4?: number | null;
  dim5?: number | null;
  evidence?: string | null;
  strategic?: string | null;
  context?: string | null;
  confidence?: string | null;
  // Add more fields as needed
};

export default function CompanyRow({
  company,
  indexWeight,
  isTopIndex,
  rank,
}: {
  company: CompanySummary;
  indexWeight?: number;
  isTopIndex?: boolean;
  rank: number;
}) {
  // This is what you were missing!
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [detail, setDetail] = useState<CompanyDetail | null>(null);

  const handleToggle = async () => {
    setOpen(o => !o);
    if (!detail && !loading && !open) {
      setLoading(true);
      const { data, error } = await supabase
        .from("company_ai_readiness")
        .select("*")
        .eq("id", company.id)
        .single();
      setDetail(data);
      setLoading(false);
      if (error) {
        console.error("Supabase fetch error:", error);
      }
    }
  };

  return (
    <>
      <tr
        onClick={handleToggle}
        style={{
            background: isTopIndex ? "#fffbec" : undefined,
            fontWeight: isTopIndex ? "bold" : undefined,
            cursor: "pointer",
        }}
        >
        <td style={{ textAlign: "right" }}>{rank}</td>
        <td>
            {company.company}
            {company.market_cap ? ` (${company.market_cap})` : ""}
        </td>
        <td style={{ textAlign: "right" }}>
            {company.overall?.toFixed(2)}
        </td>
        <td style={{ textAlign: "right" }}>
            {isTopIndex && indexWeight ? indexWeight.toFixed(2) + "%" : ""}
        </td>
        </tr>
      {open && (
        <tr>
          <td colSpan={4}>
            {loading && "Loading..."}
            {detail && (
              <div>
                <b>Sector:</b> {detail.sector}
                <br />
                <b>Industry:</b> {detail.industry}
                <br />
                <b>Dimension Scores:</b>
                <ul>
                  <li>D1: {detail.dim1}</li>
                  <li>D2: {detail.dim2}</li>
                  <li>D3: {detail.dim3}</li>
                  <li>D4: {detail.dim4}</li>
                  <li>D5: {detail.dim5}</li>
                </ul>
                <b>Evidence:</b>{" "}
                <pre style={{ whiteSpace: "pre-wrap" }}>
                  {detail.evidence}
                </pre>
                <b>Strategic:</b> {detail.strategic}
                <br />
                <b>Context:</b> {detail.context}
                <br />
                <b>Confidence:</b> {detail.confidence}
              </div>
            )}
          </td>
        </tr>
      )}
    </>
  );
}
