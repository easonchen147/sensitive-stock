const DEFAULT_API_BASE = "http://localhost:5000";

export function resolveBackendApiBaseUrl(): string {
  return process.env.NEXT_PUBLIC_API_BASE_URL || DEFAULT_API_BASE;
}
