from abc import ABC


class StorageProgressLogger(ABC):
    pass

    def log_fetch_progress(self) -> None:
        pass

    def log_store_progress(self) -> None:
        pass
