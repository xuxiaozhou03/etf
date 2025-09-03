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
  holdings: Holding[];
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

// https://fundf10.eastmoney.com/FundArchivesDatas.aspx?type=jjcc&code=159715&topline=1000&year=2025&month=&rt=0.015969691510728135
const getEtfHoldings = async (code: string) => {
  const res = await request(
    "https://fundf10.eastmoney.com/FundArchivesDatas.aspx",
    {
      params: {
        type: "jjcc",
        code,
        topline: 1000,
        year: 2025,
        month: "",
        rt: Math.random(),
      },
      headers: {
        "Content-Type": "text/html",
      },
    }
  );
  const data = nodeEval<{ content: string }>(res, "apidata");
  if (!data?.content) {
    return [];
  }
  const $ = cheerio.load(data.content);
  const tbody = $(".box:eq(0) tbody");
  const holdings: Holding[] = [];
  tbody.children("tr").each((_, tr) => {
    const code = $(tr).find("td:eq(1)").text().trim();
    const name = $(tr).find("td:eq(2)").text().trim();
    // 占比
    const ratio = $(tr).find("td:eq(6)").text().trim();
    // 持股数
    const shares = $(tr).find("td:eq(7)").text().trim();
    // 持仓市值
    const marketValue = $(tr).find("td:eq(8)").text().trim();

    holdings.push({ code, name, ratio, shares, marketValue });
  });
  return holdings;
};

export const getEtfInfo = async (code: string): Promise<EtfInfo> => {
  const info = await getEtfBasicInfo(code);
  const scale = await getEtfScale(code);
  const holdings = await getEtfHoldings(code);
  return {
    ...info,
    scale,
    holdings,
  };
};
