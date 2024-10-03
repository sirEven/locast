from typing import List, Tuple

from locast.candle.candle import Candle
from locast.candle.exchange import Exchange
from locast.candle.resolution import ResolutionDetail


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


def log_integrity_violations(
    emoji: str,
    exchange: Exchange,
    market: str,
    resolution: ResolutionDetail,
    violations: List[Tuple[Candle, Candle]],
) -> None:
    n = len(violations)
    v = "integrity violations" if n > 1 else "integrity violation"
    detail = f"{market}, {resolution.notation}"
    print(f"{emoji} Attention: {exchange.name} delivered {n} {v} for {detail} {emoji}")
    for v in violations:
        print(f"    ❌ {v[0].started_at} - {v[1].started_at}")


def log_redundant_call(emoji: str, message: str) -> None:
    print(f"{emoji} {message}")
