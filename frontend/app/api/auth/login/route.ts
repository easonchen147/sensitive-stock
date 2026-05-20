import { NextResponse } from "next/server";

import { resolveBackendApiBaseUrl } from "@/lib/api-base";
import { buildAccessTokenCookie } from "@/lib/auth";
import type { AuthLoginRequest, AuthLoginResponse } from "@/types/api";

export async function POST(request: Request) {
  const payload = (await request.json()) as AuthLoginRequest;
  const upstream = await fetch(`${resolveBackendApiBaseUrl()}/api/v1/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
    cache: "no-store",
  });

  const responseBody = await upstream.json();
  if (!upstream.ok) {
    return NextResponse.json(responseBody, { status: upstream.status });
  }

  const authPayload = responseBody as AuthLoginResponse;
  const cookie = buildAccessTokenCookie(
    authPayload.accessToken,
    authPayload.expiresIn,
    process.env.NODE_ENV === "production",
  );

  const response = NextResponse.json(authPayload);
  response.cookies.set(cookie.name, cookie.value, cookie.options);
  return response;
}
