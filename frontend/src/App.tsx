import { createBrowserRouter, RouterProvider } from "react-router";
import Layout from "./components/Layout";
import { missingConfig } from "./config";
import About from "./pages/About";
import Account from "./pages/Account";
import Home from "./pages/Home";
import Lab from "./pages/Lab";
import Phone from "./pages/Phone";

const router = createBrowserRouter([
  {
    path: "/",
    element: <Layout />,
    children: [
      { index: true, element: <Home /> },
      { path: "phone", element: <Phone /> },
      { path: "lab", element: <Lab /> },
      { path: "about", element: <About /> },
      { path: "account", element: <Account /> },
    ],
  },
]);

export default function App() {
  const missing = missingConfig();
  if (missing.length > 0) {
    const names = missing
      .map((key) => `VITE_${key.replace(/[A-Z]/g, (letter) => `_${letter}`).toUpperCase()}`)
      .join(", ");
    return (
      <main className="min-h-dvh bg-bg p-8 font-sans text-ink">
        <p className="font-mono text-accent">ARHV</p>
        <h1 className="mt-5 text-3xl font-semibold">Configuration needed</h1>
        <p className="mt-3 max-w-xl text-muted">
          This build is missing: {names}. Run <code className="font-mono text-accent">make web-env</code>, rebuild, and reload.
        </p>
      </main>
    );
  }
  return <RouterProvider router={router} />;
}
