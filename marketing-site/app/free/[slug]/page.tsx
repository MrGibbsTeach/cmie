import { notFound } from "next/navigation";
import { getAllLeadMagnets, getLeadMagnet } from "@/lib/lead-magnets";
import { LeadMagnetForm } from "./LeadMagnetForm";

export async function generateStaticParams() {
  return getAllLeadMagnets().map((lm) => ({ slug: lm.slug }));
}

export default async function FreeLeadMagnetPage(
  props: PageProps<"/free/[slug]">
) {
  const { slug } = await props.params;
  const leadMagnet = getLeadMagnet(slug);
  if (!leadMagnet) notFound();

  return (
    <div className="max-w-xl mx-auto px-6 py-16">
      <p className="text-xs font-medium text-blue-600 mb-2">
        Free lesson sample — {leadMagnet.unitTitle.split(":")[0]}
      </p>
      <h1 className="text-2xl font-bold tracking-tight mb-4">
        {leadMagnet.lessonTopic}
      </h1>
      <p className="text-slate-600 mb-8">
        A complete, ready-to-teach lesson — slides, activities, and
        objectives included. Enter your email and it's yours instantly.
      </p>
      <LeadMagnetForm slug={leadMagnet.slug} filename={leadMagnet.filename} />
    </div>
  );
}
