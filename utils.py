"""Validation and formatting helpers."""

import re
from datetime import datetime


_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_DIGITS_ONLY = re.compile(r"^\d+$")


def is_valid_email(value: str) -> bool:
    if not value:
        return False
    return bool(_EMAIL_PATTERN.match(value))


def is_digits_only(value: str) -> bool:
    if not value:
        return False
    return bool(_DIGITS_ONLY.match(value))


def luhn_check(card_number: str) -> bool:
    if not is_digits_only(card_number):
        return False

    total = 0
    reverse_digits = card_number[::-1]
    for index, digit_char in enumerate(reverse_digits):
        digit = int(digit_char)
        if index % 2 == 1:
            digit *= 2
            if digit > 9:
                digit -= 9
        total += digit
    return total % 10 == 0


def is_expiry_valid(month: int, year: int) -> bool:
    if month < 1 or month > 12:
        return False
    today = datetime.utcnow()
    if year < today.year:
        return False
    if year == today.year and month < today.month:
        return False
    return True


def format_cents_as_currency(amount_cents: int, currency: str = "USD") -> str:
    major = amount_cents // 100
    minor = amount_cents % 100
    return f"{currency} {major}.{minor:02d}"


def mask_card_number(card_number: str) -> str:
    if not card_number or len(card_number) < 4:
        return "****"
    return "*" * (len(card_number) - 4) + card_number[-4:]
