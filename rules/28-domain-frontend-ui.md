---
trigger: glob
globs: "**/*.tsx, **/*.jsx, **/*.vue, **/*.svelte, **/*.css, **/*.scss"
description: "Frontend UI domain rules: component size, derived state over sync loops, state colocation, and strict cleanup hygiene."
---

# Domain Pack: Frontend UI (`28`)

## Critical Frontend UI Guardrails

| Area | Trap / Smell | Mandatory Idiomatic Practice |
|---|---|---|
| **Component Size & Responsibility Split** | Massive 500+ LOC components mixing rendering, API fetching, complex business logic, and local state management | Keep components `<=150-200` LOC. Extract business logic, async orchestration, and subscriptions into custom hooks (`use*`), Vue composables, or Svelte stores/runes. Keep UI components focused on visual rendering |
| **Derived State Over `useEffect` / `watch` Sync Loops** | Cascading re-render bugs caused by `useEffect(() => setX(f(prop)), [prop])` or manually syncing state arrays | Compute derived values during render seamlessly using `useMemo`, Vue `computed`, or Svelte `$derived`. **Ban** using effects exclusively to synchronize state values derived from props to prevent render cycles |
| **State Colocation & Server-vs-Client Boundary** | Dumping all ephemeral UI state into global Redux/Zustand stores; mixing server-cache data with local widget state | Keep state as close to its consumers as possible. Leverage component composition, `children`, and slots before reaching for global stores. Strictly separate server cache (`TanStack Query`/SSR) from ephemeral UI state |
| **Reusable Design-System Primitives Over Copy-Paste Markup** | Duplicating 100-line JSX/template blocks for slightly different buttons or modals; inconsistent spacing and typography | Consolidate repeated UI blocks and variants via typed variant props (`cva`, component slots, polymorphism) rather than copy-pasting structure. Build robust foundational primitives to enforce design consistency |
| **Effect, Listener & Fetch Cleanup** | Leaving stray event listeners attached on unmount; abandoning network requests; stale-closure race conditions | Always return a cleanup callback using `AbortController`, `removeEventListener`, or `clearInterval` to prevent memory leaks and race conditions when fetching data or listening to global browser events |
| **Type-Safe Props, Events & Forms** | Using impossible boolean combinations (`isLoading && isError`) for state; passing untyped props (`any`) deep down the tree | Use discriminated union props for state variants (`idle | loading | error | success`) so invalid UI states are unrepresentable by the type system. Strictly type all event emitters and form payload boundaries |
| **Accessibility (`a11y`) & XSS Hygiene** | Using `<div>` for clickable elements; missing keyboard focus management; injecting untrusted user text dynamically | Use semantic `<button>`, `<dialog>`, and `<form>`. Ensure keyboard focus management and ARIA labels. Radically ban unescaped `dangerouslySetInnerHTML`, `v-html`, or `{@html}` on untrusted user data to stop XSS |
| **Performance & Bundle Discipline** | Using array index for list `key`s on mutable lists; loading large charting libraries synchronously on the first paint | Always use stable identity `key`s. Virtualize lists with `>200` rows. Aggressively lazy-load heavy routes, modals, and charts via dynamic imports to minimize the initial main-thread blocking time and interaction delay |
