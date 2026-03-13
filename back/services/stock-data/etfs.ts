// https://push2.eastmoney.com/api/qt/clist/get?np=1&fltt=1&invt=2&fs=b%3AMK0021%2Cb%3AMK0022%2Cb%3AMK0023%2Cb%3AMK0024%2Cb%3AMK0827&fields=f12%2Cf13%2Cf14%2Cf1%2Cf2%2Cf4%2Cf3%2Cf152%2Cf5%2Cf6%2Cf17%2Cf18%2Cf15%2Cf16&fid=f3&pn=1&pz=20&po=1&dect=1&ut=fa5fd1943c7b386f172d6893dbfba10b&wbp2u=%7C0%7C0%7C0%7Cweb&_=1762413813341

const fetchEtfsPage = async (page = 1, pageSize = 100) => {
  try {
    const fieldMap = {
      // 代码
      f12: "code",
      // 类型。0: 上证, 1: 深证
      f13: "type",
      // 名称
      f14: "name",
      // 最新价
      f2: "latestPrice",
      // 涨跌额
      f4: "changeAmount",
      // 涨跌幅
      f3: "changePercent",
      // 成交量
      f5: "volume",
      // 成交额
      f6: "turnover",
      // 今开价
      f17: "open",
      // 昨收价
      f18: "prevClose",
      // 最高价
      f15: "high",
      // 最低价
      f16: "low",
    };
    const searchParams = new URLSearchParams({
      np: "1",
      fltt: "1",
      invt: "2",
      fs: "b:MK0021,b:MK0022,b:MK0023,b:MK0024,b:MK0827",
      fields: Object.keys(fieldMap).join(","),
      fid: "f3",
      pn: page.toString(),
      pz: pageSize.toString(),
      po: "1",
      dect: "1",
      ut: "fa5fd1943c7b386f172d6893dbfba10b",
      wbp2u: "|0|0|0|web",
      _: Date.now().toString(),
    });

    const response = await fetch(
      `https://push2.eastmoney.com/api/qt/clist/get?${searchParams.toString()}`
    );
    if (!response.ok) {
      throw new Error(`Error fetching ETFs: ${response.statusText}`);
    }

    const data = (await response.json()) as {
      data: {
        diff: Array<{
          f2: number;
          f3: number;
          f4: number;
          f5: number;
          f6: number;
          f12: string;
          f13: number;
          f14: string;
          f15: number;
          f16: number;
          f17: number;
          f18: number;
        }>;
      };
    };
    return data.data.diff.map((item) => ({
      code: item.f12,
      type: item.f13,
      name: item.f14,
      latestPrice: item.f2,
      changeAmount: item.f4,
      changePercent: item.f3,
      volume: item.f5,
      turnover: item.f6,
      open: item.f17,
      prevClose: item.f18,
      high: item.f15,
      low: item.f16,
    }));
  } catch (err) {
    console.log("fetchEtfsPage error", err);
    return [];
  }
};

export type Etf = Awaited<ReturnType<typeof fetchEtfsPage>>[number];

export const fetchEtfs = async () => {
  let page = 1;
  const pageSize = 100;
  const etfs: Etf[] = [];
  while (true) {
    const result = await fetchEtfsPage(page, pageSize);
    etfs.push(...result);
    if (result.length < pageSize) {
      break;
    }
    await new Promise((resolve) => setTimeout(resolve, 200)); // avoid being blocked
    page += 1;
  }

  return etfs;
};
