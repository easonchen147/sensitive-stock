import { AppShell } from "@/components/app-shell";
import { WatchlistView } from "@/components/watchlist";
import { requireAuthenticatedPage } from "@/lib/server-auth";

export default async function WatchlistPage() {
  await requireAuthenticatedPage("/watchlist");

  return (
    <AppShell>
      <WatchlistView />
    </AppShell>
  );
}
