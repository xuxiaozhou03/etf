import { request } from "@/utils/request";
import { nodeEval } from "@/utils/utils";
import { Holding } from "./get_etf_info";
import * as cheerio from "cheerio";

// https://fundf10.eastmoney.com/FundArchivesDatas.aspx?type=jjcc&code=159715&topline=1000&year=2025&month=&rt=0.015969691510728135
export const getEtfHoldings = async (code: string) => {
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
