import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "Ante-Nicene Fathers — Scripture Citation Analysis",
  description:
    "Interactive analysis of biblical citations across the Ante-Nicene Fathers corpus (volumes 1–9).",
};

const navLinks = [
  { href: "/", label: "Overview" },
  { href: "/books", label: "Books" },
  { href: "/authors", label: "Church Fathers" },
  { href: "/psalms", label: "Psalms" },
  { href: "/volumes", label: "Volumes" },
];

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-stone-50 text-stone-900 min-h-screen">
        <header className="bg-stone-800 text-stone-100">
          <div className="max-w-6xl mx-auto px-4 py-4 flex flex-col sm:flex-row sm:items-center gap-3">
            <div className="flex-1">
              <span className="font-semibold text-lg tracking-tight">ANF Citation Analysis</span>
              <span className="ml-2 text-stone-400 text-sm hidden sm:inline">
                Ante-Nicene Fathers · Scripture References
              </span>
            </div>
            <nav className="flex gap-4 text-sm">
              {navLinks.map(({ href, label }) => (
                <Link
                  key={href}
                  href={href}
                  className="text-stone-300 hover:text-white transition-colors"
                >
                  {label}
                </Link>
              ))}
            </nav>
          </div>
        </header>
        <main className="max-w-6xl mx-auto px-4 py-8">{children}</main>
        <footer className="border-t border-stone-200 mt-12 py-6 text-center text-stone-400 text-sm">
          Data sourced from the{" "}
          <span className="text-stone-600">Christian Classics Ethereal Library</span> ANF collection.
        </footer>
      </body>
    </html>
  );
}
