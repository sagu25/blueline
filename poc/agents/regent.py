"""
REGENT — Certificate Inventory Manager
Production: reads/writes Azure Table Storage.
POC: in-memory sample inventory representing what Key Vault + Table Storage would hold.
"""

from datetime import datetime, timezone

_INVENTORY = [
    {
        "name":               "payments.external.com",
        "subject":            "payments.external.com",
        "expiry_date":        "2026-04-25",
        "environments":       ["Production"],
        "ca_type":            "DigiCert",
        "owner":              "Manjunath Rao",
        "last_renewed":       "2025-04-25",
        "deployment_targets": ["Azure App Service — payments-api-prod"],
    },
    {
        "name":               "api.core-main.internal",
        "subject":            "api.core-main.internal",
        "expiry_date":        "2026-05-07",
        "environments":       ["Dev", "QA", "Production"],
        "ca_type":            "Internal PKI (C&M Portal)",
        "owner":              "Pankaj Pathak",
        "last_renewed":       "2025-05-07",
        "deployment_targets": ["IIS — WEBSVR01", "IIS — WEBSVR02"],
    },
    {
        "name":               "admin.core-main.internal",
        "subject":            "admin.core-main.internal",
        "expiry_date":        "2026-07-20",
        "environments":       ["Dev", "QA", "Production"],
        "ca_type":            "Internal PKI (C&M Portal)",
        "owner":              "Ravi Kumar",
        "last_renewed":       "2025-07-20",
        "deployment_targets": ["IIS — ADMINSVR01"],
    },
    {
        "name":               "*.internal.local",
        "subject":            "*.internal.local (wildcard)",
        "expiry_date":        "2026-10-15",
        "environments":       ["Dev", "QA"],
        "ca_type":            "Internal PKI (C&M Portal)",
        "owner":              "Pankaj Pathak",
        "last_renewed":       "2025-10-15",
        "deployment_targets": ["Multiple IIS servers"],
    },
]


def _days_remaining(expiry_date: str) -> int:
    expiry = datetime.strptime(expiry_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    return (expiry - datetime.now(timezone.utc)).days


def _status(days: int) -> str:
    if days < 0:    return "EXPIRED"
    if days <= 7:   return "CRITICAL"
    if days <= 14:  return "URGENT"
    if days <= 30:  return "RENEWAL_NEEDED"
    if days <= 90:  return "MONITOR"
    return "OK"


def get_inventory() -> list[dict]:
    enriched = []
    for cert in _INVENTORY:
        days = _days_remaining(cert["expiry_date"])
        enriched.append({**cert, "days_remaining": days, "status": _status(days)})
    return sorted(enriched, key=lambda c: c["days_remaining"])


def get_cert_by_name(name: str) -> dict | None:
    for cert in get_inventory():
        if cert["name"] == name:
            return cert
    return None
