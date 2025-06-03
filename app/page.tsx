// app/page.tsx
import Link from 'next/link';
import { supabase } from '../lib/supabase';

export default async function HomePage() {
  const { data: companies, error } = await supabase.from('companies').select('*');

  if (error) {
    return <p>Error loading companies: {error.message}</p>;
  }

  return (
    <main style={{ padding: '2rem', maxWidth: '600px', margin: 'auto' }}>
      <h1 style={{ fontSize: '3rem', marginBottom: '2rem' }}>AI-25</h1>
      <nav>
        <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
          {companies?.map((company) => (
            <li key={company.id} style={{ marginBottom: '1.5rem' }}>
              <Link
                href={`/${company.name.toLowerCase().replace(/\s+/g, '-')}`}
                style={{ textDecoration: 'none', fontSize: '1.5rem', color: '#0070f3' }}
              >
                {company.name}
              </Link>
            </li>
          ))}
        </ul>
      </nav>
    </main>
  );
}
