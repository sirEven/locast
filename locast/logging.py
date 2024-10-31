from datetime import datetime
from typing import List

from locast.candle.exchange import Exchange
from locast.candle.exchange_resolution import ResolutionDetail


def log_progress(
    emoji: str,
    group_name: str,
    past_tense: str,
    amount_done: int,
    total: int,
) -> None:
    progress_message = f"{amount_done} of {total} {group_name} {past_tense}."
    if amount_done == total:
        print(f"\r{emoji} {progress_message} ✅", end="\n", flush=True)
    else:
        print(f"{emoji} {progress_message}", end="\r", flush=True)


def log_missing_candles(
    emoji: str,
    exchange: Exchange,
    market: str,
    resolution: ResolutionDetail,
    missing_candle_dates: List[datetime],
) -> None:
    n = len(missing_candle_dates)
    candles = "candles" if n > 1 else "candle"
    detail = f"{market}, {resolution.notation}"
    print(
        f"{emoji} Attention: {exchange.name} failed to deliver {n} {candles} for {detail} {emoji}"
    )
    for date in missing_candle_dates:
        print(f"    ❌ Candle missing: {date}.")


def log_redundant_call(emoji: str, message: str) -> None:
    print(f"{emoji} {message}")
