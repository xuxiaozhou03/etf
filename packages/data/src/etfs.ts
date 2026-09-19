export interface Etf {
  securityName: string;
  securityCode: string;
  scale: number;
  trackingIndex: string;
  trackIndex: string;
}
export const fetchEtfs = async () => {
  const res = await fetch(
    "https://hongsehuojian.com/fundex-quote/allPage/findListByEtf?classA=&classB=&orderBy=l.scale&order=desc&searchValue=&isSelected=&pageNo=1&pageSize=10000&position=",
    {
      headers: {
        accept: "application/json, text/plain, */*",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
        pro: "RedRocket-PC",
        "sec-ch-ua":
          '"Chromium";v="152", "Not?A_Brand";v="24", "Google Chrome";v="152"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
      },
      body: null,
      method: "GET",
    },
  );

  const data = (await res.json()) as {
    data: {
      data: Etf[];
    };
  };

  const map = new Map<string, Etf>();
  data.data.data.forEach((item) => {
    const exist = map.get(item.trackIndex);
    if (exist && exist.scale > item.scale) {
      return;
    }
    map.set(item.trackIndex, {
      securityName: item.securityName,
      securityCode: item.securityCode,
      scale: item.scale,
      trackingIndex: item.trackingIndex,
      trackIndex: item.trackIndex,
    });
  });

  const list = [...map.values()]
    .filter((item) => {
      if (item.scale < 300000000) {
        return false;
      }
      return true;
    })
    .filter((item) => {
      if (!item.trackIndex) {
        return false;
      }
      return !["债", "短融"].some((a) => item.trackingIndex.includes(a));
    })
    .sort((a, b) => (a.scale < b.scale ? 1 : -1));
  console.log(list.length);

  return list;
};
