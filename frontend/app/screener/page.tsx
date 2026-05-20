import { CapabilityPlaceholder } from "@/components/capability-placeholder";
import { requireAuthenticatedPage } from "@/lib/server-auth";

export default async function ScreenerPage() {
  await requireAuthenticatedPage("/screener");

  return (
    <CapabilityPlaceholder
      eyebrow="Skeleton Capability"
      title="选股入口已在新壳层里，但真实筛选链路还没迁进来。"
      summary="这一页继续保持诚实的 skeleton 状态。当前只保留新前端入口和后端 route 边界，不会假装东方财富自然语言选股已经在 Next.js 中可用了。"
      status="skeleton"
      route="/screener"
      availableNow={[
        "前端已有独立路由，不再依赖旧 Streamlit 的 session 跳页。",
        "backend 已预留 `/api/v1/screener` 能力入口，后续可在这里接管真实调用。",
        "capability inventory 会把 screener 明确标为 skeleton。",
      ]}
      blockedBy={[
        "东方财富指纹与自然语言选股请求链路尚未迁入 backend service。",
        "热搜问句、选股结果序列化与导出逻辑尚未迁入前端工作台。",
        "选股结果一键回灌回测的闭环还没有在新架构里补齐。",
      ]}
      nextStep="下一阶段把东方财富选股 service、热搜问句和回灌回测闭环迁进 backend + frontend。"
    />
  );
}
