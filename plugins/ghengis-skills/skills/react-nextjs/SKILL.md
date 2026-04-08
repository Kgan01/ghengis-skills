---
name: react-nextjs
description: Use when building or modifying React or Next.js applications — covers App Router patterns, server components, client components, data fetching, Zustand state management, and common pitfalls
allowed-tools: Read Write Edit Glob Grep Bash(npm *) Bash(npx *)
---

# React 19 + Next.js 15

## When This Applies

Working on any React or Next.js application — components, pages, layouts, data fetching, routing, rendering, state management (Zustand), or heavy UI libraries.

## Key Concepts

Next.js 15 App Router defaults every component to a **Server Component** — no JS bundle cost, direct data access, no hooks allowed. Add `'use client'` only when the component needs browser APIs, event handlers, or React state/effects. Data flows server-down: fetch in Server Components, pass results as props to Client Components. Zustand stores live exclusively in Client Components. Use CSS variables for all colors and spacing — never hardcode hex values or bypass the design system.

## Common Patterns

**Server Component with data fetch (default pattern):**
```tsx
// app/dashboard/page.tsx — no 'use client'
export default async function DashboardPage() {
  const data = await fetch('/api/dashboard', { next: { revalidate: 60 } });
  const result = await data.json();
  return <DashboardView data={result} />;
}
```

**Client Component (opt-in only when needed):**
```tsx
'use client';
import { useState } from 'react';

export function SearchBar({ onSearch }: { onSearch: (q: string) => void }) {
  const [query, setQuery] = useState('');
  return <input value={query} onChange={e => { setQuery(e.target.value); onSearch(e.target.value); }} />;
}
```

**Reading from Zustand stores:**
```tsx
'use client';
import { useNavigationStore } from '@/stores/navigationStore';

export function NavMenu() {
  const { currentRoute, navigate } = useNavigationStore();
  return <nav>{/* ... */}</nav>;
}
```

**Dynamic import for heavy libraries (Three.js, chart libs, etc.):**
```tsx
'use client';
import dynamic from 'next/dynamic';

const HeavyComponent = dynamic(() => import('@/components/HeavyComponent'), {
  ssr: false,
  loading: () => <div className="loader" />,
});
```

**Authenticated fetch pattern:**
```ts
// lib/api/fetchWithAuth.ts — handles token injection and 401 refresh
const result = await fetchWithAuth('/api/resource', {
  method: 'POST',
  body: JSON.stringify(payload),
});
```

**Theme-aware CSS variables:**
```css
/* Always use CSS variables, never raw colors */
.card {
  background: var(--color-surface);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border);
}
```

**Layout with shared Server/Client split:**
```tsx
// app/layout.tsx — Server Component shell
import { ThemeProvider } from '@/components/ThemeProvider'; // 'use client' inside

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html>
      <body>
        <ThemeProvider>{children}</ThemeProvider>
      </body>
    </html>
  );
}
```

**Route-level loading state:**
```tsx
// app/dashboard/loading.tsx
export default function Loading() {
  return <div className="skeleton-screen" />;
}
```

## Anti-Patterns

**'use client' everywhere** — adds every import to the JS bundle and disables server rendering. Only mark a component `'use client'` when it genuinely needs hooks, event handlers, or browser APIs. Keep the boundary as deep (leaf-ward) as possible.

**useEffect for data fetching** — fetching in `useEffect` causes loading spinners, waterfall requests, and empty server HTML. Fetch in async Server Components or use a library like SWR/React Query for client-side revalidation only.

**Importing heavy libs without dynamic()** — importing Three.js, chart libraries, or similar heavy dependencies at the top level bloats the initial bundle. Always wrap them in `next/dynamic` with `ssr: false`.

**Hardcoding colors** — `color: '#1a1a2e'` breaks dark/light mode and design system consistency. Use CSS variables exclusively.

**Pages Router patterns** — `getServerSideProps`, `getStaticProps`, `useRouter` from `next/router`, `_app.tsx`, and `_document.tsx` do not exist in the App Router. Use `app/` conventions: `page.tsx`, `layout.tsx`, `loading.tsx`, `useRouter` from `next/navigation`.

## Validation

- `npm run build` — catches type errors, missing exports, and invalid Server/Client boundaries
- `npm run dev` — live reload; watch the terminal for hydration mismatch warnings
- Browser console: hydration errors appear as red warnings — fix by ensuring Server and Client render identical initial HTML
- Check bundle size with Next.js build output: pages over 200 KB first load JS warrant a `dynamic()` split
