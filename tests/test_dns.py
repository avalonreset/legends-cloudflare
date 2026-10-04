import copy
import unittest

from legends_cloudflare.api import CloudflareError
from legends_cloudflare.dns import apply_plan, fqdn, make_plan
from legends_cloudflare.cli import execute, parser

ZID, RID, RID2 = "a" * 32, "b" * 32, "c" * 32
RECORD = {"id": RID, "name": "www.example.com", "type": "A", "content": "192.0.2.1",
          "ttl": 300, "proxied": False, "comment": "keep", "tags": ["owner:ops"],
          "settings": {}, "modified_on": "2026-01-01T00:00:00Z"}


class Fake:
    def __init__(self, records=None):
        self.records = copy.deepcopy([RECORD] if records is None else records)
        self.calls = []
        self.corrupt = False

    def zone(self, value):
        return {"id": ZID, "name": "example.com"}

    def paged(self, path, query=None):
        return copy.deepcopy(self.records)

    def request(self, method, path, body=None):
        self.calls.append((method, path, body))
        if method == "GET":
            return {"result": copy.deepcopy(self.records[0])}
        if method == "PATCH":
            self.records[0].update(body)
            if self.corrupt:
                self.records[0]["content"] = "192.0.2.99"
            return {"result": {"id": RID}}
        if method == "POST":
            self.records.append({"id": RID, **body})
            return {"result": {"id": RID}}
        if method == "DELETE":
            self.records = [r for r in self.records if r["id"] != RID]
            return {"result": {"id": RID}}
        raise AssertionError(method)


def plan(client, **kwargs):
    return make_plan(client, **{"zone": "example.com", "name": "www", "kind": "A",
                               "content": "192.0.2.2", **kwargs})


def apply(client, p):
    return apply_plan(client, p, confirm_zone="example.com", confirm_plan=p["sha256"])


class DnsTests(unittest.TestCase):
    def test_preview_has_no_writes(self):
        c = Fake()
        p = plan(c)
        self.assertEqual(p["action"], "update")
        self.assertEqual(c.calls, [])

    def test_update_omits_unspecified_fields(self):
        c = Fake()
        p = plan(c)
        self.assertEqual(set(p["payload"]), {"name", "type", "content"})
        self.assertTrue(apply(c, p)["verified"])
        self.assertEqual(c.records[0]["ttl"], 300)
        self.assertEqual(c.records[0]["comment"], "keep")
        self.assertEqual([v[0] for v in c.calls], ["GET", "PATCH", "GET"])

    def test_bad_confirmation_never_writes(self):
        c = Fake()
        p = plan(c)
        for zone, digest in [("wrong.example", p["sha256"]), ("example.com", "wrong")]:
            with self.assertRaises(CloudflareError):
                apply_plan(c, p, confirm_zone=zone, confirm_plan=digest)
        self.assertEqual(c.calls, [])

    def test_new_preview_hash_changes_with_state(self):
        c = Fake()
        old = plan(c)
        c.records[0]["content"] = "192.0.2.4"
        new = plan(c)
        self.assertNotEqual(old["sha256"], new["sha256"])
        with self.assertRaises(CloudflareError):
            apply_plan(c, new, confirm_zone="example.com", confirm_plan=old["sha256"])

    def test_immediate_read_detects_race(self):
        c = Fake()
        p = plan(c)
        c.records[0]["comment"] = "another operator"
        with self.assertRaisesRegex(CloudflareError, "changed"):
            apply(c, p)
        self.assertEqual([v[0] for v in c.calls], ["GET"])

    def test_ambiguous_records_require_id(self):
        c = Fake([RECORD, {**RECORD, "id": RID2}])
        with self.assertRaisesRegex(CloudflareError, "Multiple"):
            plan(c)
        self.assertEqual(plan(c, record_id=RID2)["before"]["id"], RID2)

    def test_delete_requires_exact_id(self):
        c = Fake()
        with self.assertRaises(CloudflareError):
            plan(c, delete=True)
        with self.assertRaises(CloudflareError):
            plan(c, delete=True, record_id=RID2)
        p = plan(c, delete=True, record_id=RID)
        self.assertTrue(apply(c, p)["verified"])
        self.assertEqual(c.records, [])

    def test_delete_keeps_other_matching_records(self):
        c = Fake([RECORD, {**RECORD, "id": RID2}])
        p = plan(c, delete=True, record_id=RID)
        self.assertTrue(apply(c, p)["verified"])
        self.assertEqual([r["id"] for r in c.records], [RID2])

    def test_create_and_appearing_record(self):
        c = Fake([])
        p = plan(c)
        self.assertEqual(p["payload"]["ttl"], 1)
        self.assertFalse(p["payload"]["proxied"])
        self.assertTrue(apply(c, p)["verified"])
        c = Fake([])
        p = plan(c)
        c.records = [RECORD]
        with self.assertRaisesRegex(CloudflareError, "appeared"):
            apply(c, p)
        self.assertEqual(c.calls, [])

    def test_noop(self):
        c = Fake()
        p = plan(c, content=RECORD["content"])
        self.assertEqual(apply(c, p)["mode"], "noop")
        self.assertEqual(c.calls, [])

    def test_readback_failure_reported_after_write(self):
        c = Fake()
        c.corrupt = True
        p = plan(c)
        with self.assertRaisesRegex(CloudflareError, "readback"):
            apply(c, p)
        self.assertEqual(len([x for x in c.calls if x[0] == "PATCH"]), 1)

    def test_name_scope_and_normalization(self):
        self.assertEqual(fqdn("@", "EXAMPLE.COM"), "example.com")
        self.assertEqual(fqdn("WWW", "example.com"), "www.example.com")
        self.assertEqual(fqdn("_verify.www.example.com.", "example.com"), "_verify.www.example.com")
        for name in ["other.com", "bad..example.com", "-bad", "w*w", "a" * 64]:
            with self.subTest(name=name), self.assertRaises(CloudflareError):
                fqdn(name, "example.com")

    def test_invalid_fields(self):
        for fields in [{"content": "not-an-ip"}, {"kind": "AAAA", "content": "192.0.2.2"},
                       {"ttl": 0}, {"ttl": 59}, {"priority": 5},
                       {"kind": "TXT", "proxied": True},
                       {"kind": "SRV"}, {"proxied": True, "ttl": 300},
                       {"kind": "MX", "content": "mail host"},
                       {"record_id": "wrong"}]:
            with self.subTest(fields=fields), self.assertRaises(CloudflareError):
                plan(Fake(), **fields)

    def test_mx_priority(self):
        with self.assertRaises(CloudflareError):
            plan(Fake([]), kind="MX", content="mail.example.com")
        p = plan(Fake([]), kind="MX", content="mail.example.com", priority=10)
        self.assertEqual(p["payload"]["priority"], 10)

    def test_offline_doctor_does_not_construct_client(self):
        def fail():
            raise AssertionError("network client constructed")
        self.assertTrue(execute(parser().parse_args(["doctor"]), fail)["ok"])

    def test_cli_gates_precede_client(self):
        def fail():
            raise AssertionError("client constructed before argument validation")
        for tail in [["--apply"], ["--confirm-zone", "example.com"]]:
            args = parser().parse_args([
                "upsert", "--zone", "example.com", "--name", "www", "--type", "A",
                "--content", "192.0.2.2", *tail])
            with self.assertRaises(CloudflareError):
                execute(args, fail)


if __name__ == "__main__":
    unittest.main()
