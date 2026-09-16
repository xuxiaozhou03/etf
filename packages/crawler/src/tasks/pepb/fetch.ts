import { fetchCheeseApi } from "../../utils/fetchCheeseApi";

export const fetchPepb = async (
  code = "588710.SH",
  index = "950125.CSI",
  type: "pe" | "pb" | "psTtm" | "indexGZPer" = "pe",
) => {
  const res = await fetchCheeseApi({
    url: `https://stock.cheesefortune.com/api/v3/details/pepb?code=${code}&type=${type}&years=10Y`,
    Referer: `https://stock.cheesefortune.com/security/etf/${index}`,
    timestamp: Date.now(),
  });
  const { min, max, mid, datas } = res as {
    min: number;
    max: number;
    mid: number;
    datas: Array<{ p: number; d: number; x: string; y: number }>;
  };

  const data = {
    code,
    type,
    min,
    max,
    mid,
    datas: datas.map((item) => {
      return {
        code,
        type,
        percentile: item.p,
        date: item.x,
        indicatorValue: item.d,
        plotValue: item.y,
      };
    }),
  };
  // console.log(data);
};

fetchPepb();
fetchPepb("588710.SH", "950125.CSI", "pb");
fetchPepb("588710.SH", "950125.CSI", "psTtm");
fetchPepb("588710.SH", "950125.CSI", "indexGZPer");
