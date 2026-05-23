import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import { resolveBackendApiBaseUrl } from "@/lib/api-base";
import { ACCESS_TOKEN_COOKIE_NAME } from "@/lib/auth";

export async function GET() {
  const cookieStore = await cookies();
  const accessToken = cookieStore.get(ACCESS_TOKEN_COOKIE_NAME)?.value;
  if (!accessToken) {
    return NextResponse.json(
      {
        error: {
          code: "authentication_required",
          message: "需要有效访问凭证。",
        },
      },
      { status: 401 },
    );
  }

  const upstream = await fetch(`${resolveBackendApiBaseUrl()}/api/v1/auth/session`, {
    cache: "no-store",
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });
  const responseBody = await upstream.json();
  const response = NextResponse.json(responseBody, { status: upstream.status });

  if (upstream.status === 401) {
    response.cookies.delete(ACCESS_TOKEN_COOKIE_NAME);
  }

  return response;
}
