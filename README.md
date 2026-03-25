# MCP CalcForge

MCP CalcForge runs as a FastMCP server with a **unified calculator registry**.

## Available MCP tools

- `list_calculators(category=None)`
- `_get_calculator_schema(slug)`
- `calculate(slug, inputs)`

All calculator discovery now goes through the registry in `calcforge/calculators.py`.

## Registry behavior

- Each registered calculator contains `meta`, `schema`, and `handler`.
- `form` calculators receive a typed default schema with validation constraints.
- Interactive tools (`cas`, `rpn`, etc.) are registry-discoverable with session payload schema and executable session handlers.
- `calculate` returns predictable JSON errors for unknown slugs and invalid inputs.

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

- `server.py` – MCP server setup and tool registration
- `calcforge/calculators.py` – unified calculator registry and execution
