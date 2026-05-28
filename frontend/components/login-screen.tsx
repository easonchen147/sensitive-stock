"use client";

import { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { toast } from "sonner";
import { LogIn, UserPlus } from "lucide-react";

import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { login, registerUser } from "@/lib/api";

export function LoginScreen() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const nextPath = searchParams.get("next") || "/";

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function handleLogin(event: React.FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      await login({ username, password });
      toast.success("登录成功");
      router.push(nextPath);
      router.refresh();
    } catch (caught) {
      const msg = caught instanceof Error ? caught.message : "登录失败，请重试。";
      setError(msg);
      toast.error(msg);
    } finally {
      setBusy(false);
    }
  }

  async function handleRegister(event: React.FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      await registerUser({ username, password, display_name: displayName || undefined });
      toast.success("注册成功");
      router.push(nextPath);
      router.refresh();
    } catch (caught) {
      const msg = caught instanceof Error ? caught.message : "注册失败，请重试。";
      setError(msg);
      toast.error(msg);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="flex min-h-[calc(100vh-8rem)] items-center justify-center">
      <div className="grid w-full max-w-4xl gap-8 lg:grid-cols-[1fr_400px]">
        <div className="hidden flex-col justify-center lg:flex">
          <span className="text-xs font-bold uppercase tracking-wider text-primary">研究终端</span>
          <h1 className="mt-3 font-display text-4xl font-bold leading-tight tracking-tight text-foreground">
            敏感股票研究台
          </h1>
          <p className="mt-4 max-w-md text-sm leading-relaxed text-muted-foreground">
            统一入口服务 A 股研究、预测、验证与组合配置。登录后即可使用全部功能。
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="font-display text-xl">欢迎使用</CardTitle>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="login">
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="login">登录</TabsTrigger>
                <TabsTrigger value="register">注册</TabsTrigger>
              </TabsList>

              <TabsContent value="login">
                <form onSubmit={handleLogin} className="grid gap-4 pt-4">
                  <div className="grid gap-2">
                    <Label htmlFor="login-username">用户名</Label>
                    <Input id="login-username" value={username} onChange={(e) => setUsername(e.target.value)} placeholder="admin" autoComplete="username" required />
                  </div>
                  <div className="grid gap-2">
                    <Label htmlFor="login-password">密码</Label>
                    <Input id="login-password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="请输入密码" autoComplete="current-password" required />
                  </div>
                  {error && <Alert variant="destructive"><AlertDescription>{error}</AlertDescription></Alert>}
                  <Button type="submit" disabled={busy} className="w-full">
                    <LogIn className="mr-2 size-4" />
                    {busy ? "登录中..." : "登录"}
                  </Button>
                </form>
              </TabsContent>

              <TabsContent value="register">
                <form onSubmit={handleRegister} className="grid gap-4 pt-4">
                  <div className="grid gap-2">
                    <Label htmlFor="reg-username">用户名 *</Label>
                    <Input id="reg-username" value={username} onChange={(e) => setUsername(e.target.value)} placeholder="3-32 个字符" autoComplete="username" required minLength={3} maxLength={32} />
                  </div>
                  <div className="grid gap-2">
                    <Label htmlFor="reg-password">密码 *</Label>
                    <Input id="reg-password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="至少 6 个字符" autoComplete="new-password" required minLength={6} />
                  </div>
                  <div className="grid gap-2">
                    <Label htmlFor="reg-display">昵称（可选）</Label>
                    <Input id="reg-display" value={displayName} onChange={(e) => setDisplayName(e.target.value)} placeholder="显示名称" />
                  </div>
                  {error && <Alert variant="destructive"><AlertDescription>{error}</AlertDescription></Alert>}
                  <Button type="submit" disabled={busy} className="w-full">
                    <UserPlus className="mr-2 size-4" />
                    {busy ? "注册中..." : "注册"}
                  </Button>
                </form>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
