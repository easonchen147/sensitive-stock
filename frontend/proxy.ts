import { NextRequest, NextResponse } from "next/server";

import { ACCESS_TOKEN_COOKIE_NAME, buildLoginRedirectPath, isProtectedAppPath } from "@/lib/auth";

export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;
  if (!isProtectedAppPath(pathname)) {
    return NextResponse.next();
  }

  const accessToken = request.cookies.get(ACCESS_TOKEN_COOKIE_NAME)?.value;
  if (accessToken) {
    return NextResponse.next();
  }

  const loginUrl = new URL(buildLoginRedirectPath(pathname), request.url);
  return NextResponse.redirect(loginUrl);
}
