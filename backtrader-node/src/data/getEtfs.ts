import { request } from "../utils/request";

/**
 * 获取 ETF 列表
 * @returns Promise<Etf[]>
 */
export async function getEtf(page = 1) {
  const url = "https://push2.eastmoney.com/api/qt/clist/get";
  const params = {
    np: 1,
    fltt: 1,
    invt: 2,
    fs: "b:MK0021,b:MK0022,b:MK0023,b:MK0024,b:MK0827",
    fields: "f12,f13,f14,f1,f2,f4,f3,f152,f5,f6,f17,f18,f15,f16",
    fid: "f3",
    pn: page,
    pz: 100,
    po: 1,
    dect: 1,
    ut: "fa5fd1943c7b386f172d6893dbfba10b",
    wbp2u: "|0|0|0|web",
  };
  const res = await request<{
    data: {
      diff: Array<{
        f1: number;
        // "f2": "最新价",
        f2: number;
        // "f3": "涨跌幅",
        f3: number;
        // "f4": "涨跌额",
        f4: number;
        // "f5": "成交量",
        f5: number;
        // "f6": "成交额",
        f6: number;
        // "f12": "代码",
        f12: string;
        // "f13": 市场。0: 沪市，1: 深市
        f13: number;
        // f14: "名称",
        f14: string;
        // "f15": "最高价",
        f15: number;
        // "f16": "最低价",
        f16: number;
        // "f17": "开盘价",
        f17: number;
        // "f18": "昨收",
        f18: number;
        f152: number;
      }>;
    };
  }>(url, params);
  return (res?.data?.diff || []).map((item) => ({
    a: item.f1,
    b: item.f2,
    c: item.f3,
    d: item.f4,
    e: item.f5,
    f: item.f6,
    // 最高价
    high: item.f15,
  }));
}

/**
 * 获取 ETF 列表
 * @returns Promise<Etf[]>
 */
export async function getEtfs() {}
