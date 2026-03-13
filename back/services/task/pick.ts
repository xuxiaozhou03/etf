import * as fs from "fs";
import * as path from "path";
import { EtfWithInfo } from "./etfs";

export const pickEtfs = () => {
  const filePath = path.join(__dirname, "..", "..", "..", "etf-with-info.json");
  console.log();
  const data = fs.readFileSync(filePath, "utf-8");
  const oldEtfs = JSON.parse(data) as EtfWithInfo[];

  const grouped = oldEtfs.reduce(
    (acc: Record<string, EtfWithInfo[]>, etf: EtfWithInfo) => {
      if (!acc[etf.tracking]) {
        acc[etf.tracking] = [];
      }
      acc[etf.tracking].push(etf);
      return acc;
    },
    {},
  );

  const result = Object.entries(grouped)
    .map(([tracking, etfs]) => {
      const sortedEtfs = etfs.sort((a, b) => b.assetSize - a.assetSize);
      return sortedEtfs[0];
    })
    .filter((etf) => etf.assetSize > 1); // 只保留资产规模大于1亿的ETF

  fs.writeFileSync("etfs.json", JSON.stringify(result, null, 2));
};
