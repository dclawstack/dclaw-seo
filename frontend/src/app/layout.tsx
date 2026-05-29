import type { Metadata } from "next";
import localFont from "next/font/local";
import "./globals.css";
import { CopilotWidget } from "@/components/copilot-widget";

// Poppins bundled locally (woff2 in src/fonts) — no build-time network fetch.
const poppins = localFont({
  variable: "--font-poppins",
  display: "swap",
  src: [
    { path: "../fonts/poppins-300.woff2", weight: "300", style: "normal" },
    { path: "../fonts/poppins-400.woff2", weight: "400", style: "normal" },
    { path: "../fonts/poppins-500.woff2", weight: "500", style: "normal" },
    { path: "../fonts/poppins-600.woff2", weight: "600", style: "normal" },
    { path: "../fonts/poppins-700.woff2", weight: "700", style: "normal" },
    { path: "../fonts/poppins-800.woff2", weight: "800", style: "normal" },
  ],
});

export const metadata: Metadata = {
  title: "DClaw SEO",
  description: "Rank higher with AI",
  icons: {
    icon: [
      { url: "/favicon.svg", type: "image/svg+xml" },
      { url: "/favicon-32x32.png", sizes: "32x32", type: "image/png" },
      { url: "/favicon-16x16.png", sizes: "16x16", type: "image/png" },
    ],
    shortcut: "/favicon.png",
    apple: [{ url: "/apple-touch-icon.png", sizes: "180x180", type: "image/png" }],
  },
  manifest: "/site.webmanifest",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={poppins.variable}>
      <body
        className="min-h-screen bg-bg-muted font-sans text-fg-1"
        style={{ fontFamily: "var(--font-poppins), var(--dk-font-sans)" }}
      >
        {children}
        <CopilotWidget />
      </body>
    </html>
  );
}
