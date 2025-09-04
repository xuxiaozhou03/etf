import { runInNewContext } from "vm";

/**
 * 从字符串中执行变量声明并获取变量值
 * @param code 变量声明字符串，如 'var foo = 123;'
 * @param varName 变量名，如 'foo'
 */
export function nodeEval<T = unknown>(
  code: string,
  varName: string
): T | undefined {
  const context: Record<string, unknown> = {};
  try {
    runInNewContext(code, context);
    return context[varName] as T;
  } catch {
    return undefined;
  }
}

/**
 * 按顺序异步执行数组任务，收集每个任务的结果，支持每个任务间歇 delay 毫秒
 * @param arr 数组
 * @param task 异步任务，返回结果
 * @param delay 间歇时间（毫秒），默认 0
 * @returns 所有任务的结果数组
 */
export async function asyncMap<T, R>(
  arr: T[],
  task: (item: T, index: number) => Promise<R>,
  delay = 0
): Promise<R[]> {
  const results: R[] = [];
  async function run(i: number): Promise<void> {
    if (i >= arr.length) return;
    results.push(await task(arr[i], i));
    if (delay > 0 && i < arr.length - 1) {
      await new Promise((resolve) => setTimeout(resolve, delay));
    }
    await run(i + 1);
  }
  await run(0);
  return results;
}
