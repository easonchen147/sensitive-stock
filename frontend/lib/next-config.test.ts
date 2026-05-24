import path from "node:path";

import { describe, expect, it } from "vitest";

import nextConfig from "../next.config";

describe("Next.js runtime config", () => {
  it("configures Turbopack with an absolute frontend root", () => {
    expect(nextConfig.turbopack?.root).toBeTruthy();
    expect(path.isAbsolute(nextConfig.turbopack?.root || "")).toBe(true);
    expect(nextConfig.turbopack?.root?.replaceAll("\\", "/")).toMatch(/\/frontend$/);
  });
});
