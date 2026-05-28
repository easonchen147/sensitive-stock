import { AppShell } from "@/components/app-shell";
import { DailyReportView } from "@/components/daily-report";
import { requireAuthenticatedPage } from "@/lib/server-auth";

export default async function DailyPage() {
  await requireAuthenticatedPage("/daily");

  return (
    <AppShell>
      <DailyReportView />
    </AppShell>
  );
}
