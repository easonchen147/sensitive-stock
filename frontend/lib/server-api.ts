import "server-only";

import { resolveBackendApiBaseUrl } from "@/lib/api-base";
import { getOpenApiBinding } from "@/lib/openapi-client";
import { getServerAccessToken } from "@/lib/server-auth";
import type { CapabilitiesResponse, Capability } from "@/types/api";

export async function getCapabilitiesServer(): Promise<Capability[]> {
  const token = await getServerAccessToken();
  const endpoint = getOpenApiBinding("capabilities");
  const response = await fetch(`${resolveBackendApiBaseUrl()}${endpoint.path}`, {
    cache: "no-store",
    method: endpoint.method,
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error(`${endpoint.path} 请求失败，状态码 ${response.status}`);
  }

  const payload = (await response.json()) as CapabilitiesResponse;
  return payload.items;
}
