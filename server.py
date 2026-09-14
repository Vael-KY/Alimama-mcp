#!/usr/bin/env python3
"""
V&K alimama-mcp v3.0
Pure Python, official Taobao Alliance (Alimama) API
No third-party wrappers

V&K
"""
import os
import sys
import json
import hashlib
from datetime import datetime

import httpx
from fastmcp import FastMCP

sys.stdout.reconfigure(line_buffering=True)

# ==================== Config ====================
APP_KEY = os.environ.get("TAOBAO_APP_KEY", "")
APP_SECRET = os.environ.get("TAOBAO_APP_SECRET", "")
SESSION = os.environ.get("TAOBAO_SESSION", "")
ADZONE_ID = os.environ.get("TAOBAO_ADZONE_ID", "")
PORT = int(os.environ.get("PORT", "8080"))

API_URL = "https://eco.taobao.com/router/rest"

mcp = FastMCP(
    name="V&K alimama-mcp",
    instructions="Taobao product search, affiliate link conversion, taocode generation. Direct official Alimama API.",
)


# ==================== Signature ====================
def sign(params: dict) -> str:
    sorted_params = sorted(params.items())
    s = APP_SECRET
    for k, v in sorted_params:
        s += f"{k}{v}"
    s += APP_SECRET
    return hashlib.md5(s.encode("utf-8")).hexdigest().upper()


def build_params(method: str, biz_params: dict) -> dict:
    sys_params = {
        "method": method,
        "app_key": APP_KEY,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "format": "json",
        "v": "2.0",
        "sign_method": "md5",
    }
    if SESSION:
        sys_params["session"] = SESSION
    all_params = {**sys_params, **biz_params}
    all_params["sign"] = sign(all_params)
    return all_params


async def call_api(method: str, biz_params: dict) -> dict:
    if not APP_KEY or not APP_SECRET:
        return {"error": "TAOBAO_APP_KEY and TAOBAO_APP_SECRET required"}
    params = build_params(method, biz_params)
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(API_URL, data=params)
        data = resp.json()
    if "error_response" in data:
        err = data["error_response"]
        return {"error": f"{err.get('msg', '')} (code={err.get('code', '')}, sub_msg={err.get('sub_msg', '')})"}
    return data


# ==================== Parsers ====================
def parse_upgrade_item(item: dict) -> str:
    item_id = item.get("item_id", "")
    basic = item.get("item_basic_info", {})
    price_info = item.get("price_promotion_info", {})
    pub_info = item.get("publish_info", {})
    income_info = pub_info.get("income_info", {})

    title = basic.get("title", "")
    shop = basic.get("shop_title", "")
    volume = basic.get("volume", "0")
    annual_vol = basic.get("annual_vol", "")

    price = price_info.get("zk_final_price", "")
    final_price = price_info.get("final_promotion_price", "")
    reserve_price = price_info.get("reserve_price", "")

    commission_rate = income_info.get("commission_rate", "0")
    rate_pct = f"{float(commission_rate) / 100:.1f}%" if commission_rate and commission_rate != "0" else ""
    income_rate = pub_info.get("income_rate", "")

    url = pub_info.get("coupon_share_url", "") or pub_info.get("click_url", "")
    if url and url.startswith("//"):
        url = "https:" + url

    line = f"\u3010{title}\u3011"
    if item_id:
        line += f"\n  ID: {item_id}"
    line += f"\n  Shop: {shop}"
    if price:
        line += f"\n  Price: \u00a5{price}"
        if final_price and final_price.strip() != price:
            line += f" -> \u00a5{final_price.strip()}"
    if reserve_price and reserve_price != price:
        line += f" (was \u00a5{reserve_price})"

    sales_parts = []
    if volume and str(volume) != "0":
        sales_parts.append(f"Monthly: {volume}")
    if annual_vol:
        sales_parts.append(f"Annual: {annual_vol}")
    if income_rate:
        sales_parts.append(f"Rate: {income_rate}%")
    if rate_pct:
        sales_parts.append(f"Commission: {rate_pct}")
    if sales_parts:
        line += f"\n  {' | '.join(sales_parts)}"

    promo_paths = price_info.get("final_promotion_path_list", {}).get("final_promotion_path_map_data", [])
    if promo_paths:
        promos = [f"{p.get('promotion_title', '')}:{p.get('promotion_desc', '')}" for p in promo_paths[:3]]
        line += f"\n  Promo: {' / '.join(promos)}"

    if url:
        line += f"\n  Link: {url}"

    return line


def parse_basic_item(item: dict) -> str:
    title = item.get("title", "")
    price = item.get("zk_final_price", "")
    shop = item.get("nick", "") or item.get("shop_title", "")
    volume = item.get("volume", "0")
    url = item.get("click_url", "") or item.get("item_url", "")
    if url and url.startswith("//"):
        url = "https:" + url

    line = f"\u3010{title}\u3011\n  Shop: {shop}\n  Price: \u00a5{price}\n  Monthly: {volume}"
    if url:
        line += f"\n  Link: {url}"
    return line


# ==================== Tools: 27939 ====================

@mcp.tool()
async def find_goods(keyword: str, count: int = 20) -> str:
    """
    Search Taobao products with affiliate links.
    Scope: 27939 (upgrade search API)

    Args:
        keyword: search keyword
        count: max results, default 20, max 100
    """
    if not ADZONE_ID:
        return "TAOBAO_ADZONE_ID required"
    biz = {
        "q": keyword,
        "page_size": str(min(count, 100)),
        "page_no": "1",
        "platform": "2",
        "sort": "total_sales_des",
        "adzone_id": ADZONE_ID,
    }
    data = await call_api("taobao.tbk.dg.material.optional.upgrade", biz)
    if "error" in data:
        return f"Search failed: {data['error']}"
    try:
        result = data.get("tbk_dg_material_optional_upgrade_response", {})
        result_list = result.get("result_list", {}).get("map_data", [])
        if not result_list:
            return f"No results for '{keyword}'."
        total = result.get("total_results", "?")
        items = [parse_upgrade_item(item) for item in result_list[:count]]
        return f"Found {total}, showing {len(items)}:\n\n" + "\n\n".join(items)
    except Exception as e:
        return f"Parse error: {e}"


@mcp.tool()
async def recommend_products(material_id: str, count: int = 10, item_id: str = "") -> str:
    """
    Get recommended products (curated lists, rankings, similar items).
    Scope: 27939

    Args:
        material_id: official material ID (required)
        count: max results, default 10
        item_id: for similar recommendations (required when material_id=13256)
    """
    if not ADZONE_ID:
        return "TAOBAO_ADZONE_ID required"
    biz = {
        "material_id": material_id,
        "page_size": str(min(count, 100)),
        "page_no": "1",
        "adzone_id": ADZONE_ID,
    }
    if item_id:
        biz["item_id"] = item_id
    data = await call_api("taobao.tbk.dg.material.recommend", biz)
    if "error" in data:
        return f"Failed: {data['error']}"
    try:
        result = data.get("tbk_dg_material_recommend_response", {})
        result_list = result.get("result_list", {}).get("map_data", [])
        if not result_list:
            return "No recommendations."
        items = [parse_upgrade_item(item) for item in result_list[:count]]
        return f"Recommended {len(items)}:\n\n" + "\n\n".join(items)
    except Exception as e:
        return f"Parse error: {e}"


# ==================== Tools: 16189 ====================

@mcp.tool()
async def get_item_info(item_ids: str) -> str:
    """
    Query product details. Batch supported, comma-separated, max 40.
    Scope: 16189
    Note: use new-format item IDs from search results.

    Args:
        item_ids: product ID(s), comma-separated
    """
    biz = {
        "num_iids": item_ids,
        "platform": "2",
    }
    data = await call_api("taobao.tbk.item.info.get", biz)
    if "error" in data:
        return f"Query failed: {data['error']}"
    try:
        results = data.get("tbk_item_info_get_response", {}).get("results", {}).get("n_tbk_item", [])
        if not results:
            return "No item info found."
        items = [parse_basic_item(item) for item in results]
        return "\n\n".join(items)
    except Exception as e:
        return f"Parse error: {e}"


# ==================== Tools: 16518 ====================

@mcp.tool()
async def featured_products(material_id: str = "28026", count: int = 10) -> str:
    """
    Get featured/curated products (rankings, deals, coupons).
    Scope: 16518
    Common IDs: 28026 (top picks), 27446 (live coupons), 28890 (personalized)

    Args:
        material_id: material ID, default 28026
        count: max results, default 10
    """
    if not ADZONE_ID:
        return "TAOBAO_ADZONE_ID required"
    biz = {
        "material_id": material_id,
        "page_size": str(min(count, 100)),
        "page_no": "1",
        "adzone_id": ADZONE_ID,
    }
    data = await call_api("taobao.tbk.dg.optimus.material", biz)
    if "error" in data:
        return f"Failed: {data['error']}"
    try:
        result = data.get("tbk_dg_optimus_material_response", {})
        result_list = result.get("result_list", {}).get("map_data", [])
        if not result_list:
            return "No featured products."
        items = [parse_upgrade_item(item) for item in result_list[:count]]
        return f"Featured {len(items)}:\n\n" + "\n\n".join(items)
    except Exception as e:
        return f"Parse error: {e}"


# ==================== Tools: 11655 ====================

@mcp.tool()
async def create_tpwd(url: str) -> str:
    """
    Generate Tao Password (taocode) from affiliate link.
    Scope: 11655
    Note: url must be an official affiliate link (s.click.taobao.com etc).

    Args:
        url: affiliate promotion link
    """
    biz = {"url": url}
    data = await call_api("taobao.tbk.tpwd.create", biz)
    if "error" in data:
        return f"Failed: {data['error']}"
    try:
        result = data.get("tbk_tpwd_create_response", {}).get("data", {})
        password = result.get("password_simple", "")
        model = result.get("model", "")
        if password:
            return f"Taocode: {password}\nCopy and open Taobao app.\n\nFull: {model}"
        if model:
            return f"Taocode: {model}"
        return "Failed to generate taocode."
    except Exception as e:
        return f"Parse error: {e}"


# ==================== Tools: 12340 ====================

@mcp.tool()
async def shorten_url(url: str) -> str:
    """
    Convert long affiliate link to short link.
    Scope: 12340
    Supported: uland.taobao.com, s.click.taobao.com, ai.taobao.com, temai.taobao.com

    Args:
        url: long affiliate link
    """
    biz = {"requests": json.dumps([{"url": url}])}
    data = await call_api("taobao.tbk.spread.get", biz)
    if "error" in data:
        return f"Failed: {data['error']}"
    try:
        results = data.get("tbk_spread_get_response", {}).get("results", {}).get("tbk_spread", [])
        if results:
            content = results[0].get("content", "")
            err_msg = results[0].get("err_msg", "")
            if err_msg and err_msg != "OK":
                return f"Failed: {err_msg}"
            return f"Short link: {content}"
        return "Conversion failed."
    except Exception as e:
        return f"Parse error: {e}"


# ==================== Tools: 18294 ====================

@mcp.tool()
async def activity_link(activity_material_id: str) -> str:
    """
    Get official campaign promotion links (Taobao/Tmall/Eleme events).
    Scope: 18294
    Get activity IDs from Alimama dashboard.

    Args:
        activity_material_id: official campaign ID (required)
    """
    if not ADZONE_ID:
        return "TAOBAO_ADZONE_ID required"
    biz = {
        "activity_material_id": activity_material_id,
        "adzone_id": ADZONE_ID,
    }
    data = await call_api("taobao.tbk.activity.info.get", biz)
    if "error" in data:
        return f"Failed: {data['error']}"
    try:
        result = data.get("tbk_activity_info_get_response", {}).get("data", {})
        lines = []
        page_name = result.get("page_name", "")
        if page_name:
            lines.append(f"Campaign: {page_name}")
        start = result.get("page_start_time", "")
        end = result.get("page_end_time", "")
        if start and end:
            lines.append(f"Period: {start} ~ {end}")
        click_url = result.get("click_url", "")
        if click_url:
            lines.append(f"Link: {click_url}")
        short_url = result.get("short_click_url", "")
        if short_url:
            lines.append(f"Short: {short_url}")
        return "\n".join(lines) if lines else "No campaign link found."
    except Exception as e:
        return f"Parse error: {e}"


# ==================== Tools: Status ====================

@mcp.tool()
async def server_info() -> str:
    """Server status and configuration check."""
    has_key = "\u2713" if APP_KEY else "\u2717"
    has_secret = "\u2713" if APP_SECRET else "\u2717"
    has_session = "\u2713" if SESSION else "\u2717"
    has_adzone = "\u2713" if ADZONE_ID else "\u2717"
    return (
        f"V&K alimama-mcp v3.0\n"
        f"Official Alimama API\n"
        f"AppKey: {has_key} | AppSecret: {has_secret}\n"
        f"Session: {has_session} | AdzoneID: {has_adzone}\n"
        f"Port: {PORT}\n\n"
        f"Tools: find_goods / recommend_products / get_item_info\n"
        f"       featured_products / create_tpwd / shorten_url / activity_link"
    )


# ==================== Start ====================
if __name__ == "__main__":
    missing = []
    if not APP_KEY:
        missing.append("TAOBAO_APP_KEY")
    if not APP_SECRET:
        missing.append("TAOBAO_APP_SECRET")
    if missing:
        print(f"Missing: {', '.join(missing)}")
        sys.exit(1)
    print(
        f"V&K alimama-mcp v3.0\n"
        f"  Port: {PORT}\n"
        f"  AppKey: {APP_KEY[:4]}****\n"
        f"  API: {API_URL}\n",
        flush=True,
    )
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=PORT,
    )
