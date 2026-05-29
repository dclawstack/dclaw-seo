import type { Metadata } from "next";
import { Poppins } from "next/font/google";
import "./globals.css";
import { CopilotWidget } from "@/components/copilot-widget";

const poppins = Poppins({
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700", "800"],
  variable: "--font-poppins",
  display: "swap",
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
