import { NextRequest, NextResponse } from "next/server";
import { getLeadMagnet } from "@/lib/lead-magnets";

export async function POST(request: NextRequest) {
  const { email, slug } = await request.json();

  if (typeof email !== "string" || !email.includes("@")) {
    return NextResponse.json({ error: "invalid email" }, { status: 400 });
  }

  const leadMagnet = typeof slug === "string" ? getLeadMagnet(slug) : undefined;
  const apiKey = process.env.BREVO_API_KEY;

  if (!apiKey) {
    // Fail open on the download, not the capture -- a misconfigured API
    // key should never block someone from getting the free lesson they
    // asked for. Logged so it's visible in Vercel's function logs.
    console.error("BREVO_API_KEY not set -- email not captured:", email);
    return NextResponse.json({ ok: true, captured: false });
  }

  const body: Record<string, unknown> = {
    email,
    updateEnabled: true,
  };
  // BREVO_LIST_ID is optional -- without it, contacts still land in Brevo's
  // main contact pool and are fully usable, just not pre-segmented into a
  // named list. Set it once a list exists, no code change needed.
  const listId = process.env.BREVO_LIST_ID;
  if (listId) body.listIds = [Number(listId)];
  if (leadMagnet) {
    body.attributes = { LEAD_MAGNET: leadMagnet.slug };
  }

  const res = await fetch("https://api.brevo.com/v3/contacts", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "api-key": apiKey,
    },
    body: JSON.stringify(body),
  });

  if (res.ok || res.status === 400) {
    // Brevo returns 400 duplicate_parameter for an already-subscribed
    // email -- they're genuinely already captured, treat it as success.
    return NextResponse.json({ ok: true, captured: true });
  }

  const text = await res.text();
  console.error("Brevo subscribe failed:", res.status, text);
  return NextResponse.json({ ok: true, captured: false });
}
