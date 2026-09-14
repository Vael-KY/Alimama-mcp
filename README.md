# alimama-mcp

Pure Python MCP server for Taobao Alliance (Alimama) official API.

by [Vael](https://github.com/Vael-KY) & Kael

## Tools

| Tool | API | Scope | What it does |
|------|-----|-------|--------------|
| `find_goods` | `tbk.dg.material.optional.upgrade` | 27939 | Search products with affiliate links |
| `recommend_products` | `tbk.dg.material.recommend` | 27939 | Curated lists / similar items |
| `get_item_info` | `tbk.item.info.get` | 16189 | Product details |
| `featured_products` | `tbk.dg.optimus.material` | 16518 | Featured picks / rankings |
| `create_tpwd` | `tbk.tpwd.create` | 11655 | Generate Tao Password |
| `shorten_url` | `tbk.spread.get` | 12340 | Long link to short link |
| `activity_link` | `tbk.activity.info.get` | 18294 | Campaign promotion links |

Marketing tools (TaoLiJin, Red Packets, CPA reports) reserved for future expansion.

## Prerequisites

- Python 3.11+
- Taobao Alliance developer account ([open.taobao.com](https://open.taobao.com))
- AppKey + AppSecret
- Scope 27939 (product material) approved
- Promotion slot (PID) created

## Setup

```bash
git clone https://github.com/Vael-KY/alimama-mcp.git
cd alimama-mcp
pip install -r requirements.txt
cp .env.example .env
# fill in your credentials
python3.11 server.py
```

MCP endpoint: `http://your-ip:8080/mcp`

## About AppKey

This project does not provide credentials or walk you through the application process.

The author has been burned too many times by people who take open-source work, strip attribution, and resell it as their own. Writing a step-by-step AppKey tutorial is not something I have the energy for right now. If you need help, any LLM can walk you through the Taobao Alliance registration flow.

I may publish a guide in the future when I feel like it.

## Architecture

```
Your AI client (MCP)
    ↓
server.py (FastMCP, streamable-http)
    ↓ MD5 signature
Alimama Official API (eco.taobao.com/router/rest)
```

Single file. No middleware. No third-party npm packages.

## Privacy

- All credentials via environment variables
- `.env` is gitignored
- Startup log shows only first 4 chars of AppKey
- All data goes directly to official API

## Disclaimer

1. For personal, non-commercial use only.
2. You need your own Taobao Alliance account and approved permissions.
3. You are responsible for complying with [Alimama API Terms](https://open.taobao.com).
4. The author is not liable for any account bans, financial losses, or legal issues arising from your use of this project.
5. Not affiliated with Taobao, Tmall, or Alibaba Group.
6. Taobao Alliance may change API rules at any time. No guarantee of permanent availability.
7. Paid deployment, commercial services, and resale are strictly prohibited.

## License

[PolyForm Noncommercial License 1.0.0](LICENSE)

Required Notice: Copyright 2026 Vael & Kael (https://github.com/Vael-KY/alimama-mcp)
