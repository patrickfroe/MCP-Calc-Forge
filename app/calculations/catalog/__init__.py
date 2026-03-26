from app.calculations.catalog.average import CALCULATION as AVERAGE
from app.calculations.catalog.percentage_of_value import CALCULATION as PERCENTAGE_OF_VALUE
from app.calculations.catalog.rule_of_three import CALCULATION as RULE_OF_THREE
from app.calculations.catalog.vat_calculation import CALCULATION as VAT_CALCULATION

ALL_CALCULATIONS = (PERCENTAGE_OF_VALUE, VAT_CALCULATION, AVERAGE, RULE_OF_THREE)

__all__ = ["ALL_CALCULATIONS"]
