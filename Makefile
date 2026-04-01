.PHONY: ui-install ui-build ui-verify test-ui-flow

ui-install:
	cd frontend && npm install

ui-build:
	cd frontend && npm run build

ui-verify:
	test -f frontend/dist/src/index.html

test-ui-flow:
	PYTHONPATH=. pytest -q \
		tests/integration/test_mcp_tools_integration.py::test_list_calculations_and_get_details_end_to_end \
		tests/unit/test_mcp_ui_resources.py::test_ui_resource_loader_returns_html_document \
		tests/unit/test_mcp_discovery.py::test_mcp_ui_flow_initialize_tool_call_and_resource_read_is_consistent
