import re

KE_PHONE = re.compile(r"^(?:\+?254|0)(7\d{8}|1\d{8})$")
KRA_PIN = re.compile(r"^[A-Z]\d{9}[A-Z]$")


def normalize_phone(p: str) -> str | None:
    if not p:
        return None
    p = p.strip().replace(" ", "").replace("-", "")
    m = KE_PHONE.match(p)
    if not m:
        return None
    return f"254{m.group(1)}"


def is_valid_kra_pin(pin: str) -> bool:
    return bool(pin and KRA_PIN.match(pin.strip().upper()))


def parse_amount(raw) -> float | None:
    try:
        v = float(str(raw).replace(",", "").strip())
        return v if v > 0 else None
    except (TypeError, ValueError):
        return None