// https://fundf10.eastmoney.com/jbgk_159322.html

import { request, safeEval } from "@etf/utils";

/**
 * 规模变动
 * 地址：https://fundf10.eastmoney.com/gmbd_159322.html
 * 接口：https://fundf10.eastmoney.com/FundArchivesDatas.aspx?type=jzcgm&code=159322&rt=0.9678474715177273
 */

export const fetchScaleChange = async (code = "159322") => {
  const url = "https://fundf10.eastmoney.com/FundArchivesDatas.aspx";
  const params = {
    type: "jzcgm",
    code,
    rt: Math.random(),
  };
  const res = await request<string>(url, {
    params,
  });
  return safeEval<{
    jzcgm_apidata: Array<[number, number]>;
  }>(res)?.jzcgm_apidata;
};
