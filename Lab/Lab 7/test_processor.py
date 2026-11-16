"""Hypothesis property-based regression tests for the three ticket processors."""
from hypothesis import given, example, settings, strategies as st
from processor import decode_promo_voucher, calculate_seat_tier_price, parse_attendee_badge


@settings(max_examples=150)
@example(None)
@example("")
@example("EARLY-101")
@given(st.text() | st.none())
def test_decode_promo_voucher_no_crash(s):
    try:
        result = decode_promo_voucher(s)
    except Exception as exc:
        assert False, f"decode_promo_voucher crashed for {s!r}: {exc!r}"
    assert isinstance(result, str)


@settings(max_examples=150)
@example(None)
@example("VIP@0")
@example("UNKNOWN@4")
@given(st.text() | st.none())
def test_calculate_seat_tier_price_safe(s):
    try:
        result = calculate_seat_tier_price(s)
    except Exception as exc:
        assert False, f"calculate_seat_tier_price crashed for {s!r}: {exc!r}"
    assert result is None or (isinstance(result, float) and result >= 0)


@settings(max_examples=150)
@example(None)
@example("Alice,not-a-number,A1")
@example("Alice,20")
@given(st.text() | st.none())
def test_parse_attendee_badge_safe(s):
    try:
        result = parse_attendee_badge(s)
    except Exception as exc:
        assert False, f"parse_attendee_badge crashed for {s!r}: {exc!r}"
    assert isinstance(result, str)


@given(st.sampled_from(["VIP", "PREMIUM", "GENERAL"]), st.integers(min_value=1, max_value=10000))
def test_valid_seat_price(tier, row):
    expected = {"VIP": 150.0, "PREMIUM": 90.0, "GENERAL": 45.0}[tier] + row * 2.0
    assert calculate_seat_tier_price(f"{tier}@{row}") == expected


@given(st.integers(min_value=0, max_value=100))
def test_valid_voucher_percentage(pct):
    assert decode_promo_voucher(f"EARLY-{pct}") == f"Valid EARLY: {pct}% OFF"


@given(st.integers(min_value=0, max_value=120))
def test_valid_attendee_age(age):
    category = "Child" if age < 18 else "Adult"
    assert parse_attendee_badge(f"Alex,{age},A1") == f"Alex [{category}] - Seat A1"
