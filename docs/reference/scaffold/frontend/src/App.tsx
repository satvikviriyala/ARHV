import { SHAPE_IDS, SHAPE_LABELS, SHAPE_PATHS } from "./lib/shapes";

// Phase 0 placeholder. Phase 2 replaces this with the real router + pages (docs/FRONTEND.md).
export default function App() {
  return (
    <main className="min-h-dvh p-8 font-sans">
      <h1 className="text-3xl font-semibold text-accent">PACT scaffold OK</h1>
      <p className="mt-2 text-muted">Frontend toolchain works. Continue with docs/phases/PHASE_2_FRONTEND_M1.md.</p>
      <div className="mt-6 flex gap-4">
        {SHAPE_IDS.map((id) => (
          <svg key={id} viewBox="-1 -1 2 2" className="size-10 fill-ink" role="img" aria-label={SHAPE_LABELS[id]}>
            <path d={SHAPE_PATHS[id]} />
          </svg>
        ))}
      </div>
    </main>
  );
}
