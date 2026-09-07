/**
 * Result<T, E> 统一错误处理（骨架）
 * 完整语义见 docs/01 §2.3 错误处理。
 */

export type Result<T, E> = { ok: true; value: T } | { ok: false; error: E };

export function ok<T, E = never>(value: T): Result<T, E> {
  return { ok: true, value };
}

export function err<T, E>(error: E): Result<T, E> {
  return { ok: false, error };
}
