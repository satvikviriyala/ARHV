export default function About() {
  return (
    <article className="mx-auto max-w-3xl space-y-6">
      <p className="font-mono text-sm tracking-widest text-accent">ABOUT ARHV</p>
      <h1 className="text-4xl font-semibold">Screen puzzles are a losing race.</h1>
      <p className="text-lg leading-relaxed text-muted">
        Agents can read and drive a browser. ARHV adds a physical tier: a real phone moves through a fresh, server-randomised path and the server checks cross-sensor physics.
      </p>
      <div className="grid gap-4 md:grid-cols-3">
        <div className="rounded-2xl border border-line p-4">
          <h2 className="font-semibold">Perceptual</h2>
          <p className="mt-2 text-sm text-muted">Moving dots reveal a shape to human vision, not a screenshot.</p>
        </div>
        <div className="rounded-2xl border border-line p-4">
          <h2 className="font-semibold">Physical</h2>
          <p className="mt-2 text-sm text-muted">Gravity, tilt, gyro, timing, continuity, and targets are checked server-side.</p>
        </div>
        <div className="rounded-2xl border border-line p-4">
          <h2 className="font-semibold">Attested</h2>
          <p className="mt-2 text-sm text-muted">The proposal: an OS trusted overlay and a private vendor-signed gesture token.</p>
        </div>
      </div>
      <p className="rounded-2xl border border-accent p-5 text-sm">
        Honest limitation: browser sensor streams are unattested. A physics-consistent simulator can pass; that is the gap ARHV measures and proposes vendors close.
      </p>
    </article>
  );
}
