"""Exact DNS plans and guarded single-record changes."""
import hashlib
import ipaddress
import json
import re

from .api import CloudflareError, ID

TYPES = ("A", "AAAA", "CNAME", "TXT", "MX", "NS")
FIELDS = ("id", "type", "name", "content", "ttl", "proxied", "priority",
          "comment", "tags", "settings", "modified_on")


def fqdn(name, zone):
    zone = zone.rstrip(".").lower()
    name = name.strip().rstrip(".").lower()
    if name == "@":
        name = zone
    elif "." not in name:
        name += "." + zone
    if name != zone and not name.endswith("." + zone):
        raise CloudflareError("Record name must belong to the selected zone; use its full name.")
    if len(name) > 253 or any(
        not label or len(label) > 63 or not re.fullmatch(r"[a-z0-9_*][a-z0-9_*-]*", label)
        or label.endswith("-") or ("*" in label and (label != "*" or i != 0))
        for i, label in enumerate(name.split("."))
    ):
        raise CloudflareError("Invalid DNS name; use ASCII or punycode labels.")
    return name


def snapshot(record):
    return {k: record[k] for k in FIELDS if k in record}


def digest(plan):
    return hashlib.sha256(json.dumps(
        {k: v for k, v in plan.items() if k != "sha256"},
        sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode()).hexdigest()


def make_plan(client, *, zone, name, kind, content=None, ttl=None, proxied=None,
              priority=None, record_id=None, delete=False):
    meta = client.zone(zone)
    zid, zname = meta["id"], meta["name"]
    name = fqdn(name, zname)
    if kind not in TYPES:
        raise CloudflareError("Unsupported record type.")
    records = client.paged(f"/zones/{zid}/dns_records", {"name": name, "type": kind})
    matches = [r for r in records if r.get("name", "").lower().rstrip(".") == name
               and r.get("type") == kind]
    if record_id:
        if not re.fullmatch(ID, record_id):
            raise CloudflareError("Invalid record ID.")
        matches = [r for r in matches if r["id"] == record_id]
        if len(matches) != 1:
            raise CloudflareError("The record ID does not match this zone, name and type.")
    if delete and not record_id:
        raise CloudflareError("Deletion requires --record-id from a reviewed inventory.")
    if len(matches) > 1:
        raise CloudflareError("Multiple records match; select --record-id explicitly.")
    before = snapshot(matches[0]) if matches else None
    payload = None
    if not delete:
        if not isinstance(content, str) or not content or len(content) > 65536:
            raise CloudflareError("Supply nonempty record content within 65536 characters.")
        if kind in {"A", "AAAA"}:
            try:
                ip = ipaddress.ip_address(content)
            except ValueError:
                raise CloudflareError("Invalid IP address.") from None
            if ip.version != (4 if kind == "A" else 6):
                raise CloudflareError("IP version does not match record type.")
            content = str(ip)
        if kind in {"CNAME", "NS", "MX"}:
            content = content.rstrip(".").lower()
            if len(content) > 253 or not all(
                re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?", part)
                for part in content.split(".")
            ):
                raise CloudflareError("Record target must be an ASCII hostname.")
        if ttl is not None and (type(ttl) is not int or ttl != 1 and not 60 <= ttl <= 86400):
            raise CloudflareError("TTL must be 1 (automatic) or 60 through 86400.")
        if priority is not None and (kind != "MX" or not 0 <= priority <= 65535):
            raise CloudflareError("Priority is valid only for MX, from 0 through 65535.")
        if proxied is not None and kind not in {"A", "AAAA", "CNAME"}:
            raise CloudflareError("Proxy setting only applies to A, AAAA and CNAME.")
        payload = {"type": kind, "name": name, "content": content}
        # Omitted options preserve existing settings; defaults only on creation.
        if ttl is not None or before is None:
            payload["ttl"] = ttl if ttl is not None else 1
        if kind in {"A", "AAAA", "CNAME"} and (proxied is not None or before is None):
            payload["proxied"] = proxied if proxied is not None else False
        effective_proxy = payload.get("proxied", (before or {}).get("proxied", False))
        if effective_proxy and payload.get("ttl", (before or {}).get("ttl", 1)) != 1:
            raise CloudflareError("Proxied records require automatic TTL; use --ttl 1.")
        if kind == "MX" and (priority is not None or before is None):
            if priority is None:
                raise CloudflareError("New MX records require --priority.")
            payload["priority"] = priority
    plan = {
        "schema": 1, "zone": zname, "zone_id": zid, "name": name, "type": kind,
        "action": "delete" if delete else ("update" if before else "create"),
        "before": before, "payload": payload,
    }
    if before and not delete and all(before.get(k) == v for k, v in payload.items()):
        plan["action"] = "noop"
    plan["sha256"] = digest(plan)
    return plan


def apply_plan(client, plan, *, confirm_zone, confirm_plan):
    if confirm_zone != plan["zone"] or confirm_plan != digest(plan):
        raise CloudflareError("Confirmation must match the exact zone and current preview SHA-256.")
    base = f'/zones/{plan["zone_id"]}/dns_records'
    before, action = plan["before"], plan["action"]
    if action == "noop":
        return {"mode": "noop", "plan": plan, "verified": True}
    if before:
        path = base + "/" + before["id"]
        current = client.request("GET", path)["result"]
        if snapshot(current) != before:
            raise CloudflareError("Record changed since preview; create and review a fresh plan.")
    else:
        path = base
        existing = client.paged(base, {"name": plan["name"], "type": plan["type"]})
        if existing:
            raise CloudflareError("A record appeared since preview; create a fresh plan.")
    response = client.request(
        {"create": "POST", "update": "PATCH", "delete": "DELETE"}[action],
        path, plan["payload"],
    )["result"]
    if not isinstance(response, dict) or not re.fullmatch(ID, str(response.get("id", ""))):
        raise CloudflareError("Write sent but result ID invalid. Inspect remote state; do not retry blindly.")
    rid = response["id"]
    if before and rid != before["id"]:
        raise CloudflareError("Write result ID mismatch. Inspect remote state.")
    if action == "delete":
        remaining = client.paged(base, {"name": plan["name"], "type": plan["type"]})
        verified = not any(r["id"] == rid for r in remaining)
    else:
        current = client.request("GET", base + "/" + rid)["result"]
        # Preserve the settings that the user did not ask to change.
        expected = {k: v for k, v in (before or {}).items()
                    if k not in {"id", "modified_on"}}
        expected.update(plan["payload"])
        verified = isinstance(current, dict) and all(current.get(k) == v for k, v in expected.items())
    if not verified:
        raise CloudflareError("Write sent but readback differs. Inspect remote state; no automatic rollback.")
    return {"mode": "applied", "plan": plan, "record_id": rid, "verified": True}
