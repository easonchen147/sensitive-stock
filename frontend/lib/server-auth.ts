import "server-only";

import { cookies } from "next/headers";
import { redirect } from "next/navigation";

import { resolveBackendApiBaseUrl } from "@/lib/api-base";
import { ACCESS_TOKEN_COOKIE_NAME, buildLoginRedirectPath } from "@/lib/auth";
import type { AuthSession } from "@/types/api";

export async function requireAuthenticatedPage(pathname: string): Promise<AuthSession> {
  const token = await getServerAccessToken();
  if (!token) {
    redirect(buildLoginRedirectPath(pathname));
  }

  const response = await fetch(`${resolveBackendApiBaseUrl()}/api/v1/auth/session`, {
    cache: "no-store",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (response.status === 401) {
    redirect(buildLoginRedirectPath(pathname));
  }

  if (!response.ok) {
    throw new Error(`会话请求失败，状态码 ${response.status}`);
  }

  return (await response.json()) as AuthSession;
}

export async function redirectIfAuthenticated(): Promise<void> {
  const token = await getServerAccessToken();
  if (!token) {
    return;
  }

  const response = await fetch(`${resolveBackendApiBaseUrl()}/api/v1/auth/session`, {
    cache: "no-store",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (response.ok) {
    redirect("/");
  }
}

export async function getServerAccessToken(): Promise<string> {
  const cookieStore = await cookies();
  return cookieStore.get(ACCESS_TOKEN_COOKIE_NAME)?.value || "";
}
