"use client";

import { useCallback, useEffect, useState } from "react";
import { toast } from "sonner";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { getWatchlist, addToWatchlist, updateWatchlistItem, removeFromWatchlist, getStockDetail } from "@/lib/api";
import type { WatchlistItem, WatchlistAddPayload } from "@/types/api";
import { SymbolLink } from "@/components/symbol-link";
import { AlertTriangle, BookmarkPlus, Pencil, RefreshCw, Trash2 } from "lucide-react";

interface EnrichedItem extends WatchlistItem {
  currentPrice?: number | null;
  changePercent?: number | null;
}

export function WatchlistView() {
  const [items, setItems] = useState<EnrichedItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editItem, setEditItem] = useState<EnrichedItem | null>(null);

  const fetchWatchlist = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getWatchlist();
      const base = data.items ?? [];

      // Enrich with live prices
      const enriched = await Promise.all(
        base.map(async (item) => {
          try {
            const detail = await getStockDetail(item.symbol);
            return {
              ...item,
              currentPrice: detail.price,
              changePercent: detail.changePercent,
              name: item.name || detail.name,
            };
          } catch {
            return { ...item };
          }
        }),
      );
      setItems(enriched);
    } catch (err) {
      setError(err instanceof Error ? err.message : "获取自选股失败");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchWatchlist(); }, [fetchWatchlist]);

  const handleDelete = async (symbol: string) => {
    try {
      await removeFromWatchlist(symbol);
      setItems((prev) => prev.filter((i) => i.symbol !== symbol));
      toast.success("已从自选股移除");
    } catch (err) {
      const msg = err instanceof Error ? err.message : "删除失败";
      setError(msg);
      toast.error(msg);
    }
  };

  const totalCost = items.reduce((s, i) => s + (i.cost_price ?? 0) * (i.shares ?? 0), 0);
  const totalMarket = items.reduce((s, i) => s + (i.currentPrice ?? 0) * (i.shares ?? 0), 0);
  const totalPnl = totalMarket - totalCost;

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="font-display text-2xl font-bold tracking-tight">自选股</h2>
          <p className="text-sm text-muted-foreground">管理关注的股票，追踪持仓成本与盈亏。</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={fetchWatchlist} disabled={loading}>
            <RefreshCw className={`mr-2 size-4 ${loading ? "animate-spin" : ""}`} />
            刷新
          </Button>
          <AddDialog
            open={dialogOpen}
            onOpenChange={setDialogOpen}
            onAdded={() => fetchWatchlist()}
          />
        </div>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertTriangle className="size-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Summary */}
      {items.length > 0 && (
        <div className="grid gap-4 sm:grid-cols-3">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-muted-foreground">持仓成本</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="font-display text-2xl font-bold">¥{totalCost.toLocaleString(undefined, { maximumFractionDigits: 0 })}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-muted-foreground">当前市值</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="font-display text-2xl font-bold">¥{totalMarket.toLocaleString(undefined, { maximumFractionDigits: 0 })}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-muted-foreground">浮动盈亏</CardTitle>
            </CardHeader>
            <CardContent>
              <div className={`font-display text-2xl font-bold ${totalPnl >= 0 ? "text-positive" : "text-negative"}`}>
                {totalPnl >= 0 ? "+" : ""}¥{totalPnl.toLocaleString(undefined, { maximumFractionDigits: 0 })}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Table */}
      <Card>
        <CardContent className="pt-4">
          {loading ? (
            <div className="space-y-3">
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-10 w-full" />
            </div>
          ) : items.length === 0 ? (
            <div className="py-12 text-center text-sm text-muted-foreground">
              暂无自选股，点击"添加"开始。
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>代码</TableHead>
                  <TableHead>名称</TableHead>
                  <TableHead className="text-right">现价</TableHead>
                  <TableHead className="text-right">涨跌幅</TableHead>
                  <TableHead className="text-right">成本</TableHead>
                  <TableHead className="text-right">股数</TableHead>
                  <TableHead className="text-right">盈亏</TableHead>
                  <TableHead>备注</TableHead>
                  <TableHead className="text-right">操作</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {items.map((item) => {
                  const cost = (item.cost_price ?? 0) * (item.shares ?? 0);
                  const market = (item.currentPrice ?? item.cost_price ?? 0) * (item.shares ?? 0);
                  const pnl = market - cost;
                  const pnlPct = cost > 0 ? (pnl / cost) * 100 : 0;

                  return (
                    <TableRow key={item.symbol}>
                      <TableCell>
                        <SymbolLink symbol={item.symbol} className="font-semibold" />
                      </TableCell>
                      <TableCell>{item.name || "-"}</TableCell>
                      <TableCell className="text-right font-mono">
                        {item.currentPrice != null ? item.currentPrice.toFixed(2) : "-"}
                      </TableCell>
                      <TableCell className={`text-right font-mono ${(item.changePercent ?? 0) >= 0 ? "text-positive" : "text-negative"}`}>
                        {item.changePercent != null ? `${item.changePercent >= 0 ? "+" : ""}${item.changePercent.toFixed(2)}%` : "-"}
                      </TableCell>
                      <TableCell className="text-right font-mono">{item.cost_price?.toFixed(2) ?? "-"}</TableCell>
                      <TableCell className="text-right font-mono">{item.shares?.toLocaleString() ?? "-"}</TableCell>
                      <TableCell className={`text-right font-mono ${pnl >= 0 ? "text-positive" : "text-negative"}`}>
                        {item.shares ? (
                          <div>
                            <div>{pnl >= 0 ? "+" : ""}¥{pnl.toLocaleString(undefined, { maximumFractionDigits: 0 })}</div>
                            <div className="text-xs">{pnlPct >= 0 ? "+" : ""}{pnlPct.toFixed(2)}%</div>
                          </div>
                        ) : "-"}
                      </TableCell>
                      <TableCell className="max-w-[120px] truncate text-sm text-muted-foreground">
                        {item.note || ""}
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-1">
                          <EditDialog item={item} onUpdated={() => fetchWatchlist()} />
                          <Button variant="ghost" size="icon" className="size-8" onClick={() => handleDelete(item.symbol)}>
                            <Trash2 className="size-3.5 text-muted-foreground hover:text-destructive" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

function AddDialog({ open, onOpenChange, onAdded }: { open: boolean; onOpenChange: (v: boolean) => void; onAdded: () => void }) {
  const [symbol, setSymbol] = useState("");
  const [name, setName] = useState("");
  const [costPrice, setCostPrice] = useState("");
  const [shares, setShares] = useState("");
  const [note, setNote] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!symbol.trim()) { setError("请输入股票代码"); return; }
    setBusy(true);
    setError("");
    try {
      const payload: WatchlistAddPayload = { symbol: symbol.trim() };
      if (name.trim()) payload.name = name.trim();
      if (costPrice) payload.cost_price = Number(costPrice);
      if (shares) payload.shares = Number(shares);
      if (note.trim()) payload.note = note.trim();
      await addToWatchlist(payload);
      setSymbol(""); setName(""); setCostPrice(""); setShares(""); setNote("");
      onOpenChange(false);
      onAdded();
      toast.success("已添加到自选股");
    } catch (err) {
      const msg = err instanceof Error ? err.message : "添加失败";
      setError(msg);
      toast.error(msg);
    } finally {
      setBusy(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogTrigger asChild>
        <Button size="sm">
          <BookmarkPlus className="mr-2 size-4" />
          添加
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>添加自选股</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="grid gap-4">
          <div className="grid gap-2">
            <Label htmlFor="add-symbol">股票代码 *</Label>
            <Input id="add-symbol" value={symbol} onChange={(e) => setSymbol(e.target.value)} placeholder="000001" required />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="add-name">名称（可选）</Label>
            <Input id="add-name" value={name} onChange={(e) => setName(e.target.value)} placeholder="平安银行" />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="grid gap-2">
              <Label htmlFor="add-cost">成本价</Label>
              <Input id="add-cost" type="number" step="0.01" min="0" value={costPrice} onChange={(e) => setCostPrice(e.target.value)} placeholder="12.50" />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="add-shares">股数</Label>
              <Input id="add-shares" type="number" min="0" value={shares} onChange={(e) => setShares(e.target.value)} placeholder="1000" />
            </div>
          </div>
          <div className="grid gap-2">
            <Label htmlFor="add-note">备注</Label>
            <Input id="add-note" value={note} onChange={(e) => setNote(e.target.value)} placeholder="底仓" />
          </div>
          {error && <Alert variant="destructive"><AlertDescription>{error}</AlertDescription></Alert>}
          <Button type="submit" disabled={busy}>{busy ? "添加中..." : "确认添加"}</Button>
        </form>
      </DialogContent>
    </Dialog>
  );
}

function EditDialog({ item, onUpdated }: { item: EnrichedItem; onUpdated: () => void }) {
  const [open, setOpen] = useState(false);
  const [costPrice, setCostPrice] = useState(String(item.cost_price ?? ""));
  const [shares, setShares] = useState(String(item.shares ?? ""));
  const [note, setNote] = useState(item.note ?? "");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      const updates: Record<string, unknown> = {};
      if (costPrice) updates.cost_price = Number(costPrice);
      if (shares) updates.shares = Number(shares);
      updates.note = note;
      await updateWatchlistItem(item.symbol, updates);
      setOpen(false);
      onUpdated();
      toast.success("自选股已更新");
    } catch (err) {
      const msg = err instanceof Error ? err.message : "更新失败";
      setError(msg);
      toast.error(msg);
    } finally {
      setBusy(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="ghost" size="icon" className="size-8">
          <Pencil className="size-3.5 text-muted-foreground" />
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>编辑 {item.symbol} {item.name}</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="grid gap-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="grid gap-2">
              <Label htmlFor="edit-cost">成本价</Label>
              <Input id="edit-cost" type="number" step="0.01" min="0" value={costPrice} onChange={(e) => setCostPrice(e.target.value)} />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="edit-shares">股数</Label>
              <Input id="edit-shares" type="number" min="0" value={shares} onChange={(e) => setShares(e.target.value)} />
            </div>
          </div>
          <div className="grid gap-2">
            <Label htmlFor="edit-note">备注</Label>
            <Input id="edit-note" value={note} onChange={(e) => setNote(e.target.value)} />
          </div>
          {error && <Alert variant="destructive"><AlertDescription>{error}</AlertDescription></Alert>}
          <Button type="submit" disabled={busy}>{busy ? "保存中..." : "保存"}</Button>
        </form>
      </DialogContent>
    </Dialog>
  );
}
