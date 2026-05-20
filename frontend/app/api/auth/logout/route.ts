import { NextResponse } from "next/server";

import { ACCESS_TOKEN_COOKIE_NAME } from "@/lib/auth";

export async function POST() {
  const response = NextResponse.json({ ok: true });
  response.cookies.delete(ACCESS_TOKEN_COOKIE_NAME);
  return response;
}
