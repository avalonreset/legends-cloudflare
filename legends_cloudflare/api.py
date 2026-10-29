"""Bounded Cloudflare API transport. No arbitrary URLs, retries or raw errors."""
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request

API_ROOT = "https://api.cloudflare.com/client/v4"
ID = r"[a-f0-9]{32}"
PATH = re.compile(rf"/zones(?:/{ID}(?:/dns_records(?:/{ID})?)?)?\Z")
MAX_RESPONSE = 16 * 1024 * 1024


class CloudflareError(Exception):
    """An actionable error safe to display without provider response bodies."""


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise CloudflareError("Redirect refused; credentials were not forwarded.")


class Client:
    def __init__(self, token=None):
        self.token = token if token is not None else os.environ.get("CLOUDFLARE_API_TOKEN")
        if not self.token or self.token != self.token.strip() or any(
            ord(c) < 33 or ord(c) > 126 for c in self.token
        ):
            raise CloudflareError("Set CLOUDFLARE_API_TOKEN through your secret manager.")
        self.opener = urllib.request.build_opener(
            urllib.request.ProxyHandler({}), NoRedirect()
        )

    def request(self, method, path, body=None, query=None):
        if not PATH.fullmatch(path):
            raise CloudflareError("Unsupported Cloudflare API path.")
        if method not in {"GET", "POST", "PATCH", "DELETE"}:
            raise CloudflareError("Unsupported method.")
        if method == "POST" and not re.fullmatch(rf"/zones/{ID}/dns_records", path):
            raise CloudflareError("Creation is restricted to DNS records.")
        if method in {"PATCH", "DELETE"} and not re.fullmatch(
            rf"/zones/{ID}/dns_records/{ID}", path
        ):
            raise CloudflareError("Mutation requires one exact DNS record ID.")
        url = API_ROOT + path
        if query:
            url += "?" + urllib.parse.urlencode(query)
        data = None if body is None else json.dumps(body).encode("utf-8")
        req = urllib.request.Request(
            url, data=data, method=method,
            headers={"Authorization": "Bearer " + self.token,
                     "Content-Type": "application/json",
                     "User-Agent": "legends-cloudflare/0.1.1"},
        )
        try:
            with self.opener.open(req, timeout=30) as response:
                raw = response.read(MAX_RESPONSE + 1)
            if len(raw) > MAX_RESPONSE:
                raise CloudflareError("API response exceeded the size limit.")
            result = json.loads(raw)
        except urllib.error.HTTPError as exc:
            raise CloudflareError(
                f"Cloudflare HTTP {exc.code}; inspect token scope or service status. "
                "No automatic retry. A failed write may have reached the service."
            ) from None
        except (urllib.error.URLError, TimeoutError, OSError):
            raise CloudflareError(
                "Cloudflare connection failed. No automatic retry; inspect remote "
                "state before repeating a write."
            ) from None
        except (ValueError, UnicodeError):
            raise CloudflareError("Invalid Cloudflare JSON response.") from None
        if not isinstance(result, dict) or result.get("success") is not True or "result" not in result:
            raise CloudflareError("Cloudflare did not confirm success; response details withheld.")
        return result

    def paged(self, path, query=None, max_pages=1000):
        records, seen = [], set()
        for page in range(1, max_pages + 1):
            result = self.request("GET", path, query={
                **(query or {}), "page": page, "per_page": 50,
            })
            batch = result["result"]
            if not isinstance(batch, list):
                raise CloudflareError("Expected an API result list.")
            for item in batch:
                if not isinstance(item, dict) or not re.fullmatch(ID, str(item.get("id", ""))):
                    raise CloudflareError("Invalid API resource ID.")
                if item["id"] in seen:
                    raise CloudflareError("Duplicate page results; repeat inventory after changes settle.")
                seen.add(item["id"])
            records.extend(batch)
            info = result.get("result_info", {})
            total = info.get("total_pages")
            if total is not None:
                if type(total) is not int or total < 0 or total > max_pages:
                    raise CloudflareError("Pagination limit or invalid metadata; inventory incomplete.")
                if page >= total:
                    return records
                if not batch:
                    raise CloudflareError("Pagination ended early; inventory incomplete.")
            elif len(batch) < 50:
                return records
        raise CloudflareError("Pagination limit reached; inventory incomplete.")

    def zone(self, value):
        if re.fullmatch(ID, value):
            zone = self.request("GET", "/zones/" + value)["result"]
        else:
            name = value.rstrip(".").lower()
            matches = [z for z in self.paged("/zones", {"name": name})
                       if z.get("name", "").lower() == name]
            if len(matches) != 1:
                raise CloudflareError("Expected one exact zone; use its ID if ambiguous.")
            zone = matches[0]
        if (not isinstance(zone, dict) or not re.fullmatch(ID, str(zone.get("id", "")))
                or not isinstance(zone.get("name"), str)):
            raise CloudflareError("Invalid zone response.")
        return zone
