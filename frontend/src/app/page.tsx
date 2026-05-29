import Link from "next/link";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8">
      <h1 className="text-4xl font-bold text-brand mb-4">DClaw SEO</h1>
      <p className="text-lg text-fg-1 mb-8">Rank higher with AI</p>
      <Link
        href="/dashboard"
        className="px-6 py-3 bg-brand text-fg-on-brand rounded-pill shadow-brand hover:bg-brand-hover transition-colors duration-base ease-out-quart"
      >
        Go to Dashboard
      </Link>
    </main>
  );
}
