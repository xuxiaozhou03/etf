/**
 * 任务跳过规则（docs/09 §5）：「收盘后已完成 → 跳过」
 *
 * 取最近一次成功完成的 finishedAt 与参考点 T 比较：
 *  - 周一~周五：T = 当日 15:00；finishedAt 晚于 T → 跳过
 *  - 周六/周日：T = 最近一个周五 15:00；finishedAt 晚于 T → 跳过
 *
 * 等价判断：需要执行 ⟺ finishedAt ≤ T
 */

/** 计算当前时刻对应的"数据收盘参考点 T" */
export function tradingCutoff(now: Date = new Date()): Date {
  const d = new Date(now);
  const day = d.getDay(); // 0=周日 … 6=周六
  if (day >= 1 && day <= 5) {
    // 周一~周五：当日 15:00
    d.setHours(15, 0, 0, 0);
  } else {
    // 周六回退 1 天、周日回退 2 天 → 周五；再设 15:00
    d.setDate(d.getDate() - (day === 0 ? 2 : 1));
    d.setHours(15, 0, 0, 0);
  }
  return d;
}

/** 是否需要跳过：finishedAt 晚于参考点 T → true（跳过） */
export function shouldSkipAfterCutoff(
  finishedAt: Date | null | undefined,
  now: Date = new Date(),
): boolean {
  if (finishedAt == null) return false; // 从未成功完成 → 必须跑
  return finishedAt.getTime() > tradingCutoff(now).getTime();
}

/**
 * 计算任务标识（写入 SyncTaskRun 用）：type + taskKey + params
 * 同参数任务只保留一条历史记录。
 */
export function taskId(type: string, key?: string | null, params?: Record<string, unknown>): string {
  return [type, key ?? "", JSON.stringify(params ?? {})].join("|");
}
