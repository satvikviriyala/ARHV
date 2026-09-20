export default function Lab() {
  return (
    <section className="mx-auto max-w-3xl space-y-5">
      <p className="font-mono text-sm tracking-widest text-accent">RED-TEAM LAB</p>
      <h1 className="text-4xl font-semibold">The agent benchmark runs from the terminal.</h1>
      <p className="text-lg text-muted">
        Phase 3's asynchronous Bedrock worker is intentionally cut from this sprint UI. Run
        <code className="mx-1 rounded bg-surface-2 px-1 font-mono text-accent">make bench BACKEND=bedrock</code>
        to attack the same motion puzzle and record real results.
      </p>
    </section>
  );
}
