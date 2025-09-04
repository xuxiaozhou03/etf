import * as cheerio from "cheerio";
import { request } from "@/utils/request";
import { nodeEval } from "@/utils/utils";

export interface Holding {
  code: string;
  name: string;
  ratio: string;
  shares: string;
  marketValue: string;
}

export interface EtfInfo {
  target: string;
  benchmark: string;
  scale: Array<[number, number]>;
  // holdings: Holding[];
}

// https://fundf10.eastmoney.com/jbgk_159278.html
const getEtfBasicInfo = async (code: string) => {
  const html = await request(
    `https://fundf10.eastmoney.com/jbgk_${code}.html`,
    {
      headers: {
        "Content-Type": "text/html",
      },
    }
  );
  const $ = cheerio.load(html);
  const map = {
    target: ".info.w790 tbody tr:eq(9) td:eq(1)",
    // 基准
    benchmark: ".info.w790 tbody tr:eq(9) td:eq(0)",
  };
  const info: Pick<EtfInfo, "benchmark" | "target"> = {
    target: "",
    benchmark: "",
  };
  Object.entries(map).forEach(([key, selector]) => {
    info[key as "target" | "benchmark"] = $(selector).text().trim();
  });
  return info;
};

// https://fundf10.eastmoney.com/FundArchivesDatas.aspx?type=jzcgm&code=159278&rt=0.12115300900651682
// 规模
const getEtfScale = async (code: string) => {
  const res = await request(
    "https://fundf10.eastmoney.com/FundArchivesDatas.aspx",
    {
      params: {
        type: "jzcgm",
        code,
        rt: Math.random(),
      },
      headers: {
        "Content-Type": "text/html",
      },
    }
  );
  return nodeEval<EtfInfo["scale"]>(res, "jzcgm_apidata") || [];
};

export const getEtfInfo = async (code: string): Promise<EtfInfo> => {
  const info = await getEtfBasicInfo(code);
  const scale = await getEtfScale(code);
  return {
    ...info,
    scale,
  };
};
