import { request } from "@etf/utils";

interface OriginalEtfItem {
  f2: string; // 最新价
  f3: string; // 涨跌幅
  f4: string; // 涨跌额
  f5: string; // 成交量
  f6: string; // 成交额
  f12: string; // 代码
  f13: string; // 市场 0=深圳 1=上海
  f14: string; // 名称
  f15: string; // 最高价
  f16: string; // 最低价
  f17: string; // 开盘价
  f18: string; // 昨收价
}

export interface EtfItem {
  code: string;
  market: 0 | 1;
  name: string;
  price: number;
  change: number;
  changeAmount: number;
  volume: number;
  amount: number;
  open: number;
  high: number;
  low: number;
  prevClose: number;
}

// 获取 ETF 列表，默认第一页，每页100条
export const fetchEtfListWithPage = async (
  page = 1,
  size = 100
): Promise<EtfItem[]> => {
  // https://push2.eastmoney.com/api/qt/clist/get?np=1&fltt=1&invt=2&fs=b%3AMK0021%2Cb%3AMK0022%2Cb%3AMK0023%2Cb%3AMK0024%2Cb%3AMK0827&fields=f12%2Cf13%2Cf14%2Cf1%2Cf2%2Cf4%2Cf3%2Cf152%2Cf5%2Cf6%2Cf17%2Cf18%2Cf15%2Cf16&fid=f3&pn=1&pz=20&po=1&dect=1&ut=fa5fd1943c7b386f172d6893dbfba10b&wbp2u=%7C0%7C0%7C0%7Cweb&_=1757414269430
  const url = "https://push2.eastmoney.com/api/qt/clist/get";
  const params = {
    np: 1,
    fltt: 1,
    invt: 2,
    fs: "b:MK0021,b:MK0022,b:MK0023,b:MK0024,b:MK0827",
    fields: "f12,f13,f14,f1,f2,f4,f3,f152,f5,f6,f17,f18,f15,f16",
    fid: "f3",
    pn: page,
    pz: size,
    po: 1,
    dect: 1,
    ut: "fa5fd1943c7b386f172d6893dbfba10b",
    wbp2u: "|0|0|0|web",
    _: Date.now(),
  };
  const res = await request<{ data: { diff: OriginalEtfItem[] } }>(`${url}`, {
    params,
  });
  return res.data.diff.map((item) => ({
    code: item.f12,
    market: parseInt(item.f13) as 0 | 1,
    name: item.f14,
    price: parseFloat(item.f2) / 1000,
    change: parseFloat(item.f3) / 1000,
    changeAmount: parseFloat(item.f4),
    volume: parseInt(item.f5, 10),
    amount: parseFloat(item.f6),
    open: parseFloat(item.f17) / 1000,
    high: parseFloat(item.f15) / 1000,
    low: parseFloat(item.f16) / 1000,
    prevClose: parseFloat(item.f18) / 1000,
  }));
};

export const fetchAllEtfList = async (): Promise<EtfItem[]> => {
  let allItems: EtfItem[] = [];
  let page = 1;
  const size = 100;
  while (true) {
    const items = await fetchEtfListWithPage(page, size);
    if (items.length === 0) break;
    allItems = allItems.concat(items);
    if (items.length < size) break; // 最后一页
    page += 1;
  }
  return allItems;
};
