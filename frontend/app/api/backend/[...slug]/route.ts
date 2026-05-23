import { cookies } from "next/headers";
import { NextRequest, NextResponse } from "next/server";

import { resolveBackendApiBaseUrl } from "@/lib/api-base";
import { ACCESS_TOKEN_COOKIE_NAME } from "@/lib/auth";
import { isProtectedOpenApiPath } from "@/lib/openapi-client";

async function proxyToBackend(request: NextRequest, slug: string[]) {
  const backendPath = `/api/v1/${slug.join("/")}`;
  if (!isProtectedOpenApiPath(backendPath)) {
    return NextResponse.json(
      {
        error: {
          code: "unknown_openapi_route",
          message: "该后端路由未登记在前端接口绑定表中。",
        },
      },
      { status: 404 },
    );
  }

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

  const backendUrl = new URL(
    `${resolveBackendApiBaseUrl()}${backendPath}${request.nextUrl.search}`,
  );
  const init: RequestInit = {
    method: request.method,
    cache: "no-store",
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  };

  const contentType = request.headers.get("content-type");
  if (contentType) {
    init.headers = {
      ...init.headers,
      "Content-Type": contentType,
    };
  }

  if (request.method !== "GET" && request.method !== "HEAD") {
    init.body = await request.text();
  }

  const upstream = await fetch(backendUrl, init);
  const body = await upstream.text();
  const response = new NextResponse(body, { status: upstream.status });

  const responseContentType = upstream.headers.get("content-type");
  if (responseContentType) {
    response.headers.set("content-type", responseContentType);
  }

  if (upstream.status === 401) {
    response.cookies.delete(ACCESS_TOKEN_COOKIE_NAME);
  }

  return response;
}

export async function GET(request: NextRequest, context: { params: Promise<{ slug: string[] }> }) {
  const { slug } = await context.params;
  return proxyToBackend(request, slug);
}

export async function POST(
  request: NextRequest,
  context: { params: Promise<{ slug: string[] }> },
) {
  const { slug } = await context.params;
  return proxyToBackend(request, slug);
}
