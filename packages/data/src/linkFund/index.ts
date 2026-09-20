import { type Etf } from "../etfs";
import { saveFile } from "../utils/saveFile";
import { CheeseApiError } from "../utils/fetchCheeseApi";
import { fetchLinkFund } from "./linkFund";

const RETRY_TIMES = 3;

const SAVE_EVERY = 5;
const REQUEST_INTERVAL = 300;

type LinkRow = { code: string; similar: number };

const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

export interface LinkResult {
  data: Record<string, LinkRow[]>;
  failed?: string[];
  empty?: string[];
}

type FetchResult =
  | { status: "success"; rows: LinkRow[] }
  | { status: "empty" }
  | { status: "failed"; error: unknown; attempts: number };

const isRetryableError = (error: unknown) => {
  return error instanceof CheeseApiError ? error.retryable : true;
};

export const fetchWithRetry = async (code: string): Promise<FetchResult> => {
  let lastError: unknown;

  for (let attempt = 1; attempt <= RETRY_TIMES; attempt++) {
    try {
      const rows = await fetchLinkFund(code);
      return rows.length === 0
        ? { status: "empty" }
        : { status: "success", rows };
    } catch (err) {
      lastError = err;
      console.warn(`[${code}] attempt ${attempt} failed:`, err);

      if (!isRetryableError(err)) {
        return { status: "failed", error: err, attempts: attempt };
      }
    }
    if (attempt < RETRY_TIMES) {
      await sleep(1000 * attempt);
    }
  }

  return { status: "failed", error: lastError, attempts: RETRY_TIMES };
};

export const fetchAllLinkFunds = async (etfs: Etf[]) => {
  const etfCodes = etfs.map((etf) => etf.securityCode);
  const result: Record<string, LinkRow[]> = {};
  const failed: string[] = [];
  const empty: string[] = [];
  const savedPairs = new Set<string>();

  for (let i = 0; i < etfs.length; i++) {
    const etf = etfs[i];
    const fetchResult = await fetchWithRetry(etf.securityCode);
    const rows = fetchResult.status === "success" ? fetchResult.rows : [];

    if (fetchResult.status === "failed") {
      failed.push(etf.securityCode);
    } else if (fetchResult.status === "empty") {
      empty.push(etf.securityCode);
    }

    const links = rows
      .filter((row) => etfCodes.includes(row.code))
      .filter((row) => {
        const pairKey = [etf.securityCode, row.code].sort().join("|");
        if (savedPairs.has(pairKey)) {
          return false;
        }
        savedPairs.add(pairKey);
        return true;
      });
    result[etf.securityCode] = links;
    console.log(
      `[${i + 1}/${etfs.length}] ${etf.securityCode}: ${links.length} links`,
    );

    if ((i + 1) % SAVE_EVERY === 0) {
      saveFile("linkFund.json", result);
    }
    await sleep(REQUEST_INTERVAL);
  }

  const data: LinkResult = {
    data: result,
    failed: failed.length > 0 ? failed : undefined,
    empty: empty.length > 0 ? empty : undefined,
  };
  saveFile("linkFund.json", data);
  if (failed.length > 0) {
    console.warn(`Failed for ${failed.length} etfs: ${failed.join(", ")}`);
  }
  if (empty.length > 0) {
    console.warn(`No data for ${empty.length} etfs: ${empty.join(", ")}`);
  }
};
