// app/[company]/page.tsx
import { supabase } from '../../lib/supabaseClient';
import Link from 'next/link';

export default async function CompanyPage({ 
  params 
}: { 
  params: Promise<{ company: string }> 
}) {
  // Await the params since it's now a Promise
  const resolvedParams = await params;
  const companyName = resolvedParams.company.replace(/-/g, ' ');

  const { data: company, error } = await supabase
    .from('companies')
    .select('*')
    .ilike('name', companyName)
    .single();

  if (error) return <div>Error loading company: {error.message}</div>;
  if (!company) return <div>Company not found</div>;

  return (
    <div>
      <h1>{company.name}</h1>
      <p>{company.wiki_intro}</p>
      <Link href="/">← Back to Home</Link>
    </div>
  );
}