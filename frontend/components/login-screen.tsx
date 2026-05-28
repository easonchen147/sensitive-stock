"use client";

import { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { LogIn } from "lucide-react";

import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { login } from "@/lib/api";

export function LoginScreen() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const nextPath = searchParams.get("next") || "/";

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError("");

    try {
      await login({ username, password });
      router.push(nextPath);
      router.refresh();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "登录失败，请重试。");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="flex min-h-[calc(100vh-8rem)] items-center justify-center">
      <div className="grid w-full max-w-4xl gap-8 lg:grid-cols-[1fr_400px]">
        {/* Left: branding */}
        <div className="hidden flex-col justify-center lg:flex">
          <span className="text-xs font-bold uppercase tracking-wider text-primary">研究终端</span>
          <h1 className="mt-3 font-display text-4xl font-bold leading-tight tracking-tight text-foreground">
            敏感股票研究台
          </h1>
          <p className="mt-4 max-w-md text-sm leading-relaxed text-muted-foreground">
            统一入口服务 A 股研究、预测、验证与组合配置。所有可见模块均有接口支撑，登录后即可使用全部功能。
          </p>
        </div>

        {/* Right: login form */}
        <Card>
          <CardHeader>
            <CardTitle className="font-display text-xl">登录</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="grid gap-4">
              <div className="grid gap-2">
                <Label htmlFor="username">用户名</Label>
                <Input
                  id="username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="admin"
                  autoComplete="username"
                  required
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="password">密码</Label>
                <Input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="请输入密码"
                  autoComplete="current-password"
                  required
                />
              </div>

              {error ? (
                <Alert variant="destructive">
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              ) : null}

              <Button type="submit" disabled={busy} className="w-full">
                <LogIn className="size-4" />
                {busy ? "登录中..." : "登录"}
              </Button>

              <p className="text-center text-xs text-muted-foreground">
                默认凭据仅用于开发环境，请在 .env 中配置正式凭据。
              </p>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
