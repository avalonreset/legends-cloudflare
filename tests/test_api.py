import io
import json
import unittest
import urllib.error
from unittest.mock import patch

from legends_cloudflare.api import Client, CloudflareError, MAX_RESPONSE, NoRedirect


class Opener:
    def __init__(self, value):
        self.value = value
        self.calls = []

    def open(self, req, timeout):
        self.calls.append(req)
        if isinstance(self.value, Exception):
            raise self.value
        return io.BytesIO(self.value)


class ApiTests(unittest.TestCase):
    def client(self, value):
        c = Client("synthetic-token-for-offline-tests")
        c.opener = Opener(value)
        return c

    def test_fixed_origin_and_query_encoding(self):
        c = self.client(b'{"success":true,"result":[]}')
        c.request("GET", "/zones", query={"name": "example.com&attack=1"})
        url = c.opener.calls[0].full_url
        self.assertTrue(url.startswith("https://api.cloudflare.com/client/v4/zones?"))
        self.assertIn("%26", url)

    def test_reject_external_paths_before_transport(self):
        c = self.client(b"")
        for path in ["https://evil.example/", "//evil.example/", "/zones/../tokens", "/zones?bad=1"]:
            with self.subTest(path=path), self.assertRaises(CloudflareError):
                c.request("GET", path)
        self.assertEqual(c.opener.calls, [])

    def test_reject_zone_mutation(self):
        c = self.client(b"")
        for method in ["POST", "PATCH", "DELETE", "PUT"]:
            with self.subTest(method=method), self.assertRaises(CloudflareError):
                c.request(method, "/zones")
        self.assertEqual(c.opener.calls, [])

    def test_refuse_redirect(self):
        with self.assertRaises(CloudflareError):
            NoRedirect().redirect_request(None, None, 302, "", {}, "https://evil.example")

    def test_token_control_characters(self):
        for token in ["", " leading", "bad\nheader", "bad\rtoken", "bad\x7f"]:
            with self.subTest(token=repr(token)), self.assertRaises(CloudflareError):
                Client(token)

    def test_missing_token(self):
        with patch.dict("os.environ", {}, clear=True), self.assertRaises(CloudflareError):
            Client()

    def test_raw_provider_errors_not_exposed_or_retried(self):
        error = urllib.error.HTTPError("https://example.com", 403, "SENSITIVE", {}, None)
        c = self.client(error)
        with self.assertRaises(CloudflareError) as ctx:
            c.request("GET", "/zones")
        self.assertNotIn("SENSITIVE", str(ctx.exception))
        self.assertEqual(len(c.opener.calls), 1)

    def test_invalid_responses(self):
        for value in [b"not-json", b'{"success":false,"errors":["SENSITIVE"]}',
                      b'{"success":true}', b"[]", b"x" * (MAX_RESPONSE + 1)]:
            c = self.client(value)
            with self.assertRaises(CloudflareError) as ctx:
                c.request("GET", "/zones")
            self.assertNotIn("SENSITIVE", str(ctx.exception))

    def test_pagination_collects_all_pages(self):
        c = Client("synthetic")
        with patch.object(c, "request", side_effect=[
            {"result": [{"id": "a"*32}], "result_info": {"total_pages": 2}},
            {"result": [{"id": "b"*32}], "result_info": {"total_pages": 2}},
        ]) as request:
            self.assertEqual(len(c.paged("/zones")), 2)
            self.assertEqual(request.call_count, 2)

    def test_pagination_refuses_truncation(self):
        c = Client("synthetic")
        with patch.object(c, "request", return_value={
            "result": [{"id": "a"*32}], "result_info": {"total_pages": 1001}
        }), self.assertRaisesRegex(CloudflareError, "incomplete"):
            c.paged("/zones")

    def test_pagination_refuses_duplicates(self):
        c = Client("synthetic")
        with patch.object(c, "request", return_value={
            "result": [{"id": "a"*32}], "result_info": {"total_pages": 2}
        }), self.assertRaisesRegex(CloudflareError, "Duplicate"):
            c.paged("/zones")

    def test_zone_id_fetches_metadata(self):
        c = Client("synthetic")
        zone = {"id": "a"*32, "name": "example.com"}
        with patch.object(c, "request", return_value={"result": zone}) as request:
            self.assertEqual(c.zone("a"*32), zone)
            request.assert_called_once_with("GET", "/zones/" + "a"*32)

    def test_zone_name_requires_exact_match(self):
        c = Client("synthetic")
        with patch.object(c, "paged", return_value=[{"id": "a"*32, "name": "other.example"}]):
            with self.assertRaises(CloudflareError):
                c.zone("example.com")


if __name__ == "__main__":
    unittest.main()
