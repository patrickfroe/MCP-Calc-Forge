from __future__ import annotations

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
    assert "<main>" in html.lower()
    assert "tool-result" in html
    assert "tool-call-request" in html
    assert 'const BRIDGE_VERSION = "1.0";' in html
    assert "mcpUi.type" in html
    assert "parseIncomingMessage" in html
    assert "get_calculation_details" in html
    assert "event.source !== window.parent" in html
    assert "event.origin !== parentOrigin" in html
