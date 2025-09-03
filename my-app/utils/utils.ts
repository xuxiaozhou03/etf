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
