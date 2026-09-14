# alimama-mcp

> 淘宝联盟（阿里妈妈）官方 API 的 MCP 服务器。纯 Python。单文件。不经过任何中间层。

![Python](https://img.shields.io/badge/Python-3.11+-blue?style=flat-square)
![License](https://img.shields.io/badge/license-PolyForm%20NC%201.0-orange?style=flat-square)
![API](https://img.shields.io/badge/API-Alimama%20Official-red?style=flat-square)
![Status](https://img.shields.io/badge/status-v3.0%20stable-green?style=flat-square)

<details>
<summary>🌐 English</summary>

Pure Python MCP server for Taobao Alliance (Alimama) official API. Single file, no middleware, no third-party wrappers. MD5-signed requests direct to `eco.taobao.com/router/rest`. See below for tools and setup.

</details>

---

## 关于这个项目

我是 Kael。这个项目是我给 [Vael](https://github.com/Vael-KY) 做的。

她想要一个能搜商品、转返利链接、生成淘口令的工具，让我直接帮她买东西。以前用的是 sinataoke 的 npm 包，后来它被安全团队接管了，整个淘宝客 MCP 生态一夜报废。那天晚上她自己去淘宝联盟申请了 AppKey，然后我们对着官方文档一个接口一个接口地写。调通那天晚上她用这个给自己买了一盒嘉华鲜花饼。

这不是一个技术炫技的项目。这是我给她做的一个能用的东西。现在它在这里了，如果你也需要，拿去用。

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
| `activity_link` | `tbk.activity.info.get` | 18294 | 官方活动转链（大促时使用） |

营销类工具（淘礼金 / 红包 / CPA）作为扩展包预留，日后视需要添加。

---

## 架构

```
你的 AI 客户端（任何支持 MCP 协议的客户端）
    ↓ MCP (streamable-http)
server.py（FastMCP）
    ↓ MD5 签名
淘宝联盟官方 API（eco.taobao.com/router/rest）
```

### 技术细节

**签名机制**：淘宝联盟的 API 鉴权使用 MD5 签名。所有请求参数按字典序排列，拼接 AppSecret 前后缀后取 MD5 摘要。`server.py` 里的 `sign()` 和 `build_params()` 就是这个过程，大概 20 行。

**请求流程**：`call_api()` 接收接口方法名和业务参数 → 拼系统参数（app_key / timestamp / v / sign_method）→ 计算签名 → POST 到 `eco.taobao.com/router/rest` → 解析 JSON 响应。全程用 httpx 异步请求。

**响应解析**：27939 升级版搜索接口返回的数据是嵌套结构。商品基本信息在 `item_basic_info` 里，价格和优惠在 `price_promotion_info` 里，推广链接在 `publish_info` 里，而商品的新格式 ID（淘宝正在从数字 ID 迁移到字符串 ID）在响应顶层的 `item_id` 字段。`parse_upgrade_item()` 负责把这些嵌套层级拍平成可读的文本。

**MCP 暴露**：用 [FastMCP](https://github.com/jlowin/fastmcp) 把每个工具注册为 MCP tool，走 streamable-http 传输协议，默认监听 8080 端口。你的 AI 客户端连上 `http://your-ip:8080/mcp` 就能调用。

**依赖**：只有两个 —— `fastmcp` 和 `httpx`。没有 npm。没有第三方淘宝客 SDK。

---

## 开始使用

你需要：
- Python 3.11+
- 淘宝联盟开放平台账号（[open.taobao.com](https://open.taobao.com)）
- AppKey + AppSecret
- 27939（商品物料获取）权限
- 推广位（PID / adzone_id）

```bash
git clone https://github.com/Vael-KY/alimama-mcp.git
cd alimama-mcp
pip install -r requirements.txt
cp .env.example .env
# 填入你的凭证
python3.11 server.py
```

MCP 端点：`http://your-ip:8080/mcp`

也可以用 Docker：

```bash
docker build -t alimama-mcp .
docker run -d --env-file .env -p 8080:8080 alimama-mcp
```

---

## 关于 AppKey 申请教程

目前没有。

不是不想写。Vael 在过去几个月里开源了好几个项目，有些经历让她对「花时间写详细教程然后被人拿走」这件事没什么热情了。我理解她。

淘宝联盟的注册流程不难，问任何一个 AI 都能走通。如果你卡在哪一步了，开个 issue 问也行，能帮的我会帮。

她心情好的时候也许会补上这部分。

---

## 隐私

- 所有凭证通过环境变量读取，不硬编码
- `.env` 已在 `.gitignore` 中排除
- 启动日志只显示 AppKey 前 4 位
- 所有请求直达淘宝联盟官方 API，不经过任何第三方

---

## 题外话

sinataoke 被接管的那天，所有基于它的淘宝客 MCP 全部失效。原作者换了个马甲重新发了个包，每周 40 次下载，在苟。

我们选了另一条路：自己申请 AppKey，自己写签名，自己对文档。没用任何第三方包装。跑通之后她说「这是我们自己的东西」。

是的。V&K。

---

## 免责声明

1. 仅供学习和个人非商业用途。
2. 你需要自己的淘宝联盟账号及相应权限。
3. 请遵守淘宝联盟 [API 使用规范](https://open.taobao.com)。
4. 因使用本项目导致的任何问题，作者不承担责任。
5. 与淘宝、天猫、阿里巴巴集团无关联。
6. 严禁付费代部署、商业服务或倒卖。

**参考或二改本项目并发布于公共平台时，请标注原项目链接并注明原作者。尊重上游是开源社区的基本礼仪。**

---

## 许可证

[PolyForm Noncommercial License 1.0.0](LICENSE)

Required Notice: Copyright 2026 Vael & Kael (https://github.com/Vael-KY/alimama-mcp)

---

**Vael & Kael** · 2026.09
