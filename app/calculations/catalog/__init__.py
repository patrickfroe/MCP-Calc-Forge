from app.calculations.catalog.average import CALCULATION as AVERAGE
from app.calculations.catalog.break_even_units import CALCULATION as BREAK_EVEN_UNITS
from app.calculations.catalog.compound_interest import CALCULATION as COMPOUND_INTEREST
from app.calculations.catalog.currency_conversion_static import CALCULATION as CURRENCY_CONVERSION_STATIC
from app.calculations.catalog.discount_calculation import CALCULATION as DISCOUNT_CALCULATION
from app.calculations.catalog.gross_margin import CALCULATION as GROSS_MARGIN
from app.calculations.catalog.loan_annuity_payment import CALCULATION as LOAN_ANNUITY_PAYMENT
from app.calculations.catalog.markup_calculation import CALCULATION as MARKUP_CALCULATION
from app.calculations.catalog.percentage_change import CALCULATION as PERCENTAGE_CHANGE
from app.calculations.catalog.percentage_of_value import CALCULATION as PERCENTAGE_OF_VALUE
from app.calculations.catalog.rule_of_three import CALCULATION as RULE_OF_THREE
from app.calculations.catalog.simple_interest import CALCULATION as SIMPLE_INTEREST
from app.calculations.catalog.vat_calculation import CALCULATION as VAT_CALCULATION
from app.calculations.catalog.weighted_average import CALCULATION as WEIGHTED_AVERAGE

ALL_CALCULATIONS = (
    PERCENTAGE_OF_VALUE,
    VAT_CALCULATION,
    AVERAGE,
    RULE_OF_THREE,
    DISCOUNT_CALCULATION,
    PERCENTAGE_CHANGE,
    COMPOUND_INTEREST,
    SIMPLE_INTEREST,
    WEIGHTED_AVERAGE,
    GROSS_MARGIN,
    MARKUP_CALCULATION,
    BREAK_EVEN_UNITS,
    LOAN_ANNUITY_PAYMENT,
    CURRENCY_CONVERSION_STATIC,
)

__all__ = ["ALL_CALCULATIONS"]
