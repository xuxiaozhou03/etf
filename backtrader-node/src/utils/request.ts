/**
 * 通用 request 方法，基于 fetch，支持 params
 * @param url 请求地址
 * @param params 查询参数对象
 * @returns Promise<any>
 */
export async function request<T = any>(
  url: string,
  params?: Record<string, any>
): Promise<T> {
  let finalUrl = url;
  if (params && Object.keys(params).length > 0) {
    const searchParams = new URLSearchParams(params).toString();
    finalUrl += (finalUrl.includes("?") ? "&" : "?") + searchParams;
  }
  const res = await fetch(finalUrl);
  const contentType = res.headers.get("content-type");
  if (contentType && contentType.includes("application/json")) {
    return (await res.json()) as T;
  }
  try {
    return (await res.json()) as T;
  } catch {
    return (await res.text()) as T;
  }
}
