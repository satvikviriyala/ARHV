import { Link, Outlet } from "react-router";

export default function Layout() {
  return (
    <div className="min-h-dvh bg-bg font-sans text-ink">
      <header className="border-b border-line">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-5 py-4">
          <Link to="/" className="font-mono text-xl font-semibold tracking-widest text-accent">
            ARHV
          </Link>
          <nav className="flex gap-4 text-sm text-muted">
            <Link to="/" className="hover:text-ink">
              Demo
            </Link>
            <Link to="/lab" className="hover:text-ink">
              Lab
            </Link>
            <Link to="/about" className="hover:text-ink">
              About
            </Link>
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-5 py-8">
        <Outlet />
      </main>
      <footer className="border-t border-line px-5 py-6 text-center text-sm text-muted">
        <p>ARHV · fictional demo · built on AWS</p>
        <a className="text-accent hover:underline" href="https://github.com/satvikviriyala/ARHV" target="_blank" rel="noreferrer">
          Public source
        </a>
      </footer>
    </div>
  );
}
