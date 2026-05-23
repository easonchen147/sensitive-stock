"use client";

import { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";

import { login } from "@/lib/api";
import { sanitizeNextPath } from "@/lib/auth";

export function LoginScreen() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const nextPath = sanitizeNextPath(searchParams.get("next"));

  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setError("");

    try {
      await login({ username, password });
      router.replace(nextPath);
      router.refresh();
    } catch (requestError) {
      const message =
        requestError instanceof Error ? requestError.message : "登录失败，请稍后重试。";
      setError(message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <section className="auth-screen">
      <article className="auth-card">
        <div className="eyebrow">内部访问</div>
        <h1 className="hero-title">登录敏感股票研究台</h1>
        <p className="hero-copy">
          当前仅提供内部管理员账号访问研究终端。登录后可以使用行情情报、预测复盘、回测验证和研究工具。
        </p>

        <form className="auth-form" onSubmit={handleSubmit}>
          <div className="field-grid">
            <label htmlFor="username">用户名</label>
            <input
              id="username"
              autoComplete="username"
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              placeholder="admin"
            />
          </div>

          <div className="field-grid">
            <label htmlFor="password">密码</label>
            <input
              id="password"
              autoComplete="current-password"
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="请输入管理员密码"
            />
          </div>

          {error ? <div className="banner banner-warning">{error}</div> : null}

          <button className="primary-button auth-submit" disabled={submitting} type="submit">
            {submitting ? "登录中" : "进入系统"}
          </button>
        </form>

        <div className="auth-note">
          暂不提供注册、找回密码、多角色和权限后台；本轮只保留登录与统一访问凭证边界。
        </div>
      </article>
    </section>
  );
}
