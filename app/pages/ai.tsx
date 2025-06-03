// pages/ai.tsx  (simplest React component)
import { useEffect, useState } from "react";
import { supabase } from "../../lib/supabase";

export default function AIReadiness() {
  const [rows, setRows] = useState<any[]>([]);

  useEffect(() => {
    supabase
      .from("company_ai_readiness")
      .select("*")
      .order("overall", { ascending: false })
      .then(({ data }) => setRows(data || []));
  }, []);

  return (
    <div className="p-6">
      <h1 className="text-2xl mb-4">AI-Readiness Scores</h1>
      <table className="w-full text-sm">
        <thead className="font-semibold bg-gray-100">
          <tr>
            <th>Company</th><th>Overall</th>
            <th>D1</th><th>D2</th><th>D3</th><th>D4</th><th>D5</th>
          </tr>
        </thead>
        <tbody>
          {rows.map(r => (
            <tr key={r.id} className="border-b hover:bg-gray-50">
              <td>{r.company}</td>
              <td>{r.overall.toFixed(2)}</td>
              <td>{r.dim1}</td><td>{r.dim2}</td><td>{r.dim3}</td>
              <td>{r.dim4}</td><td>{r.dim5}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
