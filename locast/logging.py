def log_progress(
    emoji: str,
    group_name: str,
    past_tence: str,
    amount_done: int,
    total: int,
) -> None:
    progress_message = f"{amount_done} of {total} {group_name} {past_tence}."
    if amount_done == total:
        print(f"\r{emoji} {progress_message} ✅", end="\n", flush=True)
    else:
        print(f"{emoji} {progress_message}", end="\r", flush=True)


def log_redundant_call(emoji: str, message: str) -> None:
    print(f"{emoji} {message}")
