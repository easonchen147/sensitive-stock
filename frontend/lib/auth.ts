export const ACCESS_TOKEN_COOKIE_NAME = "sensitive_stock_access_token";

export type AccessTokenCookie = {
  name: string;
  value: string;
  options: {
    httpOnly: boolean;
    sameSite: "lax";
    secure: boolean;
    path: string;
    maxAge: number;
  };
};

const PROTECTED_APP_PATHS = new Set([
  "/",
  "/backtests",
  "/market",
  "/screener",
  "/diagnosis",
  "/factors",
  "/portfolio",
  "/daily",
  "/qa",
  "/watchlist",
  "/compare",
]);

export function buildLoginRedirectPath(pathname: string): string {
  return `/login?next=${encodeURIComponent(pathname)}`;
}

export function isProtectedAppPath(pathname: string): boolean {
  if (pathname.startsWith("/api/") || pathname.startsWith("/_next/")) {
    return false;
  }

  return PROTECTED_APP_PATHS.has(pathname);
}

export function buildBackendProxyPath(backendPath: string): string {
  return backendPath.replace(/^\/api\/v1/, "/api/backend");
}

export function buildAccessTokenCookie(
  token: string,
  maxAge: number,
  secure: boolean,
): AccessTokenCookie {
  return {
    name: ACCESS_TOKEN_COOKIE_NAME,
    value: token,
    options: {
      httpOnly: true,
      sameSite: "lax",
      secure,
      path: "/",
      maxAge,
    },
  };
}

export function sanitizeNextPath(value: string | null | undefined): string {
  if (!value || !value.startsWith("/") || value.startsWith("//") || value.startsWith("/api/")) {
    return "/";
  }

  return value;
}
