import * as fs from "fs";
import { asyncMap } from "@/utils/utils";
import { getEtfList } from "../data/get_etf_list";
import { getEtfInfo } from "../data/get_etf_info";
import etfInfo from "../json/etfs_info.json";
import { getEtfHoldings } from "../data/get_target_holdings";

// 生成 ETF 列表的基本信息
export const generateEtfsInfo = async () => {
  const etfs = await getEtfList();
  const result = await asyncMap(
    etfs,
    async (etf) => {
      console.log(`Processing ETF: ${etf.code}`);
      // 处理每个 etf
      const info = await getEtfInfo(etf.code);
      const data = {
        ...info,
        ...etf,
      };
      console.log("result:", data);
      return data;
    },
    100
  );
  if (process.env.NODE_ENV === "development") {
    fs.writeFileSync("./etfs_info.json", JSON.stringify(result, null, 2));
  }
  return result;
};

// 生成 跟踪标的 的持仓信息
export const generateHoldingsInfo = async () => {
  const targetAndCodeMap: Record<string, string> = {};
  etfInfo.forEach((etf) => {
    if (etf.target === "该基金无跟踪标的") {
      return;
    }
    targetAndCodeMap[etf.target] = etf.code;
  });
  const result = await asyncMap(
    Object.entries(targetAndCodeMap),
    async ([target, code]) => {
      console.log(`Generating holdings info for target: ${target}`);
      const holdings = await getEtfHoldings(code);
      // 这里可以添加生成持仓信息的逻辑
      return { target, holdings };
    }
  );
  const data = result.reduce((acc, item) => {
    acc[item.target] = item.holdings;
    return acc;
  }, {} as Record<string, (typeof result)[number]["holdings"]>);

  if (process.env.NODE_ENV === "development") {
    fs.writeFileSync("./holdings_info.json", JSON.stringify(data, null, 2));
  }
  return data;
};
