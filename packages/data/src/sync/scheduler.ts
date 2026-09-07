/**
 * 两阶段同步调度器（docs/09 §3.4）：
 *
 *   pnpm sync
 *    └─ 阶段① 判断 etf_list —— 执行(抓列表/刷 Security) 或 跳过
 *    └─ 阶段② 从 DB Security 读取 → 组装 [code]_kline 任务 → 逐个判断执行/跳过
 *
 * 阶段② 的组装不依赖阶段①本次是否真的执行：只要 DB 里的 Security 列表可用即可。
 * 但调用顺序固定 —— 每次 sync 都先走阶段①判断 etf_list。
 */

import { shouldSkipAfterCutoff } from "./rule";
import { etfListTask, klineTask } from "./tasks";
import { SyncContext, SyncReport, SyncTask, TaskRunOutcome } from "./types";

async function runOne(task: SyncTask, ctx: SyncContext): Promise<TaskRunOutcome> {
  const outcome: TaskRunOutcome = {
    taskId: `${task.type}${task.taskKey ? `:${task.taskKey}` : ""}`,
    status: "executed",
  };

  try {
    const needRun = await task.shouldRun(ctx);
    if (!needRun) {
      outcome.status = "skipped";
      outcome.reason = "上次成功完成于数据收盘参考点之后，无需重跑（docs/09 §5）";
      return outcome;
    }
  } catch (e) {
    outcome.status = "failed";
    outcome.error = `shouldRun 异常: ${String(e)}`;
    return outcome;
  }

  outcome.startedAt = new Date();
  try {
    await task.run(ctx);
    outcome.finishedAt = new Date();
    // TODO(骨架)：执行成功后写 SyncTaskRun（status=success / startedAt / finishedAt）
  } catch (e) {
    outcome.status = "failed";
    outcome.error = String(e);
    // TODO(骨架)：失败也写 SyncTaskRun（status=failed / error），供下次判断
  }
  return outcome;
}

/**
 * 执行一次完整同步。
 * ctx 当前为纯标记（force），真实的 DataService / DataWriter 注入见 TODO。
 */
export async function runSync(ctx: SyncContext): Promise<SyncReport> {
  const outcomes: TaskRunOutcome[] = [];

  // ---- 阶段①：etf_list（先判断 / 再执行）----
  outcomes.push(await runOne(etfListTask, ctx));

  // ---- 阶段②：从 DB 读 Security → 组装 [code]_kline → 逐个判断执行 ----
  // TODO(骨架)：真实实现改为 DataService.getETFList() 取全量 Security；
  //   此处用占位（阶段①若本次成功执行会刷新该表，但组装始终以 DB 现值为准）。
  const securities: Array<{ code: string; name: string }> = [
    // { code: "510300", name: "沪深300ETF" },
  ];

  for (const s of securities) {
    const task = klineTask(s.code, s.name);
    outcomes.push(await runOne(task, ctx));
  }

  return {
    outcomes,
    summary: {
      executed: outcomes.filter((o) => o.status === "executed").length,
      skipped: outcomes.filter((o) => o.status === "skipped").length,
      failed: outcomes.filter((o) => o.status === "failed").length,
    },
  };
}

export { shouldSkipAfterCutoff };
