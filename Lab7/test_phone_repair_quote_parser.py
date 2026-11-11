"""
Lab 7 - Fuzz tests (Hypothesis) for phone_repair_quote_parser.py
Name : Satyam Goyal
SRN  : PES1UG24CS424

Run:
    pytest test_phone_repair_quote_parser.py
    python -m pytest test_phone_repair_quote_parser.py
"""
import string

from hypothesis import given, strategies as st
from phone_repair_quote_parser import mask_imei, parse_parts_order, parse_model


# ---------------------------------------------------------------------------
# Part 1: required "must not crash" fuzz tests (one per function)
# ---------------------------------------------------------------------------
@given(st.text() | st.none())
def test_mask_imei_no_crash(s):
    try:
        mask_imei(s)
    except Exception as e:
        assert False, f"mask_imei crashed with: {e!r}"


@given(st.text() | st.none())
def test_parse_parts_order_no_crash(s):
    try:
        parse_parts_order(s)
    except Exception as e:
        assert False, f"parse_parts_order crashed with: {e!r}"


@given(st.text() | st.none())
def test_parse_model_no_crash(s):
    try:
        parse_model(s)
    except Exception as e:
        assert False, f"parse_model crashed with: {e!r}"


# ---------------------------------------------------------------------------
# Part 2: no crash for values of any type, not only str and None
# ---------------------------------------------------------------------------
any_value = st.one_of(
    st.none(),
    st.booleans(),
    st.integers(),
    st.floats(),
    st.binary(),
    st.text(),
    st.lists(st.integers()),
    st.dictionaries(st.text(), st.integers()),
)


@given(any_value)
def test_no_function_crashes_on_any_type(x):
    for fn in (mask_imei, parse_parts_order, parse_model):
        try:
            fn(x)
        except Exception as e:
            assert False, f"{fn.__name__} crashed on {x!r} with: {e!r}"


# ---------------------------------------------------------------------------
# Part 3: correctness properties (the output must also make sense)
# ---------------------------------------------------------------------------
@given(st.text())
def test_mask_imei_only_reveals_last_four(s):
    cleaned = s.replace("-", "").replace(" ", "")
    result = mask_imei(s)
    assert isinstance(result, str)
    assert len(result) == len(cleaned)
    if len(cleaned) > 4:
        assert result == "*" * (len(cleaned) - 4) + cleaned[-4:]
    else:
        # nothing may be revealed when there are four or fewer digits
        assert result == "*" * len(cleaned)


@given(st.one_of(st.none(), st.integers(), st.binary()))
def test_mask_imei_non_string_gives_empty_string(x):
    assert mask_imei(x) == ""


@given(st.text() | st.none())
def test_parse_parts_order_returns_clean_dict(s):
    result = parse_parts_order(s)
    assert isinstance(result, dict)
    for part, qty in result.items():
        assert isinstance(part, str) and part == part.strip() and part != ""
        assert isinstance(qty, int) and qty >= 1


part_names = (
    st.text(alphabet=string.ascii_letters + " ", min_size=1, max_size=15)
    .map(str.strip)
    .filter(bool)
)


@given(st.dictionaries(part_names, st.integers(min_value=1, max_value=10**6), min_size=1, max_size=6))
def test_parse_parts_order_round_trip(order):
    text = "; ".join(f"{part} x{qty}" for part, qty in order.items())
    assert parse_parts_order(text) == order


@given(st.text() | st.none())
def test_parse_model_returns_pair_of_strings(s):
    result = parse_model(s)
    assert isinstance(result, tuple) and len(result) == 2
    assert all(isinstance(piece, str) for piece in result)


# ---------------------------------------------------------------------------
# Part 4: regression tests for the kinds of input the fuzzer found
# ---------------------------------------------------------------------------
def test_normal_inputs_still_work():
    assert mask_imei("35-209900-176148-1") == "*" * 11 + "1481"
    assert parse_parts_order("screen x1; battery x2") == {"screen": 1, "battery": 2}
    assert parse_model("samsung Galaxy S23") == ("Samsung", "Galaxy S23")


def test_short_imei_is_fully_masked():
    assert mask_imei("123") == "***"


def test_empty_and_none_inputs():
    assert mask_imei("") == ""
    assert mask_imei(None) == ""
    assert parse_parts_order("") == {}
    assert parse_parts_order(None) == {}
    assert parse_model("") == ("", "")
    assert parse_model(None) == ("", "")


def test_part_names_containing_x():
    assert parse_parts_order("toolbox x3; xenon lamp x1") == {"toolbox": 3, "xenon lamp": 1}


def test_malformed_items_are_skipped_not_fatal():
    assert parse_parts_order("screen x1;; battery; camera xabc; x2; charger x-1") == {"screen": 1}


def test_duplicate_parts_are_added_together():
    assert parse_parts_order("screen x1; screen x2") == {"screen": 3}


def test_single_word_model():
    assert parse_model("samsung") == ("Samsung", "")


def test_model_split_on_any_whitespace():
    assert parse_model("apple\tiPhone 15") == ("Apple", "iPhone 15")
