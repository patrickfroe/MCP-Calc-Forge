import calcforge.calculators as calculators


def test_list_calculators_with_category_filter() -> None:
    arithmetic_only = calculators.list_calculators(category="arithmetic")

    assert arithmetic_only
    assert all(entry["category"] == "arithmetic" for entry in arithmetic_only)


def test_calculate_returns_result_and_prefilled_url() -> None:
    payload = calculators.calculate("add", {"a": 2, "b": 5})

    assert payload["result"] == 7
    assert payload["prefilled_url"].startswith("https://calcforge.app/calculator?")
    assert "calculator=add" in payload["prefilled_url"]


def test_calculate_cas_numeric_and_handoff() -> None:
    response = calculators.calculate_cas(["2+3", "x+1"])

    assert response["mode"] == "headless_numeric"
    assert response["results"][0]["status"] == "ok"
    assert response["results"][0]["result"].startswith("5")
    assert response["results"][1]["status"] == "handoff"
    assert response["results"][1]["handoff_url"].startswith("https://calcforge.app/cas?")


def test_calculate_cas_headless_alias() -> None:
    assert calculators.calculate_cas_headless(["3*3"]) == calculators.calculate_cas(["3*3"])
