"""
Lab 6 - Branch coverage tests for phone_repair_quote.py
Name : Satyam Goyal
SRN  : PES1UG24CS424

Every decision in the module is exercised for both its True and False outcome,
plus boundary values (12/13, 24/25, 48/49 months) and the 'or' conditions.

Run:
    coverage run --branch -m pytest BranchCoverageTest_phone_repair_quote.py
    coverage report -m
"""
import pytest
from phone_repair_quote import repair_quote, repair_days, trade_in_value


# ---------------------------------------------------------------- repair_quote
class TestRepairQuoteValidation:
    def test_unknown_part_raises(self):
        with pytest.raises(ValueError, match="unknown part"):
            repair_quote("speaker", "budget", False, False)

    def test_unknown_brand_tier_raises(self):
        with pytest.raises(ValueError, match="unknown brand tier"):
            repair_quote("screen", "midrange", False, False)

    def test_valid_part_is_checked_before_tier(self):
        # both invalid: the part check comes first
        with pytest.raises(ValueError, match="unknown part"):
            repair_quote("speaker", "midrange", False, False)


@pytest.mark.parametrize(
    "part, tier, warranty, express, expected",
    [
        # budget / flagship branch
        ("screen", "budget", False, False, 4600),
        ("screen", "flagship", False, False, 8600),
        # screen / non-screen labour branch
        ("battery", "budget", False, False, 1800),
        ("camera", "budget", False, False, 2800),
        ("charging_port", "flagship", False, False, 1900),
        # warranty branch: waives part cost for non-screen parts only
        ("battery", "budget", True, False, 300),
        ("camera", "flagship", True, False, 300),
        ("screen", "budget", True, False, 4600),      # screen never waived
        ("screen", "flagship", True, True, 9100),     # waiver skipped + express
        # express branch
        ("battery", "flagship", False, True, 3800),
        ("charging_port", "budget", True, True, 800),
    ],
)
def test_repair_quote_combinations(part, tier, warranty, express, expected):
    assert repair_quote(part, tier, warranty, express) == expected


# ----------------------------------------------------------------- repair_days
@pytest.mark.parametrize(
    "part, in_stock, techs, expected",
    [
        # technicians_free == 0 (True) vs > 0 (False)
        ("battery", True, 0, 3),
        ("battery", True, 1, 1),
        ("battery", True, 5, 1),
        # in stock: restock branch skipped entirely
        ("screen", True, 0, 3),
        ("camera", True, 2, 1),
        # out of stock: screen / camera -> +5
        ("screen", False, 2, 6),
        ("camera", False, 2, 6),
        ("screen", False, 0, 8),
        ("camera", False, 0, 8),
        # out of stock: any other part -> +2
        ("battery", False, 2, 3),
        ("charging_port", False, 2, 3),
        ("charging_port", False, 0, 5),
    ],
)
def test_repair_days(part, in_stock, techs, expected):
    assert repair_days(part, in_stock, techs) == expected


# -------------------------------------------------------------- trade_in_value
class TestTradeInValidation:
    def test_zero_price_raises(self):
        with pytest.raises(ValueError, match="invalid input"):
            trade_in_value(0, 10, False)

    def test_negative_price_raises(self):
        with pytest.raises(ValueError, match="invalid input"):
            trade_in_value(-500, 10, False)

    def test_negative_age_raises(self):
        with pytest.raises(ValueError, match="invalid input"):
            trade_in_value(10000, -1, False)

    def test_age_zero_is_valid(self):
        assert trade_in_value(10000, 0, False) == 6000


@pytest.mark.parametrize(
    "price, age, cracked, expected",
    [
        # age band 1: <= 12 months -> 60%
        (10000, 6, False, 6000),
        (10000, 12, False, 6000),      # upper boundary
        # age band 2: 13..24 months -> 40%
        (10000, 13, False, 4000),      # lower boundary
        (10000, 24, False, 4000),      # upper boundary
        # age band 3: 25..48 months -> 20%
        (10000, 25, False, 2000),      # lower boundary
        (10000, 48, False, 2000),      # upper boundary (not rejected)
        # older than 48 months -> worth nothing, cracked flag irrelevant
        (10000, 49, False, 0),
        (10000, 49, True, 0),
        # cracked screen halves the value in every band
        (10000, 12, True, 3000),
        (10000, 24, True, 2000),
        (10000, 48, True, 1000),
        # integer division behaviour
        (999, 5, False, 599),
        (999, 5, True, 299),
    ],
)
def test_trade_in_value(price, age, cracked, expected):
    assert trade_in_value(price, age, cracked) == expected
