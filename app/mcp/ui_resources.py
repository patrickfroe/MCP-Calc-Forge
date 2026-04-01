from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from fastmcp import FastMCP

UI_ASSETS_DIR = Path(__file__).resolve().parent / "ui"

UIResourceLoader = Callable[[], str]


@dataclass(frozen=True)
class MCPUIResourceSpec:
    uri: str
    name: str
    description: str
    mime_type: str
    loader: UIResourceLoader
    meta: dict[str, object] = field(default_factory=dict)


def _read_ui_file(filename: str) -> str:
    return (UI_ASSETS_DIR / filename).read_text(encoding="utf-8")


def _restrictive_default_csp_meta() -> dict[str, object]:
    return {
        "_meta": {
            "ui": {
                "bridge": {
                    "version": "1.0",
                    "incomingMessageTypes": ["tool-result"],
                    "outgoingMessageTypes": ["tool-call-request"],
                    "supportsLegacyTopLevelType": True,
                },
                "csp": {
                    "connectDomains": [],
                    "resourceDomains": [],
                },
                "displayModes": ["inline", "fullscreen"],
                "theming": {"supportsHostTheme": True},
                "hostContext": {"acceptsLocale": True, "acceptsTimezone": True},
                "lifecycle": {
                    "initEvent": "tool-result",
                    "updateEvent": "tool-result",
                    "teardownEvent": "view-unload",
                },
            }
        }
    }


def get_ui_resource_specs() -> tuple[MCPUIResourceSpec, ...]:
    return (
        MCPUIResourceSpec(
            uri="ui://calculations/list",
            name="calculations_list_view",
            description="UI scaffold for listing available calculations.",
            mime_type="text/html",
            loader=lambda: _read_ui_file("list_calculations.html"),
            meta=_restrictive_default_csp_meta(),
        ),
    )


def register_ui_resources(mcp: FastMCP) -> None:
    for spec in get_ui_resource_specs():
        mcp.resource(
            spec.uri,
            name=spec.name,
            description=spec.description,
            mime_type=spec.mime_type,
            meta=spec.meta or None,
        )(spec.loader)
