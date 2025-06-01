// app/[company]/page.tsx
import { supabase } from '../../lib/supabaseClient';
import Link from 'next/link';

export default async function CompanyPage({ params }: { params: { company: string } }) {
  const companyName = params.company.replace(/-/g, ' ');

  const { data: company, error } = await supabase
    .from('companies')
    .select('*')
    .ilike('name', companyName)
    .single();

  if (error) return <div>Error loading company: {error.message}</div>;
  if (!company) return <div>Company not found</div>;

  return (
    <main style={{ padding: '2rem', maxWidth: '600px', margin: 'auto' }}>
      <h1 style={{ fontSize: '2.5rem' }}>{company.name}</h1>
      <p>{company.wiki_intro}</p>
      <Link href="/" style={{ color: '#0070f3', textDecoration: 'underline' }}>
        ← Back to Home
      </Link>
    </main>
  );
}
