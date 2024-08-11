from datetime import datetime


def datetime_to_dydx_iso_str(date: datetime) -> str:
        return date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")