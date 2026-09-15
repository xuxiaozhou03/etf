const KLINE_API = "https://hongsehuojian.com/fundex-quote/line/kline";

/** 接口单次最多返回 1000 条，超出需用 begin 翻页 */
const PAGE_SIZE = 1000;

/** 相邻两次翻页请求的最小间隔（ms），避免刷太快 */
const PAGE_INTERVAL = 120;

/** items 每行的字段顺序（week 仅展示用，不落库） */
const COLS = [
  "week",
  "tradeDate",
  "open",
  "high",
  "low",
  "close",
  "volume",
  "amount",
  "change",
  "changePercent",
] as const;

interface KlineRow {
  code: string;
  date: number; // YYYYMMDD
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  amount: number;
  change: number;
  changePercent: number;
}

/**
 * 拉取某 ETF 的完整日 K。
 *  - 库中无该代码数据：从今天开始 count=-1000 往回翻页，直到取到最早一根；
 *  - 库中已有数据：从 max(date) 之后向后 count=1000 补新的 bar（日常 1 次请求即可）。
 */
export async function collectKlines(code: string): Promise<KlineRow[]> {
  const byDate = new Map<number, KlineRow>();
  let cursor = todayYmd();
  while (true) {
    const rows = await fetchPage(code, cursor, -PAGE_SIZE);
    if (rows.length === 0) break;
    for (const row of rows) byDate.set(row.date, row);
    if (rows.length < PAGE_SIZE) break; // 不足一页 → 已到最早可获取的窗口
    cursor = addDays(Math.min(...rows.map((r) => r.date)), -1);
    await sleep(PAGE_INTERVAL);
  }
  return [...byDate.values()].sort((a, b) => a.date - b.date);
}

/**
 * 请求一页 K 线。count>0 表示从 begin（含）向后取；count<0 表示取 begin（含）之前的最近 |count| 根。
 */
async function fetchPage(
  code: string,
  beginYmd: number,
  count: number,
): Promise<KlineRow[]> {
  const params = new URLSearchParams({
    securityCode: code,
    count: String(count),
    begin: String(beginYmd),
    period: "day",
    adjust: "1",
    ts: String(Date.now()),
  });

  const res = await fetch(`${KLINE_API}?${params}`, {
    headers: {
      accept: "application/json, text/plain, */*",
      "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
      pro: "RedRocket-PC",
      pla: "rr_Mac",
      referer: `https://hongsehuojian.com/index/h5/fundexh5bai/index.html?targetPage=indexDetail&securityCode=${code}&pro=RedRocket-PC`,
    },
    method: "GET",
  });
  if (!res.ok) throw new Error(`[kline] HTTP ${res.status} for ${code}`);

  const json = (await res.json()) as { data?: { items?: string } };
  return parseItems(code, json.data?.items);
}

/** items 是 ; 分隔的多行字符串，每行是 COLS 顺序的逗号分隔 CSV */
function parseItems(code: string, items: unknown): KlineRow[] {
  if (typeof items !== "string" || !items) return [];

  const rows: KlineRow[] = [];
  for (const line of items.split(";")) {
    if (!line) continue;
    const v = line.split(",");
    const cell: Record<string, string> = {};
    COLS.forEach((col, i) => (cell[col] = v[i] ?? ""));

    const date = Number(cell.tradeDate.replace(/-/g, ""));
    const open = Number(cell.open);
    if (!Number.isFinite(date) || !Number.isFinite(open)) continue; // 脏行跳过

    rows.push({
      code,
      date,
      open,
      high: Number(cell.high),
      low: Number(cell.low),
      close: Number(cell.close),
      volume: Number(cell.volume),
      amount: Number(cell.amount),
      change: Number(cell.change),
      changePercent: Number(cell.changePercent),
    });
  }
  return rows;
}

function todayYmd(): number {
  return fmtYmd(new Date());
}

function fmtYmd(d: Date): number {
  const mm = String(d.getMonth() + 1).padStart(2, "0");
  const dd = String(d.getDate()).padStart(2, "0");
  return Number(`${d.getFullYear()}${mm}${dd}`);
}

function addDays(ymd: number, delta: number): number {
  const s = String(ymd);
  const d = new Date(
    Number(s.slice(0, 4)),
    Number(s.slice(4, 6)) - 1,
    Number(s.slice(6, 8)),
  );
  d.setDate(d.getDate() + delta);
  return fmtYmd(d);
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
