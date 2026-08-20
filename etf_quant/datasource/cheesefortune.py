"""芝士财富（stock.cheesefortune.com）日K线数据源。

接口：GET /api/v4/dayKV2/{code}?t={t}
响应 datas.list 每行：[date, prev_close, open, high, low, close, volume, amount]

鉴权流程（对应前端源码，已实测验证）：
  1. token：GET /api/v2/system/apiOuth 公开获取（无需登录）；
  2. 时间戳 ts = 当前毫秒时间戳；
  3. 加密块 l = Base64(AES-ECB-PKCS7(token 按 8 字符分块后的第 ts%10 块))，密钥固定；
  4. zstokv1 请求头 = MD5(str(ts) + l)；
  5. URL 的 t 参数 = 对 ts 做"插入一位"变换（详见 generate_t_param）。
"""

from __future__ import annotations

import base64
import hashlib
import logging
import time
from typing import Any, Dict, List, Optional

import pandas as pd
import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

log = logging.getLogger(__name__)

BASE_URL = "https://stock.cheesefortune.com"
AES_KEY = b"vGEZCiIXRIImAWSv"

# dayKV2 返回列表的字段顺序（实测：prev_close 在前，close 在最后）
KLINE_COLUMNS = ["date", "prev_close", "open", "high", "low", "close", "volume", "amount"]

# 实测通过的完整请求头集合（缺任一关键头或格式不符均返回 500 fail）
BASE_HEADERS = {
    "accept": "*/*",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "content-type": "application/json;charset=utf-8",
    "devicetype": "pc",
    "expires": "-1",
    "pragma": "no-cache",
    "requestfrom": "wechat",
    "runtimetype": "browser",
    "sec-ch-ua": '"Not=A?Brand";v="99", "Google Chrome";v="151", "Chromium";v="151"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "app-version": "",
    "User-Agent": "Mozilla/5.0",
}


def normalize_code(code: str) -> str:
    """代码规范化：510300.SH / 510300SH / 510300 均转为接口格式 510300SH。"""
    return code.strip().replace(".", "").upper()


def get_api_token(session: Optional[requests.Session] = None) -> str:
    """获取 apiAuthToken（公开接口，无鉴权，前端 V2() 同源）。"""
    sess = session or requests.Session()
    resp = sess.get(f"{BASE_URL}/api/v2/system/apiOuth", timeout=15)
    resp.raise_for_status()
    body = resp.json()
    if body.get("code") != "000" or not body.get("datas"):
        raise RuntimeError(f"apiOuth 失败: {body}")
    return body["datas"]


def compute_zstokv1(api_token: str, timestamp_ms: int) -> str:
    """计算 zstokv1 请求头（前端 pu() 同源）。

    取 token 第 timestamp_ms%10 个 8 字符分块做 AES-ECB 加密，再与时间戳拼接取 MD5。
    """
    chunks = [api_token[i:i + 8] for i in range(0, len(api_token), 8)]
    chosen_chunk = chunks[timestamp_ms % 10]
    cipher = AES.new(AES_KEY, AES.MODE_ECB)
    encrypted_chunk = base64.b64encode(cipher.encrypt(pad(chosen_chunk.encode(), 16))).decode()
    return hashlib.md5((str(timestamp_ms) + encrypted_chunk).encode()).hexdigest()


def generate_t_param(timestamp_ms: int) -> str:
    """生成 dayKV2 URL 的 t 参数（前端 Z0() 同源）。

    取时间戳字符串倒数第 4 位数字，插入到第 n 位之前（n = 末位数字，末位为 0 时 n = 2）。
    注意是"插入"而非替换，输出比输入多 1 位（13 位毫秒时间戳 -> 14 位 t 参数）。
    """
    ts_str = str(timestamp_ms)
    digit = ts_str[-4]
    insert_pos = 2 if ts_str[-1] == "0" else int(ts_str[-1])
    return ts_str[: insert_pos - 1] + digit + ts_str[insert_pos - 1 :]


def build_headers(timestamp_ms: int, api_token: str, user_token: str = "", referer: str = "") -> Dict[str, str]:
    """构造请求头；user_token 为登录态（可空），referer 建议传对应页面地址。"""
    headers = dict(BASE_HEADERS)
    headers["zstokv1"] = compute_zstokv1(api_token, timestamp_ms)
    headers["timestamp"] = str(timestamp_ms)
    if user_token:
        headers["token"] = user_token
    if referer:
        headers["Referer"] = referer
    return headers


class CheeseFortuneClient:
    """芝士财富日K线客户端。"""

    def __init__(self, user_token: str = "", timeout: int = 20):
        self.session = requests.Session()
        self.user_token = user_token
        self.timeout = timeout
        self._api_token: Optional[str] = None

    @property
    def api_token(self) -> str:
        if self._api_token is None:
            self._api_token = get_api_token(self.session)
            log.info("apiAuthToken 获取成功，长度 %s", len(self._api_token))
        return self._api_token

    def _get(self, path: str, referer: str = "") -> Dict[str, Any]:
        """GET 请求并附带完整鉴权头，返回 JSON。"""
        timestamp_ms = int(time.time() * 1000)
        url = f"{BASE_URL}{path}?t={generate_t_param(timestamp_ms)}"
        headers = build_headers(timestamp_ms, self.api_token, self.user_token, referer)
        resp = self.session.get(url, headers=headers, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    def fetch_daily(self, code: str) -> pd.DataFrame:
        """拉取指定标的全量日K线。

        返回列：date, prev_close, open, high, low, close, volume, amount
        附数据：df.attrs['factors']（复权因子 [[date_int, factor], ...]）、
               df.attrs['float_shares']（流通份额 [[date_int, shares], ...]）。
        """
        norm = normalize_code(code)
        body = self._get(f"/api/v4/dayKV2/{norm}", referer=f"https://stock.cheesefortune.com/security/index/{norm}")
        if body.get("code") != "000":
            raise RuntimeError(f"dayKV2 失败 [{norm}]: {body.get('code')} {body.get('message')}")
        datas = body.get("datas") or {}
        rows = datas.get("list") or []
        df = pd.DataFrame(rows, columns=KLINE_COLUMNS)
        if not df.empty:
            df["date"] = pd.to_datetime(df["date"].astype(str), format="%Y%m%d")
            for col in KLINE_COLUMNS[1:]:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        df.attrs["factors"] = datas.get("factors") or []
        df.attrs["float_shares"] = datas.get("floatShares") or []
        return df
