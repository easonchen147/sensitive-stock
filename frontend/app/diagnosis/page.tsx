import { CapabilityPlaceholder } from "@/components/capability-placeholder";
import { requireAuthenticatedPage } from "@/lib/server-auth";

export default async function DiagnosisPage() {
  await requireAuthenticatedPage("/diagnosis");

  return (
    <CapabilityPlaceholder
      eyebrow="Skeleton Capability"
      title="AI 诊股入口已经迁到新导航里，但诊断引擎仍留在后续阶段。"
      summary="AI 诊股依赖实时行情、技术指标和模型提示词拼装。这一页当前只承担‘入口迁移 + 状态表达’职责，不伪装成已完成报告页。"
      status="skeleton"
      route="/diagnosis"
      availableNow={[
        "前端和 capability inventory 已保留 AI 诊股入口。",
        "backend 已预留 `/api/v1/diagnosis` route 边界，便于后续接入真实服务。",
        "市场数据主干已逐步迁到 backend，为诊断链路后续落地铺路。",
      ]}
      blockedBy={[
        "实时行情拉取、技术指标计算和提示词构建尚未迁入 backend service。",
        "前端问答交互、报告渲染与失败兜底视图还没有实现。",
        "模型调用配置与敏感信息管理还需要在新架构下重新收口。",
      ]}
      nextStep="等行情与指标服务继续稳定后，再迁移诊断 prompt 构建、问答容器和报告视图。"
    />
  );
}
