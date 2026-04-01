from __future__ import annotations

from pathlib import Path

from app.mcp import ui_resources
from app.mcp.ui_resources import get_ui_resource_specs


def test_ui_resource_specs_expose_ui_scheme_and_restrictive_default_csp() -> None:
    specs = get_ui_resource_specs()
    assert specs

    resource = specs[0]
    assert resource.uri.startswith("ui://")
    assert resource.mime_type == "text/html"
    assert resource.meta["_meta"]["ui"]["csp"]["connectDomains"] == []
    assert resource.meta["_meta"]["ui"]["csp"]["resourceDomains"] == []
    assert resource.meta["_meta"]["ui"]["bridge"]["version"] == "1.0"
    assert resource.meta["_meta"]["ui"]["bridge"]["incomingMessageTypes"] == ["tool-result"]
    assert resource.meta["_meta"]["ui"]["bridge"]["outgoingMessageTypes"] == ["tool-call-request"]
    assert resource.meta["_meta"]["ui"]["bridge"]["supportsLegacyTopLevelType"] is True
    assert resource.meta["_meta"]["ui"]["displayModes"] == ["inline", "fullscreen"]
    assert resource.meta["_meta"]["ui"]["theming"]["supportsHostTheme"] is True
    assert resource.meta["_meta"]["ui"]["hostContext"]["acceptsLocale"] is True
    assert resource.meta["_meta"]["ui"]["lifecycle"]["teardownEvent"] == "view-unload"


def test_ui_resource_loader_returns_html_document() -> None:
    resource = get_ui_resource_specs()[0]
    html = resource.loader()

    assert "<!doctype html>" in html.lower()
    assert "Calculations" in html
    assert "tool-call-request" in html
    assert "get_calculation_details" in html
    assert "safe-area-inset-top" in html or "--host-inset-top" in html


def test_ui_resource_specs_allow_env_based_csp_domain_extension(monkeypatch) -> None:
    monkeypatch.setenv("MCP_UI_CSP_CONNECT_DOMAINS", "https://api.example.com, https://mcp.example.com")
    monkeypatch.setenv("MCP_UI_CSP_RESOURCE_DOMAINS", "https://cdn.example.com")

    resource = get_ui_resource_specs()[0]
    csp_meta = resource.meta["_meta"]["ui"]["csp"]

    assert csp_meta["connectDomains"] == ["https://api.example.com", "https://mcp.example.com"]
    assert csp_meta["resourceDomains"] == ["https://cdn.example.com"]


def test_ui_loader_prefers_frontend_dist_when_available(tmp_path, monkeypatch) -> None:
    built_html = tmp_path / "index.html"
    built_html.write_text("<!doctype html><html><body>built-ui</body></html>", encoding="utf-8")
    monkeypatch.setattr(ui_resources, "FRONTEND_DIST_HTML", Path(built_html))

    resource = get_ui_resource_specs()[0]
    html = resource.loader()

    assert "built-ui" in html
