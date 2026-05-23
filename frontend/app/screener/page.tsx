import { ScreenerWorkbench } from "@/components/research-workbenches";
import { WorkbenchHero } from "@/components/workbench-layout";
import { requireAuthenticatedPage } from "@/lib/server-auth";

export default async function ScreenerPage() {
  await requireAuthenticatedPage("/screener");

  return (
    <>
      <WorkbenchHero
        eyebrow="选股研究"
        title="条件选股工作台"
        description="结构化条件、自然语言解释、候选排序、导出字段和回测回灌契约共享同一套 OpenAPI 后端边界。"
        metrics={[
          { label: "接口", value: "/screener/run", note: "正式后端接口" },
          { label: "复用", value: "导出 + 回测", note: "包含交接请求体" },
        ]}
        meta={["结构化条件", "语义解释", "回测交接"]}
      />
      <ScreenerWorkbench />
    </>
  );
}
