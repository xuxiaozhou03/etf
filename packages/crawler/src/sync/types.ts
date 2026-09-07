/**
 * 统一同步任务调度 —— 类型定义（骨架）
 * 属于 @quant-backtest/crawler：任务从 @quant-backtest/data 取数、经本层 DataWriter 落库。
 */

export interface SyncContext {
  /** 是否 --force 强制（忽略跳过判断） */
  force: boolean;
  // TODO(骨架)：注入取数（data 的 DataService / ETFFetcher）+ 本层 DataWriter + SyncTaskRun 访问入口
}

/** 同步任务：etf_list / kline 等 */
export interface SyncTask {
  /** 任务类型标识 */
  type: string;
  /** 类型内唯一键（如 [code]_kline 的 code）；同 type+taskKey 共享一条历史记录 */
  taskKey?: string;
  /** 任务参数（同类型不同参数视为不同任务） */
  params?: Record<string, unknown>;
  /** 是否需要执行（规则见各任务） */
  shouldRun(ctx: SyncContext): Promise<boolean>;
  /** 执行任务主体 */
  run(ctx: SyncContext): Promise<void>;
}

/** 单次调度结果 */
export interface TaskRunOutcome {
  taskId: string;
  status: "executed" | "skipped" | "failed";
  reason?: string;
  error?: string;
  startedAt?: Date;
  finishedAt?: Date;
}

/** 一次 pnpm sync 的汇总 */
export interface SyncReport {
  outcomes: TaskRunOutcome[];
  summary: { executed: number; skipped: number; failed: number };
}
