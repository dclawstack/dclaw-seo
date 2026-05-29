"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

const nav = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/audit", label: "Audit" },
  { href: "/keywords", label: "Keywords" },
  { href: "/content", label: "Content" },
  { href: "/rankings", label: "Rankings" },
  { href: "/backlinks", label: "Backlinks" },
  { href: "/competitor", label: "Competitor" },
  { href: "/brief", label: "Content Brief" },
  { href: "/performance", label: "Performance" },
  { href: "/settings", label: "Settings" },
];

export function Navbar() {
  const pathname = usePathname();
  return (
    <nav className="w-64 min-h-screen bg-bg border-r border-border p-4">
      <div className="mb-8">
        <div className="flex items-center gap-2">
          <img src="/brand/logos/dclaw-icon-purple.svg" alt="" className="h-8 w-8" />
          <h1 className="text-xl font-bold text-brand">DClaw SEO</h1>
        </div>
        <p className="text-xs text-fg-2">Rank higher with AI</p>
      </div>
      <ul className="space-y-1">
        {nav.map((item) => (
          <li key={item.href}>
            <Link
              href={item.href}
              className={cn(
                "block px-3 py-2 rounded-md text-sm font-medium transition",
                pathname === item.href
                  ? "bg-brand-soft text-brand-press"
                  : "text-fg-1 hover:bg-bg-muted"
              )}
            >
              {item.label}
            </Link>
          </li>
        ))}
      </ul>
    </nav>
  );
}
