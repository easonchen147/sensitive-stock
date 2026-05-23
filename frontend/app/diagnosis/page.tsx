import { DiagnosisWorkbench } from "@/components/research-workbenches";
import { WorkbenchHero } from "@/components/workbench-layout";
import { requireAuthenticatedPage } from "@/lib/server-auth";

export default async function DiagnosisPage() {
  await requireAuthenticatedPage("/diagnosis");

  return (
    <>
      <WorkbenchHero
        eyebrow="诊股报告"
        title="结构化诊股工作台"
        description="把行情上下文、技术指标、报告段落、风险提示和降级 metadata 放在同一张研究报告里。"
        metrics={[
          { label: "接口", value: "/diagnosis/run", note: "正式后端接口" },
          { label: "状态", value: "可降级", note: "部分报告仍可检查" },
        ]}
        meta={["行情上下文", "指标摘要", "风险提示"]}
      />
      <DiagnosisWorkbench />
    </>
  );
}
