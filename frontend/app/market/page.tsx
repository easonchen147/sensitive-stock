import { MarketWorkbench } from "@/components/market-workbench";
import { WorkbenchHero } from "@/components/workbench-layout";
import { requireAuthenticatedPage } from "@/lib/server-auth";

export default async function MarketPage() {
  await requireAuthenticatedPage("/market");

  return (
    <>
      <WorkbenchHero
        eyebrow="行情情报"
        title="行情与快讯工作台"
        description="直接消费后端 market/news 接口，展示 AkShare 报价、热门板块、多源快讯、DeepSeek 预测、历史复盘和评估结果。"
        metrics={[
          { label: "行情来源", value: "AkShare", note: "报价与板块数据" },
          { label: "资讯来源", value: "多源聚合", note: "降级状态显式展示" },
        ]}
        meta={["实时接口", "规则情报", "来源质量", "预测评估"]}
      />

      <MarketWorkbench />
    </>
  );
}
