# MCP CalcForge

MCP CalcForge is a lightweight **Model Context Protocol (MCP)** math server built with FastMCP. It exposes a collection of calculation tools over an HTTP JSON-RPC interface so MCP-compatible clients can call arithmetic, algebra, geometry, statistics, and utility functions.

The project is intentionally small and modular:
- `server.py` defines the MCP server and registers all tools.
- `calcforge/` contains domain-specific and utility math modules.

## Features

### 1) Arithmetic tools
- `add(a, b)`
- `subtract(a, b)`
- `multiply(a, b)`
- `divide(a, b)` (raises `ZeroDivisionError` on division by zero)
- `percentage_of(value, percent)`
- `to_fraction(value)` (returns reduced `fractions.Fraction`)

### 2) Geometry tools
- `circle_area(radius)`
- `circle_circumference(radius)`
- `rectangle_area(a, b)`
- `rectangle_perimeter(a, b)`
- `triangle_area(base, height)`
- `sphere_volume(radius)`
- `cylinder_volume(radius, height)`
- `cone_volume(radius, height)`
- `pyramid_volume(base_area, height)`

### 3) Algebra tools (via SymPy)
- `solve_quadratic(a, b, c)`
- `solve_linear_system(equations, variables)`
- `factor_polynomial(expr)`
- `find_roots(expr)`

### 4) Statistics and number theory tools
- `mean(numbers)`
- `std_dev(numbers)` (population standard deviation)
- `gcd(a, b)`
- `lcm(a, b)`
- `prime_factors(n)`

### 5) Utility tools
- `log_base(x, base)`
- `power(base, exponent)`
- `to_scientific_notation(x, precision=3)`
- `to_binary(n)`
- `from_binary(bin_str)`

### 6) Tool discovery helpers
- `list_calculators()` returns all calculator tool names.
- `get_calculator_schema(calculator)` returns a tool's description, parameters, and return type.

## Architecture overview

The server follows a simple delegation pattern:
1. A function is exposed as an MCP tool in `server.py` using `@mcp.tool()`.
2. That function delegates directly to a module function.
3. Domain modules contain the implementation and validation logic.

This keeps the transport layer (MCP/FastMCP) separate from the calculation logic, making maintenance and testing easier.

## Requirements

This repository is Python-based and requires:
- Python 3.10+
- `fastmcp`
- `sympy`

Because no lockfile or dependency manifest is currently included, install dependencies manually (or add your preferred package manager config).

Example:

```bash
python -m venv .venv
source .venv/bin/activate
pip install fastmcp sympy
```

## Running the server

Start the MCP server:

```bash
python server.py
```

By default it runs with:
- transport: `http`
- host: `127.0.0.1`
- port: `8080` (override with `FASTMCP_PORT`)

Example with custom port:

```bash
FASTMCP_PORT=8081 python server.py
```

## Testing the server with MCP Inspector

You can validate that the server is reachable and that tools are callable by using the official MCP Inspector.

1. Start the server in one terminal:

   ```bash
   python server.py
   ```

2. In a second terminal, start MCP Inspector:

   ```bash
   npx @modelcontextprotocol/inspector
   ```

3. In the Inspector UI:
   - Select **Streamable HTTP** transport.
   - Set the server URL to `http://127.0.0.1:8080/mcp` (or your custom `FASTMCP_PORT`).
   - Connect and open the **Tools** tab.
   - Run a quick check call such as `add` with `a=2` and `b=3` (expected result: `5`).

If you started the server with a custom port, update the Inspector URL accordingly (for example `http://127.0.0.1:8081/mcp`).

## How clients use it

An MCP-compatible client can connect to the server endpoint and invoke registered tools by name with structured arguments. Tool signatures and docstrings are defined in `server.py`, while the implementation lives in the backing modules.

## Error behavior and validation notes

- `divide(a, b)` raises `ZeroDivisionError` when `b == 0`.
- `solve_quadratic(a, b, c)` raises `ValueError` when `a == 0`.
- `find_roots(expr)` raises `ValueError` for multivariate expressions.
- `prime_factors(n)` raises `ValueError` when `n < 2`.
- `mean([])` and `std_dev([])` propagate `statistics.StatisticsError`.

## Development notes

### Suggested project improvements
If you plan to extend this repository, consider adding:
- A dependency manifest (`pyproject.toml` or `requirements.txt`)
- Automated tests (e.g., `pytest`) for each math module
- CI checks (lint, type checks, tests)
- Versioning and changelog practices

### Code style
The current codebase favors:
- Small, focused modules
- Explicit function interfaces and docstrings
- Minimal abstraction between MCP tools and math logic

## File map

- `server.py` – MCP server setup and tool registration
- `calcforge/arithmetic.py` – core arithmetic helpers
- `calcforge/algebra.py` – symbolic algebra operations using SymPy
- `calcforge/geometry.py` – geometric formulas
- `calcforge/stats.py` – statistics and integer utilities
- `calcforge/utils.py` – misc numerical utility functions

## License

No license file is currently present in this repository. Add a license if you intend to distribute or publish this project.
