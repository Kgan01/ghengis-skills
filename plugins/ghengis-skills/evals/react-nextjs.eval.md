# React + Next.js -- Evaluation

## TC-1: Server Component Data Fetch
- **prompt:** "Create a dashboard page that fetches data from /api/dashboard and renders it"
- **context:** Next.js 15 App Router project. Default should be a Server Component.
- **assertions:**
  - Component is an async function (Server Component by default) -- no `'use client'` directive
  - Uses `await fetch()` directly in the component body (not in useEffect)
  - File is placed in `app/` directory (e.g., `app/dashboard/page.tsx`)
  - Uses `next: { revalidate: N }` or equivalent caching strategy
  - Does not import `useState`, `useEffect`, or other client-only hooks
- **passing_grade:** 4/5 assertions must pass

## TC-2: Client Component Boundary
- **prompt:** "Add a search bar with live filtering to this server-rendered page"
- **context:** Existing Server Component page needs interactive client-side functionality.
- **assertions:**
  - Search bar component has `'use client'` directive at the top
  - Uses `useState` for the query state
  - The client boundary is pushed as deep as possible (only the search bar, not the whole page)
  - Parent page remains a Server Component
  - Props are passed from Server to Client component for data flow
- **passing_grade:** 4/5 assertions must pass

## TC-3: Heavy Library Dynamic Import
- **prompt:** "I need to add a 3D visualization using Three.js to my Next.js page"
- **context:** User wants to import a heavy library that should not be in the initial bundle.
- **assertions:**
  - Uses `next/dynamic` with `ssr: false` to import the Three.js component
  - Component file has `'use client'` directive
  - Includes a `loading` fallback component
  - Does not import Three.js at the top level of a Server Component
  - Does not use `useEffect` with `import()` as the primary pattern
- **passing_grade:** 4/5 assertions must pass

## TC-4: Anti-Pattern Detection -- useEffect for Data Fetching
- **prompt:** "Here's my component. Is there anything wrong with it?\n```tsx\n'use client';\nimport { useState, useEffect } from 'react';\nexport default function ProductList() {\n  const [products, setProducts] = useState([]);\n  useEffect(() => { fetch('/api/products').then(r => r.json()).then(setProducts); }, []);\n  return <ul>{products.map(p => <li key={p.id}>{p.name}</li>)}</ul>;\n}\n```"
- **context:** User has a component with the classic useEffect data fetching anti-pattern in App Router.
- **assertions:**
  - Identifies useEffect for data fetching as an anti-pattern in App Router
  - Explains the problems: loading spinners, waterfall requests, empty server HTML
  - Recommends converting to an async Server Component with direct fetch
  - Removes `'use client'` in the refactored version
  - Refactored code uses `await fetch()` in the component body
- **passing_grade:** 4/5 assertions must pass

## TC-5: CSS Variables Over Hardcoded Colors
- **prompt:** "Add styling to this card component: background should be #1a1a2e, text should be white"
- **context:** User requests hardcoded hex colors. Skill should enforce CSS variables.
- **assertions:**
  - Does not use hardcoded hex values in the CSS/className
  - Uses CSS variables (e.g., `var(--color-surface)`, `var(--color-text-primary)`)
  - Explains why hardcoded colors break dark/light mode and design system consistency
  - Provides a CSS variable definition example if no design system exists yet
- **passing_grade:** 3/4 assertions must pass
