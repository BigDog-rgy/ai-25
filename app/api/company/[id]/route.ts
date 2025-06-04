import { NextResponse } from "next/server";
import { createClient } from "@supabase/supabase-js";

type RouteContext = {
  params: {
    id: string;
  };
};

export async function GET(request: Request, context: RouteContext) {
  const id = context.params.id;

  const supabase = createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  );
  const { data } = await supabase
    .from("company_ai_readiness")
    .select("*")
    .eq("id", id)
    .single();

  if (!data) {
    return NextResponse.json({ error: "Company not found" }, { status: 404 });
  }
  return NextResponse.json(data);
}
