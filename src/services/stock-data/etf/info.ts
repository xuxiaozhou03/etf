import * as cheerio from "cheerio";

export const fetchEtfInfo = async (code = "563830") => {
  const url = `https://fundf10.eastmoney.com/jbgk_${code}.html`;
  const response = await fetch(url);
  if (!response.ok) {
    return {
      benchmark: "",
      tracking: "",
      assetSize: 0,
    };
  }
  const html = await response.text();
  const $ = cheerio.load(html);
  return {
    // 业绩比较基准
    benchmark: $(".info.w790 tr:eq(9) td:eq(0)").text(),
    // 跟踪标的
    tracking: $(".info.w790 tr:eq(9) td:eq(1)").text(),
    // 资产规模
    assetSize: parseFloat($(".info.w790 tr:eq(3) td:eq(0)").text()),
  };
};

export type EtfInfo = Awaited<ReturnType<typeof fetchEtfInfo>>;
