// app/CompanyRow.tsx
"use client";
import { useState } from "react";

type CompanySummary = {
  id: string;
  company: string;
  overall: number;
};

export default function CompanyRow({ company }: { company: CompanySummary }) {
  const [open, setOpen] = useState(false);
  const [detail, setDetail] = useState<any | null>(null);
  const [loading, setLoading] = useState(false);

  const handleToggle = async () => {
    setOpen(o => !o);
    if (!detail && !loading && !open) {
      setLoading(true);
      const res = await fetch(`/api/company/${company.id}`);
      const data = await res.json();
      setDetail(data);
      setLoading(false);
    }
  };

  return (
    <>
      <tr onClick={handleToggle} style={{ cursor: "pointer", background: open ? "#eee" : undefined }}>
        <td>{company.company}</td>
        <td style={{ textAlign: "right" }}>{company.overall?.toFixed(2)}</td>
      </tr>
      {open && (
        <tr>
          <td colSpan={2}>
            {loading && "Loading..."}
            {detail && (
              <div>
                <b>Sector:</b> {detail.sector}<br />
                <b>Industry:</b> {detail.industry}<br />
                <b>Dimension Scores:</b>
                <ul>
                  <li>D1: {detail.dim1}</li>
                  <li>D2: {detail.dim2}</li>
                  <li>D3: {detail.dim3}</li>
                  <li>D4: {detail.dim4}</li>
                  <li>D5: {detail.dim5}</li>
                </ul>
                <b>Evidence:</b> <pre style={{ whiteSpace: "pre-wrap" }}>{detail.evidence}</pre>
                <b>Strategic:</b> {detail.strategic}<br />
                <b>Context:</b> {detail.context}<br />
                <b>Confidence:</b> {detail.confidence}
              </div>
            )}
          </td>
        </tr>
      )}
    </>
  );
}
