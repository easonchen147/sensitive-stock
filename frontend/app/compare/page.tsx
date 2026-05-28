import { StockCompareView } from "@/components/stock-compare";
import { requireAuthenticatedPage } from "@/lib/server-auth";

export default async function ComparePage() {
  await requireAuthenticatedPage("/compare");

  return <StockCompareView />;
}
