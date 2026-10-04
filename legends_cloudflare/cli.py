"""JSON CLI with offline doctor and preview-first DNS changes."""
import argparse
import json
import sys
from datetime import datetime, timezone

from . import __version__
from .api import Client, CloudflareError
from .dns import TYPES, apply_plan, make_plan, snapshot


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--version", action="version", version=__version__)
    sub = p.add_subparsers(dest="command", required=True)
    doctor = sub.add_parser("doctor", help="Offline runtime check; --live checks zone access.")
    doctor.add_argument("--live", action="store_true")
    sub.add_parser("zones", help="List all accessible zones.")
    ns = sub.add_parser("nameservers", help="Get the selected zone's assigned nameservers.")
    ns.add_argument("--zone", required=True)
    records = sub.add_parser("records", help="List zone DNS records. Output may contain sensitive content.")
    records.add_argument("--zone", required=True)
    records.add_argument("--name")
    records.add_argument("--type", choices=TYPES)
    for command in ("upsert", "delete"):
        op = sub.add_parser(command, help="Preview a DNS change; explicit confirmation required to apply.")
        op.add_argument("--zone", required=True)
        op.add_argument("--name", required=True)
        op.add_argument("--type", required=True, choices=TYPES)
        op.add_argument("--record-id", required=command == "delete")
        if command == "upsert":
            op.add_argument("--content", required=True)
            op.add_argument("--ttl", type=int)
            op.add_argument("--priority", type=int)
            proxy = op.add_mutually_exclusive_group()
            proxy.add_argument("--proxied", dest="proxied", action="store_true")
            proxy.add_argument("--dns-only", dest="proxied", action="store_false")
            op.set_defaults(proxied=None)
        op.add_argument("--apply", action="store_true")
        op.add_argument("--confirm-zone")
        op.add_argument("--confirm-plan", help="SHA-256 from the reviewed preview.")
    return p


def execute(args, client_factory=Client):
    if args.command == "doctor" and not args.live:
        return {"module": "legends-cloudflare", "version": __version__,
                "ok": True, "mode": "offline", "live_access": "not_checked"}
    if args.command in {"upsert", "delete"}:
        confirmations = bool(args.confirm_zone or args.confirm_plan)
        if args.apply and not (args.confirm_zone and args.confirm_plan):
            raise CloudflareError("--apply requires --confirm-zone and --confirm-plan.")
        if confirmations and not args.apply:
            raise CloudflareError("Confirmation flags require --apply.")
    client = client_factory()
    if args.command in {"doctor", "zones"}:
        zones = client.paged("/zones")
        if args.command == "doctor":
            return {"ok": True, "mode": "live", "accessible_zone_count": len(zones),
                    "dns_read_or_write_access": "not_checked"}
        return {"zones": [{k: z[k] for k in ("id", "name", "status", "name_servers") if k in z}
                          for z in zones]}
    if args.command == "nameservers":
        zone = client.zone(args.zone)
        return {k: zone.get(k) for k in ("id", "name", "status", "name_servers")}
    if args.command == "records":
        from .dns import fqdn
        zone = client.zone(args.zone)
        query = {}
        if args.name:
            query["name"] = fqdn(args.name, zone["name"])
        if args.type:
            query["type"] = args.type
        records = client.paged(f'/zones/{zone["id"]}/dns_records', query)
        return {"zone": zone["name"], "records": [snapshot(r) for r in records]}
    params = dict(zone=args.zone, name=args.name, kind=args.type,
                  record_id=args.record_id, delete=args.command == "delete")
    if args.command == "upsert":
        params.update(content=args.content, ttl=args.ttl, priority=args.priority, proxied=args.proxied)
    plan = make_plan(client, **params)
    if not args.apply:
        return {"mode": "preview", "plan": plan, "writes_sent": 0}
    return apply_plan(client, plan, confirm_zone=args.confirm_zone, confirm_plan=args.confirm_plan)


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        result = execute(args)
        result["observed_at"] = datetime.now(timezone.utc).isoformat()
        print(json.dumps(result, indent=2, ensure_ascii=True))
        return 0
    except CloudflareError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 1
    except (ValueError, TypeError, KeyError):
        print(json.dumps({"ok": False, "error": "Unexpected API data; inspect remote state before retrying."}),
              file=sys.stderr)
        return 1
