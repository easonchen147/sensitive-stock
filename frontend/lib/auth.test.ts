import { describe, expect, it } from "vitest";

describe("frontend auth helpers", () => {
  it("builds login redirect paths for protected routes", async () => {
    const authModule = await import("./auth").catch(() => null);

    expect(authModule?.buildLoginRedirectPath?.("/market")).toBe("/login?next=%2Fmarket");
    expect(authModule?.buildLoginRedirectPath?.("/")).toBe("/login?next=%2F");
  });

  it("marks only application pages as protected routes", async () => {
    const authModule = await import("./auth").catch(() => null);

    expect(authModule?.isProtectedAppPath?.("/")).toBe(true);
    expect(authModule?.isProtectedAppPath?.("/backtests")).toBe(true);
    expect(authModule?.isProtectedAppPath?.("/market")).toBe(true);
    expect(authModule?.isProtectedAppPath?.("/factors")).toBe(true);
    expect(authModule?.isProtectedAppPath?.("/portfolio")).toBe(true);
    expect(authModule?.isProtectedAppPath?.("/login")).toBe(false);
    expect(authModule?.isProtectedAppPath?.("/api/auth/login")).toBe(false);
    expect(authModule?.isProtectedAppPath?.("/_next/static/chunk.js")).toBe(false);
  });

  it("builds backend proxy paths under the frontend auth boundary", async () => {
    const authModule = await import("./auth").catch(() => null);

    expect(authModule?.buildBackendProxyPath?.("/api/v1/capabilities")).toBe(
      "/api/backend/capabilities",
    );
    expect(authModule?.buildBackendProxyPath?.("/api/v1/market/news")).toBe(
      "/api/backend/market/news",
    );
  });

  it("uses httpOnly cookie settings for the access token", async () => {
    const authModule = await import("./auth").catch(() => null);

    expect(authModule?.buildAccessTokenCookie?.("token-123", 3600, true)).toMatchObject({
      name: "sensitive_stock_access_token",
      value: "token-123",
      options: {
        httpOnly: true,
        sameSite: "lax",
        secure: true,
        path: "/",
        maxAge: 3600,
      },
    });
  });

  it("sanitizes next paths to avoid open redirects", async () => {
    const authModule = await import("./auth").catch(() => null);

    expect(authModule?.sanitizeNextPath?.("/market")).toBe("/market");
    expect(authModule?.sanitizeNextPath?.("https://evil.example")).toBe("/");
    expect(authModule?.sanitizeNextPath?.("//evil.example")).toBe("/");
    expect(authModule?.sanitizeNextPath?.("market")).toBe("/");
    expect(authModule?.sanitizeNextPath?.("/api/auth/login")).toBe("/");
  });
});
