from app.calculations.catalog.percentage_of import CALCULATION as PERCENTAGE_OF
from app.calculations.catalog.simple_interest import CALCULATION as SIMPLE_INTEREST
from app.calculations.catalog.vat_add import CALCULATION as VAT_ADD

ALL_CALCULATIONS = (PERCENTAGE_OF, VAT_ADD, SIMPLE_INTEREST)

__all__ = ["ALL_CALCULATIONS"]
