from datetime import date
from dateutil.relativedelta import relativedelta
from typing import Optional, Tuple


def resolve_or_default(
    data_inicio: Optional[date],
    data_fim: Optional[date],
    default_inicio: date,
    default_fim: date,
) -> Tuple[date, date]:
    """
    Ensure we always return a valid period. If provided dates are None, falls back.
    Raises ValueError when start is after end.
    """
    inicio = data_inicio or default_inicio
    fim = data_fim or default_fim
    if inicio > fim:
        raise ValueError("data_inicio cannot be after data_fim")
    return inicio, fim


def last_full_month() -> Tuple[date, date]:
    """
    Return first and last day of the previous calendar month.
    """
    today = date.today()
    first_current = today.replace(day=1)
    last_previous = first_current - relativedelta(days=1)
    first_previous = last_previous.replace(day=1)
    return first_previous, last_previous


def last_n_months(n: int) -> Tuple[date, date]:
    """
    Return range covering the last n months inclusive ending today.
    """
    end = date.today()
    start = end - relativedelta(months=n)
    return start, end


def last_n_days(n: int) -> Tuple[date, date]:
    end = date.today()
    start = end - relativedelta(days=n)
    return start, end
