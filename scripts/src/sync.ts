/**
 * pnpm sync 统一入口（docs/09）
 *   pnpm sync            两阶段：先 etf_list，再从 DB 组装 [code]_kline
 *   pnpm sync --force    忽略跳过判断，全部强制执行
 * TODO(骨架)：真正接入时替换 runSync 的实现依赖（SyncTaskRun 持久化等）。
 */

import { runSync } from "@quant-backtest/data";

async function main() {
  const force = process.argv.includes("--force");
  const ctx = { force };

  const report = await runSync(ctx);

  // 汇总输出
  for (const o of report.outcomes) {
    const flag = o.status === "executed" ? "✔" : o.status === "skipped" ? "⏭" : "✖";
    console.log(`${flag} ${o.taskId}${o.reason ? `  (${o.reason})` : ""}${o.error ? `  -> ${o.error}` : ""}`);
  }
  const { executed, skipped, failed } = report.summary;
  console.log(`\n完成：执行 ${executed}，跳过 ${skipped}，失败 ${failed}`);

  process.exitCode = failed > 0 ? 1 : 0;
}

main().catch((e) => {
  console.error(e);
  process.exitCode = 1;
});
