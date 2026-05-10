# Noesis Dashboard UI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a simple working Next.js dashboard in `ui` with a Noesis header, topic form, selectable source tags, previous artifacts, and process logs that replace the form after generation.

**Architecture:** Create a small App Router Next.js app with one client component for dashboard state. Keep static artifact and source-preset data inside the component file because the current scope is a standalone UI prototype.

**Tech Stack:** Next.js, TypeScript, Tailwind CSS, Vitest, Testing Library, lucide-react.

---

### Task 1: Scaffold UI App

**Files:**
- Create: `ui/package.json`
- Create: `ui/next.config.mjs`
- Create: `ui/tsconfig.json`
- Create: `ui/postcss.config.mjs`
- Create: `ui/tailwind.config.ts`
- Create: `ui/vitest.config.ts`
- Create: `ui/src/test/setup.ts`
- Create: `ui/src/app/layout.tsx`
- Create: `ui/src/app/page.tsx`
- Create: `ui/src/app/globals.css`

- [ ] **Step 1: Add package and config files**

Use scripts: `dev`, `build`, `test`, `test:run`, and dependencies for Next.js, React, Tailwind, Vitest, Testing Library, jsdom, and lucide-react.

- [ ] **Step 2: Add App Router files**

`page.tsx` should render `<NoesisDashboard />`. `layout.tsx` should import `globals.css`.

### Task 2: Dashboard Behavior Test

**Files:**
- Create: `ui/src/components/noesis-dashboard.test.tsx`
- Create: `ui/src/components/noesis-dashboard.tsx`

- [ ] **Step 1: Write failing tests**

Test that the default dashboard shows the header actions, add button, and previous artifacts. Test that clicking add shows form fields from the spec. Test that selecting source tags and submitting replaces the form with all process logs.

- [ ] **Step 2: Run test to verify it fails**

Run: `npm test -- --run src/components/noesis-dashboard.test.tsx`

Expected: fail because `NoesisDashboard` is not implemented.

- [ ] **Step 3: Implement dashboard**

Build a client component with:
- Header containing Noesis logo, settings icon button, and help icon button.
- Main dashboard with an add-new-topic action at the start and artifact cards beside it.
- Modal/panel opened by add button.
- Typical form with `Topic`, `Source presets` as compact selectable tags, `Optional evidence`, and `Generate artifact` submit.
- Submit or Enter replaces the form panel content with logs: `Collecting sources`, `Normalizing material`, `Preparing evidence`, `Drafting handbook`, `Finalizing artifact`, `Handbook ready`.

- [ ] **Step 4: Run tests to verify pass**

Run: `npm test -- --run src/components/noesis-dashboard.test.tsx`

Expected: pass.

### Task 3: Styling And Verification

**Files:**
- Modify: `ui/src/app/globals.css`
- Modify: `ui/src/components/noesis-dashboard.tsx`

- [ ] **Step 1: Apply visual polish**

Use a white minimal dashboard, Agrandir-like typography fallback, subtle ink/accent colors, compact tags, clean icon buttons, and restrained motion. Avoid landing-page hero treatment and avoid strong forced themes.

- [ ] **Step 2: Run full verification**

Run:
```powershell
npm test -- --run
npm run build
```

Expected: tests pass and Next.js build exits 0.
