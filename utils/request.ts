/* eslint-disable @typescript-eslint/no-explicit-any */

type RequestOptions = {
  method?: string;
  headers?: Record<string, string>;
  body?: any;
  params?: Record<string, any>;
};

function buildUrl(url: string, params?: Record<string, any>) {
  if (!params) return url;
  const query = Object.entries(params)
    .map(
      ([key, value]) =>
        `${encodeURIComponent(key)}=${encodeURIComponent(value)}`
    )
    .join("&");
  return query ? `${url}?${query}` : url;
}

export async function request<T = any>(
  url: string,
  options: RequestOptions = {}
): Promise<T> {
  const { method = "GET", headers = {}, body, params } = options;

  const fetchOptions: RequestInit = {
    method,
    headers: {
      "Content-Type": "application/json",
      ...headers,
    },
  };

  if (body && method !== "GET") {
    fetchOptions.body = typeof body === "string" ? body : JSON.stringify(body);
  }

  const finalUrl = buildUrl(url, params);

  const response = await fetch(finalUrl, fetchOptions);

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(errorText || response.statusText);
  }

  const contentType = response.headers.get("content-type");
  if (contentType && contentType.includes("application/json")) {
    return response.json();
  }
  return response.text() as unknown as T;
}
