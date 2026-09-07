/**
 * quant sync —— 数据同步子命令
 *
 * 两阶段：先判断 etf_list（抓列表/刷 Security），再从 DB 组装 [code]_kline 逐个判断。
 * 跳过规则「收盘后已完成 → 跳过」见 @quant-backtest/crawler 的 sync/rule.ts。
 *
 * 用法：quant sync [--force]     --force 忽略跳过判断，全部强制执行
 */

import { runSync } from "@quant-backtest/crawler";

export async function runSyncCommand(args: string[]): Promise<number> {
  const force = args.includes("--force");
  const ctx = { force };

  const report = await runSync(ctx);

  // 汇总输出
  for (const o of report.outcomes) {
    const flag =
      o.status === "executed" ? "✔" : o.status === "skipped" ? "⏭" : "✖";
    console.log(
      `${flag} ${o.taskId}${o.reason ? `  (${o.reason})` : ""}${o.error ? `  -> ${o.error}` : ""}`,
    );
  }
  const { executed, skipped, failed } = report.summary;
  console.log(`\n完成：执行 ${executed}，跳过 ${skipped}，失败 ${failed}`);

  return failed > 0 ? 1 : 0;
}
