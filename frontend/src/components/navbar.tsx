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
  { href: "/settings", label: "Settings" },
];

export function Navbar() {
  const pathname = usePathname();
  return (
    <nav className="w-64 min-h-screen bg-white border-r border-gray-200 p-4">
      <div className="mb-8">
        <h1 className="text-xl font-bold text-emerald-600">DClaw SEO</h1>
        <p className="text-xs text-gray-500">Rank higher with AI</p>
      </div>
      <ul className="space-y-1">
        {nav.map((item) => (
          <li key={item.href}>
            <Link
              href={item.href}
              className={cn(
                "block px-3 py-2 rounded-md text-sm font-medium transition",
                pathname === item.href
                  ? "bg-emerald-50 text-emerald-700"
                  : "text-gray-700 hover:bg-gray-50"
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
