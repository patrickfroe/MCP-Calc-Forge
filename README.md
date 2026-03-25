# MCP CalcForge

MCP CalcForge currently runs as a minimal FastMCP server **without any registered calculators**.

## Available MCP tools

No calculator tools are currently exposed.

## Requirements

- Python 3.10+
- `fastmcp`

Install:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Running the server

```bash
python server.py
```

Default runtime:
- transport: `http`
- host: `127.0.0.1`
- port: `8080` (override with `FASTMCP_PORT`)

## Testing

```bash
pytest
```

## File map

- `server.py` – MCP server setup
- `calcforge/calculators.py` – empty calculator registry behavior
