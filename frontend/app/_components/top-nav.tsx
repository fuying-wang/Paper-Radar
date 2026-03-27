import Link from "next/link";

const links = [
  { href: "/", label: "Dashboard" },
  { href: "/healthcare-ai", label: "Healthcare AI" },
  { href: "/general-ai-frontier", label: "General AI Frontier" },
  { href: "/crossovers", label: "Crossovers" },
  { href: "/journals", label: "Journals" },
  { href: "/conferences", label: "Conferences" },
  { href: "/social-buzz", label: "Social Buzz" },
  { href: "/watchlists", label: "Watchlists" },
];

export default function TopNav() {
  return (
    <header className="border-b border-slate-200 bg-white">
      <nav className="mx-auto flex w-full max-w-6xl flex-wrap items-center gap-2 px-6 py-4">
        {links.map((link) => (
          <Link
            key={link.href}
            href={link.href}
            className="rounded-lg px-3 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-100 hover:text-slate-900"
          >
            {link.label}
          </Link>
        ))}
      </nav>
    </header>
  );
}
