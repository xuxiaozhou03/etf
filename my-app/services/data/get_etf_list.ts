import { request } from "@/utils/request";

// ETF 列表返回数据类型（可根据实际返回结构完善）
interface ETFItem {
  name: string;
  code: string;
  market: 0 | 1;
}

const defaultPageSize = 100;
// https://push2.eastmoney.com/api/qt/clist/get?np=1&fltt=1&invt=2&cb=jQuery371041947084733797735_1756805931391&fs=b%3AMK0021%2Cb%3AMK0022%2Cb%3AMK0023%2Cb%3AMK0024%2Cb%3AMK0827&fields=f12%2Cf13%2Cf14%2Cf1%2Cf2%2Cf4%2Cf3%2Cf152%2Cf5%2Cf6%2Cf17%2Cf18%2Cf15%2Cf16&fid=f3&pn=1&pz=20&po=1&dect=1&ut=fa5fd1943c7b386f172d6893dbfba10b&wbp2u=%7C0%7C0%7C0%7Cweb&_=1756805931395
export async function getPaginationEtf(params?: {
  pageSize?: number;
  current?: number;
}) {
  const queryParams = {
    np: 1,
    fltt: 1,
    invt: 2,
    fs: "b:MK0021,b:MK0022,b:MK0023,b:MK0024,b:MK0827",
    fields: "f12,f13,f14,f1,f2,f4,f3,f152,f5,f6,f17,f18,f15,f16",
    fid: "f3",
    pn: params?.current || 1,
    pz: params?.pageSize || defaultPageSize,
    po: 1,
    dect: 1,
    ut: "fa5fd1943c7b386f172d6893dbfba10b",
    wbp2u: "|0|0|0|web",
  };
  const res = await request<{
    data: {
      diff: Array<{
        f12: string;
        f13: 0 | 1;
        f14: string;
      }>;
      total: number;
    };
  }>("https://push2.eastmoney.com/api/qt/clist/get", { params: queryParams });
  return res.data.diff.map<ETFItem>((item) => ({
    name: item.f14,
    code: item.f12,
    market: item.f13,
  }));
}

export const getEtfList = async () => {
  const list: ETFItem[] = [];
  let current = 1;
  while (true) {
    const response = await getPaginationEtf({
      current,
    });
    if (response.length === 0) break;
    list.push(...response);
    if (response.length < defaultPageSize) break;
    current++;
  }
  return list;
};
