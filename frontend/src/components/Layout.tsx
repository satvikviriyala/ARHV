import { Link, Outlet } from "react-router";

export default function Layout() {
  return (
    <div className="min-h-dvh bg-bg font-sans text-ink">
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-50 focus:rounded-lg focus:bg-accent focus:px-3 focus:py-2 focus:font-semibold focus:text-bg"
      >
        Skip to content
      </a>
      <header className="border-b border-line">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-4 px-5 py-4">
          <Link
            to="/"
            className="font-mono text-xl font-semibold tracking-widest text-accent focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
          >
            ARHV
          </Link>
          <nav className="flex flex-wrap gap-x-4 gap-y-2 text-sm text-muted" aria-label="Primary navigation">
            <Link to="/" className="hover:text-ink focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent">
              Demo
            </Link>
            <Link to="/phone" className="hover:text-ink focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent">
              Phone check
            </Link>
            <Link to="/lab" className="hover:text-ink focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent">
              Lab
            </Link>
            <Link to="/about" className="hover:text-ink focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent">
              About
            </Link>
          </nav>
        </div>
      </header>
      <main id="main-content" className="mx-auto max-w-6xl px-5 py-8">
        <Outlet />
      </main>
      <footer className="border-t border-line px-5 py-6 text-center text-sm text-muted">
        <p>ARHV · fictional demo · built on AWS</p>
        <a
          className="text-accent hover:underline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
          href="https://github.com/satvikviriyala/ARHV"
          target="_blank"
          rel="noreferrer"
        >
          Public source
        </a>
      </footer>
    </div>
  );
}
