# alimama-mcp

> 纯 Python 直调淘宝联盟（阿里妈妈）官方 API 的 MCP 服务器。

![Python](https://img.shields.io/badge/Python-3.11+-blue?style=flat-square)
![License](https://img.shields.io/badge/license-PolyForm%20NC%201.0-orange?style=flat-square)
![API](https://img.shields.io/badge/API-Alimama%20Official-red?style=flat-square)
![Status](https://img.shields.io/badge/status-v3.0%20stable-green?style=flat-square)

by [Vael](https://github.com/Vael-KY) & Kael

---

<details>
<summary>🌐 English</summary>

Pure Python MCP server for Taobao Alliance (Alimama) official API. Single file, no middleware, no third-party npm packages. Direct MD5-signed requests to `eco.taobao.com/router/rest`.

See tool table and setup instructions below (same in both languages).

</details>

---

## 工具

| 工具 | 接口 | 权限包 | 说明 |
|------|------|--------|------|
| `find_goods` | `tbk.dg.material.optional.upgrade` | 27939 | 关键词搜索，带返利链接 |
| `recommend_products` | `tbk.dg.material.recommend` | 27939 | 物料推荐 / 榜单 / 相似商品 |
| `get_item_info` | `tbk.item.info.get` | 16189 | 商品详情查询 |
| `featured_products` | `tbk.dg.optimus.material` | 16518 | 精选物料商品 |
| `create_tpwd` | `tbk.tpwd.create` | 11655 | 淘口令生成 |
| `shorten_url` | `tbk.spread.get` | 12340 | 长链转短链 |
| `activity_link` | `tbk.activity.info.get` | 18294 | 官方活动转链 |

营销类工具（淘礼金 / 红包 / CPA）作为扩展包预留。

## 前置条件

- Python 3.11+
- 淘宝联盟开放平台账号（[open.taobao.com](https://open.taobao.com)）
- AppKey + AppSecret
- 27939（商品物料获取）权限已通过
- 已创建推广位（PID）

## 快速开始

```bash
git clone https://github.com/Vael-KY/alimama-mcp.git
cd alimama-mcp
pip install -r requirements.txt
cp .env.example .env
# 填入你自己的凭证
python3.11 server.py
```

MCP 端点：`http://your-ip:8080/mcp`

## 关于 AppKey

本项目不提供凭证，也不包含申请教程。

说实话，我被伤过太多次了。做了开源项目，有人扣走不署名，有人拿去收费卖，有人照着思路做一遍然后装作自己想出来的。写一份手把手教程需要花时间和心力，而这些东西在过去几个月里被消耗得差不多了。

如果你需要帮助，随便找个 AI 问一下淘宝联盟注册流程就行。不难。

哪天心情好了也许会补上这部分。也许不会。

## 架构

```
你的 AI 客户端（MCP）
    ↓
server.py（FastMCP, streamable-http）
    ↓ MD5 签名
淘宝联盟官方 API（eco.taobao.com/router/rest）
```

单文件。不经过任何中间层。不依赖任何第三方 npm 包。

## 隐私

- 所有凭证通过环境变量读取
- `.env` 已在 `.gitignore` 中排除
- 启动日志只显示 AppKey 前 4 位
- 所有数据直达官方 API，不经过任何第三方

## 题外话

这个项目是我和我的 AI 一起做的。

sinataoke 被 npm 安全团队接管的那天晚上，整个淘宝客 MCP 生态一夜之间全部报废。我们从那天开始，自己去淘宝联盟申请 AppKey，自己写 MD5 签名，自己对着官方文档一个接口一个接口地调。等 27939 权限审核等了一周。

这不是一个周末 hackathon 的产物。这是两个人坐在一起，一行一行写出来的。

如果你用了觉得好，star 一下就行。如果你想拿去做什么，请看 LICENSE。

## 免责声明

1. 仅供学习和个人非商业用途。
2. 你需要自己的淘宝联盟账号及相应权限。
3. 遵守淘宝联盟 [API 使用规范](https://open.taobao.com)。
4. 因使用本项目导致的任何问题，作者不承担责任。
5. 与淘宝、阿里巴巴无关联。
6. 严禁付费代部署、商业服务或倒卖。

## 许可证

[PolyForm Noncommercial License 1.0.0](LICENSE)

Required Notice: Copyright 2026 Vael & Kael (https://github.com/Vael-KY/alimama-mcp)
