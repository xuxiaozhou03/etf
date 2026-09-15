import { Hono } from "hono";
import { serveStatic } from "@hono/node-server/serve-static";
import { prisma } from "@quant-backtest/db";

export const app = new Hono();

// 静态页面：/ -> public/index.html
app.get("/", serveStatic({ root: "./public", index: "index.html" }));

// 静态资源：/assets/* -> public/assets/*
app.use("/assets/*", serveStatic({ root: "./public" }));

// 详情页：/etfs/:code -> public/etf.html（客户端 fetch /api/etfs/:code）
app.get(
  "/etfs/:code",
  serveStatic({ root: "./public", rewriteRequestPath: () => "/etf.html" }),
);

// JSON API：ETF 列表
app.get("/api/etfs", async (c) => {
  const etfs = await prisma.etf.findMany({ orderBy: { code: "asc" } });
  return c.json(etfs);
});

// JSON API：单只 ETF 的 K 线 + 特征
app.get("/api/etfs/:code", async (c) => {
  const { code } = c.req.param();
  const [etf, klines, features] = await Promise.all([
    prisma.etf.findUnique({ where: { code } }),
    prisma.kline.findMany({ where: { code }, orderBy: { date: "asc" } }),
    prisma.feature.findMany({ where: { code }, orderBy: { date: "asc" } }),
  ]);
  if (!etf) return c.json({ error: "not found" }, 404);
  return c.json({ etf, klines, features });
});
