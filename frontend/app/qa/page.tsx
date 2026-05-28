import { AppShell } from "@/components/app-shell";
import { StockQAChat } from "@/components/stock-qa";
import { requireAuthenticatedPage } from "@/lib/server-auth";

export default async function QAPage() {
  await requireAuthenticatedPage("/qa");

  return (
    <AppShell>
      <StockQAChat />
    </AppShell>
  );
}
