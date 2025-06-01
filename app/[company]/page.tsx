import { supabase } from '../../lib/supabaseClient';

interface PageProps {
  params: { company: string };
}

export default async function CompanyPage({ params }: PageProps) {
  const { company } = params;

  // Convert hyphenated URL slug back to company name-ish for lookup
  const companyName = company.replace(/-/g, ' ');

  // Query Supabase for the company by name (case insensitive)
  const { data, error } = await supabase
    .from('companies')
    .select('name, ticker')
    .ilike('name', `%${companyName}%`)
    .limit(1)
    .single();

  if (error || !data) {
    return <p>Company not found: {company}</p>;
  }

  return (
    <main style={{ padding: '2rem', maxWidth: '600px', margin: 'auto' }}>
      <h1>{data.name}</h1>
      <p>Ticker: {data.ticker}</p>
    </main>
  );
}
