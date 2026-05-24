import { afterEach, describe, expect, it } from "vitest";

import { clearFrontendFileEnvCache } from "./file-env";
import { resolveBackendApiBaseUrl } from "./api-base";

describe("frontend file env config", () => {
  afterEach(() => {
    clearFrontendFileEnvCache();
  });

  it("reads NEXT_PUBLIC_API_BASE_URL from frontend .env file", () => {
    expect(resolveBackendApiBaseUrl()).toBe("http://localhost:5000");
  });
});
