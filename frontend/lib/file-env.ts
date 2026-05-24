import { readFileSync } from "node:fs";

const FRONTEND_ENV_FILE = ".env";

function parseEnvText(text: string): Record<string, string> {
  const values: Record<string, string> = {};

  for (const rawLine of text.split(/\r?\n/)) {
    let line = rawLine.trim();
    if (!line || line.startsWith("#")) {
      continue;
    }
    if (line.startsWith("export ")) {
      line = line.slice(7).trim();
    }
    const separatorIndex = line.indexOf("=");
    if (separatorIndex <= 0) {
      continue;
    }

    const key = line.slice(0, separatorIndex).trim();
    let value = line.slice(separatorIndex + 1).trim();
    if (!key) {
      continue;
    }

    if (
      (value.startsWith('"') && value.endsWith('"')) ||
      (value.startsWith("'") && value.endsWith("'"))
    ) {
      value = value.slice(1, -1);
    } else {
      const inlineCommentIndex = value.indexOf(" #");
      if (inlineCommentIndex >= 0) {
        value = value.slice(0, inlineCommentIndex).trimEnd();
      }
    }

    values[key] = value;
  }

  return values;
}

let cachedEnv: Record<string, string> | null = null;

export function clearFrontendFileEnvCache() {
  cachedEnv = null;
}

export function loadFrontendFileEnv(): Record<string, string> {
  if (cachedEnv) {
    return { ...cachedEnv };
  }

  const values: Record<string, string> = {};
  try {
    const text = readFileSync(FRONTEND_ENV_FILE, "utf-8");
    Object.assign(values, parseEnvText(text));
  } catch {
    // Ignore missing local config files and keep defaults.
  }

  cachedEnv = values;
  return { ...values };
}

export function getFrontendEnvValue(name: string, defaultValue: string): string {
  const fileEnv = loadFrontendFileEnv();
  return fileEnv[name] || defaultValue;
}
