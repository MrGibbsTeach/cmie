import leadMagnets from "@/lib/lead-magnets.json";

export default function HomePage() {
  return (
    <div className="max-w-3xl mx-auto px-6 py-16">
      <h1 className="text-3xl font-bold tracking-tight mb-3">
        Free Digital Technologies lesson samples
      </h1>
      <p className="text-slate-600 mb-10 max-w-xl">
        Ready-to-teach lessons for Years 7–10, aligned to real classroom
        practice. Pick a free sample below — no prep required.
      </p>

      <div className="grid gap-4 sm:grid-cols-2">
        {leadMagnets.map((lm) => (
          <a
            key={lm.slug}
            href={`/free/${lm.slug}`}
            className="block rounded-xl border border-slate-200 bg-white p-5 hover:border-slate-400 hover:shadow-sm transition-all"
          >
            <p className="text-xs font-medium text-blue-600 mb-1">
              {lm.unitTitle.split(":")[0]}
            </p>
            <p className="font-semibold text-slate-900 leading-snug">
              {lm.lessonTopic}
            </p>
          </a>
        ))}
      </div>
    </div>
  );
}
