"""
Lab 6 - Code (line) coverage tests for phone_repair_quote.py
Name : Satyam Goyal
SRN  : PES1UG24CS424

Run:
    coverage run -m pytest CodeCoverageTest_phone_repair_quote.py
    coverage report -m
"""
import pytest
from phone_repair_quote import repair_quote, repair_days, trade_in_value


# ---------------------------------------------------------------- repair_quote
def test_budget_screen():
    assert repair_quote("screen", "budget", False, False) == 4600


def test_unknown_part_raises():
    with pytest.raises(ValueError, match="unknown part"):
        repair_quote("speaker", "budget", False, False)


def test_unknown_brand_tier_raises():
    with pytest.raises(ValueError, match="unknown brand tier"):
        repair_quote("screen", "midrange", False, False)


def test_flagship_battery_warranty_express():
    # cost 3000 waived by warranty, labour 300, express +500
    assert repair_quote("battery", "flagship", True, True) == 800


# ----------------------------------------------------------------- repair_days
def test_in_stock_quick():
    assert repair_days("battery", True, 2) == 1


def test_screen_out_of_stock_no_technician():
    # 3 (no technician) + 5 (screen out of stock)
    assert repair_days("screen", False, 0) == 8


def test_battery_out_of_stock_with_technician():
    # 1 + 2 (non screen/camera out of stock)
    assert repair_days("battery", False, 1) == 3


# -------------------------------------------------------------- trade_in_value
def test_trade_in_invalid_price_raises():
    with pytest.raises(ValueError, match="invalid input"):
        trade_in_value(0, 10, False)


def test_trade_in_too_old_is_zero():
    assert trade_in_value(10000, 60, False) == 0


def test_trade_in_new_cracked():
    # 60% of 10000 = 6000, halved for cracked screen
    assert trade_in_value(10000, 6, True) == 3000


def test_trade_in_mid_age():
    assert trade_in_value(10000, 18, False) == 4000


def test_trade_in_older():
    assert trade_in_value(10000, 30, False) == 2000
