export async function api<T>(
  path: string,
  method = "GET",
  body?: unknown,
): Promise<T> {
  const res = await fetch("/api" + path, {
    method,
    headers:
      body === undefined ? undefined : { "Content-Type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  if (!res.ok) {
    const d = await res.json().catch(() => null);
    const e = d?.error;
    throw new Error(
      (e?.message ?? `请求失败 ${res.status}`) +
        (e?.details
          ? "：" +
            e.details
              .map(
                (x: { field: string; message: string }) =>
                  `${x.field} ${x.message}`,
              )
              .join("；")
          : ""),
    );
  }
  return res.json() as Promise<T>;
}
export const money = (n: number | null | undefined) =>
  n == null
    ? "—"
    : "¥" + n.toLocaleString("zh-CN", { maximumFractionDigits: 2 });
export const num = (n: number | undefined, d = 1) =>
  n == null ? "—" : n.toLocaleString("zh-CN", { maximumFractionDigits: d });
export const dt = (s: string | undefined) =>
  s
    ? new Intl.DateTimeFormat("zh-CN", {
        timeZone: "Asia/Shanghai",
        month: "2-digit",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
        hour12: false,
      }).format(new Date(s))
    : "—";
export const cargoNames = {
  general: "普通货物",
  cold: "冷链生鲜",
  fragile: "易碎精密",
};
