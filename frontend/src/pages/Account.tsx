export default function Account() {
  return (
    <section className="mx-auto max-w-xl space-y-4">
      <p className="font-mono text-sm tracking-widest text-accent">ACCESSIBLE PATH</p>
      <h1 className="text-3xl font-semibold">Verify with a confirmed account</h1>
      <p className="text-muted">
        The Cognito account path is the non-cognitive alternative. It issues an account-assurance token with a daily Cedar quota.
      </p>
      <p className="rounded-2xl border border-line p-4 text-sm text-muted">Cognito UI is cut from today's sprint; the backend route and Cedar quota policy are shipped.</p>
    </section>
  );
}
