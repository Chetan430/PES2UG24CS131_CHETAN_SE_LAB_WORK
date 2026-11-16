"""Robust event-ticket input processors."""
import csv
import io
import math
import re


def decode_promo_voucher(voucher_code):
    """Accept PREFIX-0..100, returning a message instead of raising on bad input."""
    if not isinstance(voucher_code, str):
        return "Invalid voucher"
    match = re.fullmatch(r"\s*([A-Za-z][A-Za-z0-9_]*)-([0-9]{1,3})\s*", voucher_code)
    if not match:
        return "Invalid voucher"
    percentage = int(match.group(2))
    if percentage > 100:
        return "Invalid voucher"
    return f"Valid {match.group(1).upper()}: {percentage}% OFF"


def calculate_seat_tier_price(tier_spec):
    """Price supported tiers and positive row numbers; return None for bad input."""
    if not isinstance(tier_spec, str):
        return None
    match = re.fullmatch(r"\s*(VIP|PREMIUM|GENERAL)\s*@\s*([0-9]+)\s*", tier_spec, re.IGNORECASE)
    if not match:
        return None
    row = int(match.group(2)) if len(match.group(2)) < 1000 else 0
    if not 1 <= row <= 10000:
        return None
    rates = {"VIP": 150.0, "PREMIUM": 90.0, "GENERAL": 45.0}
    return rates[match.group(1).upper()] + row * 2.0


def parse_attendee_badge(badge_csv):
    """Parse three CSV fields, with age 0..120 and a nonempty name and seat."""
    if not isinstance(badge_csv, str):
        return "Invalid badge"
    try:
        tokens = next(csv.reader(io.StringIO(badge_csv, newline=""), strict=True))
    except (csv.Error, StopIteration, ValueError):
        return "Invalid badge"
    if len(tokens) != 3:
        return "Invalid badge"
    name, age_text, seat = (token.strip() for token in tokens)
    if not name or not seat or not re.fullmatch(r"[0-9]{1,3}", age_text):
        return "Invalid badge"
    age = int(age_text)
    if age > 120:
        return "Invalid badge"
    category = "Child" if age < 18 else "Adult"
    return f"{name} [{category}] - Seat {seat}"


def main():
    print("==== Running decode_promo_voucher ====")
    print("Voucher:", decode_promo_voucher(input("Enter voucher (e.g. EARLY-20): ")))
    print("\n==== Running calculate_seat_tier_price ====")
    print("Seat Price: $", calculate_seat_tier_price(input("Enter tier spec (e.g. VIP@4): ")))
    print("\n==== Running parse_attendee_badge ====")
    print("Badge:", parse_attendee_badge(input("Enter badge CSV (Name,Age,Seat): ")))


if __name__ == "__main__":
    main()
