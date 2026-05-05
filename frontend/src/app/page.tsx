import Link from "next/link";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8">
      <h1 className="text-4xl font-bold text-emerald-600 mb-4">DClaw SEO</h1>
      <p className="text-lg text-gray-600 mb-8">Rank higher with AI</p>
      <Link
        href="/dashboard"
        className="px-6 py-3 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition"
      >
        Go to Dashboard
      </Link>
    </main>
  );
}
