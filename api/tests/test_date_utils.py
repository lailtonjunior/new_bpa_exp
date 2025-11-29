from datetime import date
from pathlib import Path
import sys
import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from api.date_utils import last_full_month, last_n_days, last_n_months, resolve_or_default


def test_resolve_or_default_accepts_defaults():
    start, end = resolve_or_default(None, None, date(2024, 1, 1), date(2024, 1, 31))
    assert start == date(2024, 1, 1)
    assert end == date(2024, 1, 31)


def test_resolve_or_default_rejects_inverted_dates():
    with pytest.raises(ValueError):
        resolve_or_default(date(2024, 2, 1), date(2024, 1, 31), date(2024, 1, 1), date(2024, 1, 31))


def test_last_full_month_bounds():
    start, end = last_full_month()
    assert start.day == 1
    assert end >= start


def test_last_n_helpers():
    start, end = last_n_days(7)
    assert (end - start).days == 7
    start_m, end_m = last_n_months(12)
    assert end_m >= start_m
