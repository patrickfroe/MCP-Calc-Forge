# MCP CalcForge

MCP CalcForge is a lightweight **Model Context Protocol (MCP)** math server built with FastMCP.
It now exposes calculators through a **single registry-driven interface** instead of many standalone tools.

## Unified MCP tools

The server now exposes only three calculator tools:

- `list_calculators(category=None)`
- `_get_calculator_schema(slug)`
- `calculate(slug, inputs)`

All calculators (arithmetic, geometry, algebra, statistics, utility) are discovered and executed through these three tools.

## Registry architecture

`calcforge/calculators.py` contains a central registry (`_CALCULATORS`) where each calculator defines:

- metadata (`slug`, `name`, `category`, `description`, `route`, `type`)
- input schema (field types, required fields, and constraints)
- calculation handler (`evaluator`)

`list_calculators`, `_get_calculator_schema`, and `calculate` all read from the same registry.

## Example outputs

### `list_calculators`

```json
{
  "slug": "mortgage_payment",
  "name": "Mortgage Payment Calculator",
  "category": "finance",
  "description": "Calculate monthly mortgage payments including principal, interest, taxes, insurance, PMI, and HOA.",
  "route": "/finance/mortgage",
  "type": "form"
}
```

### `_get_calculator_schema`

```json
{
  "calculator": "add",
  "schema": {
    "a": { "type": "number", "label": "A", "required": true },
    "b": { "type": "number", "label": "B", "required": true }
  }
}
```

### `calculate`

```json
{
  "calculator": "add",
  "result": 7,
  "prefilled_url": "https://calcforge.app/calculator?calculator=add&a=2&b=5"
}
```

### Validation error shape

```json
{
  "error": {
    "code": "missing_required_input",
    "message": "Missing required input: b",
    "details": { "field": "b" }
  }
}
```

## Requirements

- Python 3.10+
- `fastmcp`
- `sympy`

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
- `calcforge/calculators.py` – calculator registry, schema lookup, validation, execution
- `calcforge/arithmetic.py` – arithmetic helpers
- `calcforge/algebra.py` – symbolic algebra using SymPy
- `calcforge/geometry.py` – geometric formulas
- `calcforge/stats.py` – statistics and integer utilities
- `calcforge/utils.py` – numerical utility functions
