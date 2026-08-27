import data from "./lead-magnets.json";

export type LeadMagnet = {
  slug: string;
  unitId: string;
  unitTitle: string;
  lessonNumber: number;
  lessonTopic: string;
  filename: string;
  bundleUrl: string;
};

const leadMagnets = data as LeadMagnet[];

export function getLeadMagnet(slug: string): LeadMagnet | undefined {
  return leadMagnets.find((lm) => lm.slug === slug);
}

export function getAllLeadMagnets(): LeadMagnet[] {
  return leadMagnets;
}
