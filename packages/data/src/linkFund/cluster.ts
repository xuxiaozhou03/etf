import fs from "fs";
import path from "path";

const THRESHOLD = 80;

interface Etf {
  securityName: string;
  securityCode: string;
  scale: number;
  trackingIndex: string;
  trackIndex: string;
}

type Link = Etf & { similar: number };
type LinkEntry = Etf & { links: Link[] };

const read = <T>(name: string): T =>
  JSON.parse(fs.readFileSync(path.resolve(name), "utf-8")) as T;

class UnionFind {
  private parent = new Map<string, string>();

  find(x: string): string {
    const p = this.parent.get(x);
    if (p === undefined) {
      this.parent.set(x, x);
      return x;
    }
    if (p === x) return x;
    const root = this.find(p);
    this.parent.set(x, root);
    return root;
  }

  union(a: string, b: string) {
    const ra = this.find(a);
    const rb = this.find(b);
    if (ra !== rb) this.parent.set(ra, rb);
  }
}

const main = () => {
  const etfs = read<Etf[]>("etfs.json");
  const entries = read<LinkEntry[]>("linkFund.json");
  const info = new Map(etfs.map((etf) => [etf.securityCode, etf]));
  const linksOf = new Map(
    entries.map((entry) => [entry.securityCode, entry.links]),
  );

  const uf = new UnionFind();
  for (const etf of etfs) uf.find(etf.securityCode);

  const seen = new Set<string>();
  let edgeCount = 0;
  for (const entry of entries) {
    for (const row of entry.links) {
      if (row.similar <= THRESHOLD) continue;
      // 只认 etfs.json 里存在的代码
      if (!info.has(entry.securityCode) || !info.has(row.securityCode)) continue;
      const key = [entry.securityCode, row.securityCode].sort().join("|");
      if (seen.has(key)) continue;
      seen.add(key);
      edgeCount++;
      uf.union(entry.securityCode, row.securityCode);
    }
  }

  const clusters = new Map<string, Etf[]>();
  for (const etf of etfs) {
    const root = uf.find(etf.securityCode);
    const list = clusters.get(root) ?? [];
    list.push(etf);
    clusters.set(root, list);
  }

  const list = [...clusters.values()]
    .map((members) => {
      const [rep, ...rest] = [...members].sort((a, b) => b.scale - a.scale);
      return {
        ...rep,
        dropped: rest.map((etf) => {
          const link = linksOf
            .get(rep.securityCode)
            ?.find((r) => r.securityCode === etf.securityCode);
          return { ...etf, similar: link?.similar ?? 0 };
        }),
      };
    })
    .sort((a, b) => b.scale - a.scale);

  const kept = list.length;
  const droppedCount = etfs.length - kept;

  for (const etf of list) {
    if (etf.dropped.length === 0) continue;
    console.log(
      `${etf.securityCode} ${etf.securityName} (${(etf.scale / 1e8).toFixed(0)}亿) <- ${etf.dropped
        .map(
          (d) =>
            `${d.securityCode} ${d.securityName}(${(d.scale / 1e8).toFixed(0)}亿,${d.similar.toFixed(1)})`,
        )
        .join(", ")}`,
    );
  }

  console.log(
    `\n相似度 >${THRESHOLD} 的边: ${edgeCount},有合并的簇: ${list.filter((e) => e.dropped.length > 0).length},` +
      `ETF ${etfs.length} -> ${kept}(丢弃 ${droppedCount})`,
  );

  fs.writeFileSync(
    path.resolve("linkClusters.json"),
    JSON.stringify({
      threshold: THRESHOLD,
      total: etfs.length,
      kept,
      list,
    }),
  );
};

main();
