"use client";

import { useState } from "react";

export function LeadMagnetForm({
  slug,
  filename,
}: {
  slug: string;
  filename: string;
}) {
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState<"idle" | "loading" | "done" | "error">(
    "idle"
  );

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setStatus("loading");
    try {
      const res = await fetch("/api/subscribe", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, slug }),
      });
      if (!res.ok) throw new Error("failed");
      setStatus("done");
    } catch {
      setStatus("error");
    }
  }

  if (status === "done") {
    return (
      <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-6">
        <p className="font-medium text-emerald-900 mb-3">
          You're in! Your download is ready.
        </p>
        <a
          href={`/downloads/${filename}`}
          className="inline-block px-5 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-sm font-medium transition-colors"
        >
          Download the lesson
        </a>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-3">
      <input
        type="email"
        required
        placeholder="you@school.edu"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        className="flex-1 rounded-lg border border-slate-300 px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
      <button
        type="submit"
        disabled={status === "loading"}
        className="px-5 py-2.5 bg-blue-600 hover:bg-blue-500 disabled:opacity-60 text-white rounded-lg text-sm font-medium transition-colors whitespace-nowrap"
      >
        {status === "loading" ? "Sending..." : "Get the free lesson"}
      </button>
      {status === "error" && (
        <p className="text-sm text-red-600 sm:absolute sm:mt-12">
          Something went wrong — try again.
        </p>
      )}
    </form>
  );
}
