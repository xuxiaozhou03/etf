/**
 * 安全地解析类似 'var jzcgm_apidata=[[...]]' 的字符串，返回变量名和数据
 * @param {string} code 形如 'var xxx=[...]' 的字符串
 * @returns {{ name: string, value: any } | null}
 */
export function safeEval<T extends Record<string, any>>(
  code: string
): T | null {
  try {
    // 用 Proxy 捕获变量赋值
    let varName = "";
    let varValue;
    const handler = {
      set(target: any, prop: string, value: any) {
        varName = prop;
        varValue = value;
        target[prop] = value;
        return true;
      },
    };
    const ctx = new Proxy({}, handler);
    // 将 var 替换为 ctx 的属性赋值
    // 只支持单个变量定义：var xxx = ...
    const code2 = code.replace(/^var\s+([a-zA-Z_$][\w$]*)\s*=\s*/, "ctx.$1 = ");
    new Function("ctx", code2)(ctx);
    if (varName) {
      return { [varName]: varValue } as T;
    }
    return null;
  } catch (e) {
    return null;
  }
}
