import fs from "fs";
import path from "path";

const THRESHOLD = 80;
const DATA_DIR = path.resolve(__dirname, "../..");
const A_MD_PATH = path.resolve(DATA_DIR, "../../a.md");

interface Etf {
  securityName: string;
  securityCode: string;
  scale: number;
  trackingIndex: string;
  trackIndex: string;
}

interface LinkRow {
  code: string;
  similar: number;
}

interface LinkFundFile {
  data: Record<string, LinkRow[]>;
}

interface ParsedCategory {
  name: string;
  codes: string[];
}

interface SimilarFund {
  similar: number;
  name: string;
  code: string;
  scale: number;
}

interface DroppedEtf extends Etf {
  similar: number;
}

interface KeptEtf extends Etf {
  similarFunds: SimilarFund[];
  dropped: DroppedEtf[];
}

interface CategoryResult {
  name: string;
  lists: KeptEtf[];
}

const readJson = <T>(file: string): T => {
  return JSON.parse(fs.readFileSync(file, "utf-8")) as T;
};

const pairKey = (a: string, b: string) => {
  return [a, b].sort().join("|");
};

const parseCategories = (markdown: string): ParsedCategory[] => {
  const categories: ParsedCategory[] = [];
  let current: ParsedCategory | undefined;

  for (const rawLine of markdown.split(/\r?\n/)) {
    const line = rawLine.trim();
    const heading = line.match(/^## (.+?)（(\d+)个ETF）$/);
    if (heading) {
      current = { name: heading[1], codes: [] };
      categories.push(current);
      continue;
    }

    if (!current) {
      continue;
    }

    const row = line.match(/^(.+)\((\d{6}\.(?:SH|SZ))\)$/);
    if (row) {
      current.codes.push(row[2]);
    }
  }

  return categories;
};

const main = () => {
  const etfs = readJson<Etf[]>(path.join(DATA_DIR, "etfs.json"));
  const linkFund = readJson<LinkFundFile>(path.join(DATA_DIR, "linkFund.json"));
  const etfMap = new Map(etfs.map((etf) => [etf.securityCode, etf]));
  const categories = parseCategories(
    fs.readFileSync(A_MD_PATH, { encoding: "utf-8" }),
  );

  const edgeMap = new Map<string, number>();
  const similarityMap = new Map<string, Map<string, number>>();
  for (const [from, rows] of Object.entries(linkFund.data)) {
    if (!etfMap.has(from)) {
      continue;
    }

    for (const row of rows) {
      if (!etfMap.has(row.code)) {
        continue;
      }

      const key = pairKey(from, row.code);
      const similarity = Math.max(edgeMap.get(key) ?? 0, row.similar);
      edgeMap.set(key, similarity);

      const fromSimilarities = similarityMap.get(from) ?? new Map();
      fromSimilarities.set(
        row.code,
        Math.max(fromSimilarities.get(row.code) ?? 0, row.similar),
      );
      similarityMap.set(from, fromSimilarities);

      const toSimilarities = similarityMap.get(row.code) ?? new Map();
      toSimilarities.set(
        from,
        Math.max(toSimilarities.get(from) ?? 0, row.similar),
      );
      similarityMap.set(row.code, toSimilarities);
    }
  }

  const getSimilarFunds = (code: string): SimilarFund[] => {
    return [...(similarityMap.get(code) ?? new Map())]
      .map(([similarCode, similar]) => ({
        similar,
        name: etfMap.get(similarCode)!.securityName,
        code: similarCode,
        scale: etfMap.get(similarCode)!.scale,
      }))
      .sort((a, b) => b.similar - a.similar);
  };

  const classifiedCodes = new Set(
    categories.flatMap((category) =>
      category.codes.filter((code) => etfMap.has(code)),
    ),
  );
  const members = [...classifiedCodes]
    .map((code) => etfMap.get(code)!)
    .sort((a, b) => b.scale - a.scale);
  const keptEtfs: KeptEtf[] = [];

  for (const member of members) {
    let matched: KeptEtf | undefined;
    let matchedSimilarity = 0;

    for (const kept of keptEtfs) {
      const similarity = edgeMap.get(
        pairKey(member.securityCode, kept.securityCode),
      );
      if (
        similarity &&
        similarity > THRESHOLD &&
        similarity > matchedSimilarity
      ) {
        matched = kept;
        matchedSimilarity = similarity;
      }
    }

    if (matched) {
      matched.dropped.push({
        ...member,
        similar: matchedSimilarity,
      });
    } else {
      keptEtfs.push({
        ...member,
        similarFunds: getSimilarFunds(member.securityCode),
        dropped: [],
      });
    }
  }

  const result: CategoryResult[] = categories.map((category) => {
    const codes = new Set(category.codes);
    return {
      name: category.name,
      lists: keptEtfs.filter((etf) => codes.has(etf.securityCode)),
    };
  });

  fs.writeFileSync(
    path.join(DATA_DIR, "linkClusters.json"),
    JSON.stringify(result),
  );

  const missingFromEtfs = [
    ...new Set(categories.flatMap((category) => category.codes)),
  ].filter((code) => !etfMap.has(code));
  const unclassified = etfs.filter(
    (etf) => !classifiedCodes.has(etf.securityCode),
  );

  console.log(
    `ETF ${etfs.length}, classified ${classifiedCodes.size}, kept ${keptEtfs.length}`,
  );
  if (unclassified.length > 0) {
    console.warn(
      `Unclassified ${unclassified.length}: ${unclassified
        .map((etf) => etf.securityCode)
        .join(", ")}`,
    );
  }
  if (missingFromEtfs.length > 0) {
    console.warn(`Missing from etfs.json: ${missingFromEtfs.join(", ")}`);
  }
};

main();
