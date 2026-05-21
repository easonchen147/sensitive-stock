import { spawn, spawnSync } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";

const frontendRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const repoRoot = path.resolve(frontendRoot, "..");
const backendRoot = path.join(repoRoot, "backend");
const backendPort = Number(process.env.BACKEND_SMOKE_PORT || 5311);
const frontendPort = Number(process.env.FRONTEND_SMOKE_PORT || 3311);
const backendBaseUrl = `http://127.0.0.1:${backendPort}`;
const frontendBaseUrl = `http://127.0.0.1:${frontendPort}`;
const children = new Set();

function command(name) {
  return process.platform === "win32" ? `${name}.cmd` : name;
}

function spawnLogged(label, commandName, args, options = {}) {
  const child = spawn(commandName, args, {
    ...options,
    stdio: ["ignore", "pipe", "pipe"],
  });
  children.add(child);
  child.stdout.on("data", (chunk) => process.stdout.write(`[${label}] ${chunk}`));
  child.stderr.on("data", (chunk) => process.stderr.write(`[${label}] ${chunk}`));
  child.on("exit", (code, signal) => {
    children.delete(child);
    if (code && !shuttingDown) {
      console.error(`[${label}] exited with code ${code}${signal ? ` (${signal})` : ""}`);
      shutdown(code);
    }
  });
  return child;
}

async function waitForUrl(url, label, timeoutMs = 60_000) {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    try {
      const response = await fetch(url);
      if (response.ok) {
        return;
      }
    } catch {
      // Service is not ready yet.
    }
    await new Promise((resolve) => setTimeout(resolve, 500));
  }
  throw new Error(`${label} did not become ready at ${url}`);
}

let shuttingDown = false;
function shutdown(code = 0) {
  shuttingDown = true;
  for (const child of children) {
    killChildTree(child);
  }
  process.exit(code);
}

function killChildTree(child) {
  if (!child.pid) {
    return;
  }

  if (process.platform === "win32") {
    spawnSync("taskkill", ["/pid", String(child.pid), "/t", "/f"], { stdio: "ignore" });
    return;
  }

  child.kill("SIGTERM");
}

process.on("SIGINT", () => shutdown(0));
process.on("SIGTERM", () => shutdown(0));
process.on("exit", () => {
  for (const child of children) {
    killChildTree(child);
  }
});

const backend = spawnLogged(
  "backend",
  "uv",
  ["run", "flask", "--app", "wsgi", "run", "--host", "127.0.0.1", "--port", String(backendPort)],
  {
    cwd: backendRoot,
    env: {
      ...process.env,
      BACKEND_ENV: "testing",
      BACKEND_HTTP_TIMEOUT: "2",
      BACKEND_CORS_ORIGINS: frontendBaseUrl,
      FLASK_DEBUG: "0",
    },
  },
);

await waitForUrl(`${backendBaseUrl}/api/v1/health`, "backend");

const frontendCommand = process.platform === "win32" ? "cmd.exe" : command("npx");
const frontendArgs =
  process.platform === "win32"
    ? [
        "/d",
        "/s",
        "/c",
        "npx",
        "next",
        "start",
        "--hostname",
        "127.0.0.1",
        "--port",
        String(frontendPort),
      ]
    : ["next", "start", "--hostname", "127.0.0.1", "--port", String(frontendPort)];

spawnLogged("frontend", frontendCommand, frontendArgs, {
  cwd: frontendRoot,
  env: {
    ...process.env,
    NEXT_PUBLIC_API_BASE_URL: backendBaseUrl,
    NEXT_TELEMETRY_DISABLED: "1",
  },
});

await waitForUrl(frontendBaseUrl, "frontend", 90_000);

console.log(`[smoke] ready at ${frontendBaseUrl} with backend ${backend.pid}`);
setInterval(() => undefined, 60_000);
