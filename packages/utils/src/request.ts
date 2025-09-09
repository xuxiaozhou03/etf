export interface RequestOptions extends RequestInit {
  params?: Record<string, any>;
}

export async function request<T = any>(
  url: string,
  options: RequestOptions = {}
): Promise<T> {
  const { method = "GET", params, body, headers } = options;
  let finalUrl = url;
  if (params && Object.keys(params).length > 0) {
    const searchParams = new URLSearchParams(
      params as Record<string, string>
    ).toString();
    finalUrl += (finalUrl.includes("?") ? "&" : "?") + searchParams;
  }
  const fetchOptions: RequestInit = {
    method,
    headers,
  };
  if (body && method !== "GET") {
    fetchOptions.body = typeof body === "string" ? body : JSON.stringify(body);
    fetchOptions.headers = {
      "Content-Type": "application/json",
      ...headers,
    };
  }
  const res = await fetch(finalUrl, fetchOptions);
  if (!res.ok) throw new Error(res.statusText);
  const contentType = res.headers.get("content-type") || "";

  if (contentType.includes("application/json")) {
    return res.json();
  }

  // 默认尝试 text
  return res.text() as T;
}
