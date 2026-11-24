from datetime import datetime


def kes(v) -> str:
    try:
        return f"KES {float(v):,.2f}"
    except (TypeError, ValueError):
        return "KES 0.00"


def dt(v: datetime | None, fmt="%Y-%m-%d %H:%M") -> str:
    return v.strftime(fmt) if v else "—"