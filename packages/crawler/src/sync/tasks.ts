/**
 * 任务注册表：目前两个固定阶段任务
 *   · etf_list —— 抓 ETF 列表并刷新 Security 表（阶段①）
 *   · [code]_kline —— 由阶段①之后从 DB 读 Security 组装（阶段②）
 *
 * 阶段① 与 阶段② 严格顺序，见 scheduler.ts。
 */

import { shouldSkipAfterCutoff, taskId } from "./rule";
import { SyncTask } from "./types";

/** etf_list 任务：刷 Security 表 */
export const etfListTask: SyncTask = {
  type: "etf_list",

  async shouldRun(ctx) {
    // 规则（etf_list 与 kline 同一套）：收盘后已完成 → 跳过
    if (ctx.force) return true;
    // TODO(骨架)：从 SyncTaskRun 读取该任务最近一次成功 finishedAt
    const lastSuccess: Date | null = null;
    return !shouldSkipAfterCutoff(lastSuccess);
  },

  async run(_ctx) {
    // TODO(骨架)：调 data 的 ETFFetcher.fetchAndFilter + 本层 DataWriter.syncETFList，写 SyncTaskRun
    throw new Error("TODO(骨架): 实现 etf_list 任务执行（抓列表 → 刷 Security 表）");
  },
};

/** 生成 [code]_kline 任务 */
export function klineTask(code: string, name?: string): SyncTask {
  return {
    type: "kline",
    params: { code, name },
    taskKey: code,

    async shouldRun(ctx) {
      if (ctx.force) return true;
      // TODO(骨架)：按 taskKey=code 查该任务最近一次成功 finishedAt
      const lastSuccess: Date | null = null;
      return !shouldSkipAfterCutoff(lastSuccess);
    },

    async run(_ctx) {
      // TODO(骨架)：调本层 DataWriter.syncETF(code, name, {incremental:true})（取数来自 data），写 SyncTaskRun
      throw new Error(`TODO(骨架): 实现 kline 任务执行 ${code}（增量同步日K）`);
    },
  };
}

export { taskId };
