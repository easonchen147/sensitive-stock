import { DiagnosisWorkbench } from "@/components/research-workbenches";
import { WorkbenchHero } from "@/components/workbench-layout";
import { requireAuthenticatedPage } from "@/lib/server-auth";

export default async function DiagnosisPage() {
  await requireAuthenticatedPage("/diagnosis");

  return (
    <>
      <WorkbenchHero
        eyebrow="Diagnosis"
        title="结构化诊股工作台"
        description="把行情上下文、技术指标、报告段落、风险提示和降级 metadata 放在同一张研究报告里。"
        metrics={[
          { label: "Endpoint", value: "/diagnosis/run", note: "formal API" },
          { label: "State", value: "degraded aware", note: "partial reports stay inspectable" },
        ]}
        meta={["Market context", "Indicator summary", "Risk notes"]}
      />
      <DiagnosisWorkbench />
    </>
  );
}
