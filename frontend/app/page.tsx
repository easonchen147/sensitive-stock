import Link from "next/link";

import { WorkbenchHero } from "@/components/workbench-layout";
import { getCapabilitiesServer } from "@/lib/server-api";
import { requireAuthenticatedPage } from "@/lib/server-auth";

const LIVE_ENTRIES = [
  { href: "/screener", title: "Screener", copy: "Run structured screens and hand results to backtests." },
  { href: "/diagnosis", title: "Diagnosis", copy: "Generate structured market-context diagnosis reports." },
  { href: "/factors", title: "Factors", copy: "Analyze factor snapshots and IC rankings." },
  { href: "/portfolio", title: "Portfolio", copy: "Optimize allocations for a selected basket." },
];

export default async function HomePage() {
  await requireAuthenticatedPage("/");
  const capabilities = await getCapabilitiesServer();
  const migrated = capabilities.filter((item) => item.status === "migrated");
  const skeletons = capabilities.filter((item) => item.status !== "migrated");

  return (
    <>
      <WorkbenchHero
        eyebrow="Research Cockpit"
        title="A-share research workbench"
        description="Auth, market intelligence, AKQuant backtests, screening, diagnosis, factor analysis, and portfolio optimization now converge through Flask APIs and the shared OpenAPI contract."
        metrics={[
          {
            label: "Migrated",
            value: migrated.length,
            note: "Capabilities with real backend routes.",
          },
          {
            label: "Skeleton",
            value: skeletons.length,
            note: "Capabilities still marked as placeholders.",
          },
        ]}
        meta={["Quiet Capital Terminal", "OpenAPI governed", "Protected routes"]}
      />

      <section className="dashboard-grid">
        <aside className="panel">
          <div className="eyebrow">New Workbenches</div>
          <h2 className="panel-title">Research loops</h2>
          <div className="action-grid">
            {LIVE_ENTRIES.map((item) => (
              <Link className="action-card" href={item.href} key={item.href}>
                <strong>{item.title}</strong>
                <p>{item.copy}</p>
              </Link>
            ))}
          </div>
        </aside>

        <article className="panel">
          <div className="eyebrow">Capability Truth Map</div>
          <h2 className="panel-title">Backend capability inventory</h2>
          <div className="status-list">
            {capabilities.map((capability) => (
              <div className="status-item" data-status={capability.status} key={capability.name}>
                <div className="status-head">
                  <strong>{capability.label}</strong>
                  <span className="status-pill">{capability.status}</span>
                </div>
                <p>{capability.summary}</p>
              </div>
            ))}
          </div>
        </article>

        <article className="panel">
          <div className="eyebrow">Contract</div>
          <h2 className="panel-title">OpenAPI is the source of truth</h2>
          <div className="status-list">
            <div className="placeholder-item">Runtime discovery: /api/v1/openapi.json</div>
            <div className="placeholder-item">Static artifact: openapi.json</div>
            <div className="placeholder-item">
              Protected business APIs use the shared bearerAuth security scheme.
            </div>
          </div>
        </article>
      </section>
    </>
  );
}
