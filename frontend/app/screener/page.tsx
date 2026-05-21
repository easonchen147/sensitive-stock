import { ScreenerWorkbench } from "@/components/research-workbenches";
import { WorkbenchHero } from "@/components/workbench-layout";
import { requireAuthenticatedPage } from "@/lib/server-auth";

export default async function ScreenerPage() {
  await requireAuthenticatedPage("/screener");

  return (
    <>
      <WorkbenchHero
        eyebrow="Screener"
        title="条件选股工作台"
        description="结构化条件、自然语言解释、候选排序、导出字段和回测回灌契约共享同一套 OpenAPI 后端边界。"
        metrics={[
          { label: "Endpoint", value: "/screener/run", note: "formal API" },
          { label: "Reuse", value: "export + backtest", note: "handoff payload included" },
        ]}
        meta={["Structured filters", "Prompt interpretation", "Backtest handoff"]}
      />
      <ScreenerWorkbench />
    </>
  );
}
