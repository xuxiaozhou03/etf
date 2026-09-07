#!/usr/bin/env tsx
/**
 * @quant-backtest/cli —— quant 命令入口（骨架）
 *
 * 用法：
 *   quant sync [--force]     统一数据同步（两阶段：etf_list → [code]_kline）
 *
 * TODO(骨架)：run / list / compare 回测子命令。
 */

import { runSyncCommand } from "./commands/sync.js";

interface Command {
  desc: string;
  run(args: string[]): Promise<number>;
}

/** 子命令注册表：新增子命令时在此登记 */
const COMMANDS: Record<string, Command> = {
  sync: { desc: "统一数据同步（etf_list → [code]_kline 两阶段调度）", run: runSyncCommand },
};

const VERSION = "0.1.0";

function printUsage() {
  console.log(`quant v${VERSION} —— 量化回测命令行\n`);
  console.log("用法: quant <子命令> [参数]\n");
  console.log("子命令:");
  for (const [name, cmd] of Object.entries(COMMANDS)) {
    console.log(`  ${name.padEnd(12)} ${cmd.desc}`);
  }
  console.log("\n当前可用: sync；run/list/compare 待实现");
}

async function main() {
  const [, , sub, ...rest] = process.argv;
  const cmd = sub ? COMMANDS[sub] : undefined;
  if (!cmd) {
    printUsage();
    return; // 未给子命令或子命令未知 → 展示帮助，exit 0
  }
  process.exitCode = await cmd.run(rest);
}

main().catch((e) => {
  console.error(e);
  process.exitCode = 1;
});
