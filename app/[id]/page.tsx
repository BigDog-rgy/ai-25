// app/[id]/page.tsx
import { createClient } from "@supabase/supabase-js";
import Link from "next/link";

// DO NOT import or define any PageProps types

// Use the default export name "Page" (not required, but most canonical)
export default async function Page({ params }: { params: { id: string } }) {
  const supabase = createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  );
  const { data } = await supabase
    .from("company_ai_readiness")
    .select("*")
    .eq("id", params.id)
    .single();

  if (!data) return <div>Company not found.</div>;

  return (
    <main style={{ maxWidth: 700, margin: "2rem auto" }}>
      <Link href="/">&larr; Back to list</Link>
      <h1>{data.company}</h1>
      {/* ... rest of your details ... */}
    </main>
  );
}
