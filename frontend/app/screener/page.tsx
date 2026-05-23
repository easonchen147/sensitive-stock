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
        description="结构化条件、自然语言解释、候选排序、导出字段和回测交接共享同一套后端接口边界。"
        metrics={[
          { label: "执行链路", value: "选股筛选", note: "受保护服务" },
          { label: "复用", value: "导出 + 回测", note: "包含交接请求体" },
        ]}
        meta={["结构化条件", "语义解释", "回测交接"]}
      />
      <ScreenerWorkbench />
    </>
  );
}
