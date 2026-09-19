import { fetchEtfs, type Etf } from "./etfs";
import { fetchLinkFund } from "./linkFund/linkFund";
import fs from "fs";
import path from "path";

const RETRY_TIMES = 3;
const SAVE_EVERY = 5;
const REQUEST_INTERVAL = 300;

type LinkRow = { code: string; similar: number };
type Link = Etf & { similar: number };
type LinkEntry = Etf & { links: Link[] };

const save = (name: string, data: unknown) => {
  fs.writeFileSync(path.resolve(name), JSON.stringify(data));
};

const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

const fetchWithRetry = async (code: string): Promise<LinkRow[]> => {
  for (let attempt = 1; attempt <= RETRY_TIMES; attempt++) {
    try {
      const rows = await fetchLinkFund(code);
      if (rows.length > 0) {
        return rows;
      }
      console.warn(`[${code}] attempt ${attempt}: empty result`);
    } catch (err) {
      console.warn(`[${code}] attempt ${attempt} failed:`, err);
    }
    if (attempt < RETRY_TIMES) {
      await sleep(1000 * attempt);
    }
  }
  return [];
};

const main = async () => {
  const etfs = await fetchEtfs();
  save("etfs.json", etfs);

  const info = new Map(etfs.map((etf) => [etf.securityCode, etf]));
  const result: LinkEntry[] = [];
  const failed: string[] = [];

  for (let i = 0; i < etfs.length; i++) {
    const etf = etfs[i];
    const rows = await fetchWithRetry(etf.securityCode);

    if (rows.length === 0) {
      failed.push(etf.securityCode);
    }
    const links = rows
      .filter((row) => info.has(row.code))
      .map((row) => ({ ...info.get(row.code)!, similar: row.similar }));
    result.push({ ...etf, links });
    console.log(
      `[${i + 1}/${etfs.length}] ${etf.securityCode}: ${links.length} links`,
    );

    if ((i + 1) % SAVE_EVERY === 0) {
      save("linkFund.json", result);
    }
    await sleep(REQUEST_INTERVAL);
  }

  save("linkFund.json", result);
  if (failed.length > 0) {
    console.warn(`Failed for ${failed.length} etfs: ${failed.join(", ")}`);
  }
};

main();
