import { MarketWorkbench } from "@/components/market-workbench";
import { WorkbenchHero } from "@/components/workbench-layout";
import { requireAuthenticatedPage } from "@/lib/server-auth";

export default async function MarketPage() {
  await requireAuthenticatedPage("/market");

  return (
    <>
      <WorkbenchHero
        eyebrow="Market Intelligence"
        title="行情与快讯工作台"
        description="直接消费 backend market/news 接口，展示 AkShare 报价、热门板块、Jin10 快讯和规则式 intelligence 的真实返回结果。"
        metrics={[
          { label: "Source", value: "AkShare", note: "quotes and sectors" },
          { label: "News", value: "Jin10", note: "degraded state is explicit" },
        ]}
        meta={["Live API", "Rule-based intelligence", "Source metadata"]}
      />

      <MarketWorkbench />
    </>
  );
}
