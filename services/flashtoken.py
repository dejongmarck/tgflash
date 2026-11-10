import uuid
import httpx
from config import settings

class FlashTokenError(Exception): pass

class FlashToken:
    def __init__(self):
        self.headers = {"Authorization": f"Bearer {settings.flashtoken_api_key}", "Accept": "application/json"}

    async def request(self, method, path, **kwargs):
        if not settings.flashtoken_api_key:
            raise FlashTokenError("FLASHTOKEN_API_KEY is not configured.")
        async with httpx.AsyncClient(timeout=25) as client:
            response = await client.request(method, settings.api_base + path, headers=self.headers, **kwargs)
        try:
            data = response.json()
        except Exception:
            data = {"raw": response.text[:500]}
        if response.status_code >= 400:
            raise FlashTokenError(f"FlashToken API returned HTTP {response.status_code}: {data}")
        return data

    async def products(self):
        return await self.request("GET", "/products")

    async def account(self):
        return await self.request("GET", "/account")

    async def create_order(self, product, network, amount, wallet, idempotency_key):
        payload = {
            "product": str(product),
            "delivery_network": str(network),
            "amount": float(amount),
            "bsc_address": wallet
        }
        return await self.request(
            "POST", "/orders", json=payload,
            headers={**self.headers, "Idempotency-Key": idempotency_key}
        )

    async def order(self, order_id):
        return await self.request("GET", f"/orders/{order_id}")

def _as_list(value):
    if isinstance(value, list): return value
    if isinstance(value, dict):
        for nested in ("products", "items", "results", "data", "catalog", "catalogue"):
            if isinstance(value.get(nested), (list, dict)):
                found = _as_list(value[nested])
                if found: return found
        # dict keyed by product id: {"usdt": {...}, "btc": {...}}
        if value and all(isinstance(v, dict) for v in value.values()):
            return [{"id": k, **v} if "id" not in v else v for k, v in value.items()]
    return []

def unwrap(data):
    result = _as_list(data)
    if not result:
        import logging
        shape = list(data.keys()) if isinstance(data, dict) else type(data).__name__
        logging.getLogger(__name__).warning("Catalogue parsed as empty; response shape: %s; body: %s", shape, str(data)[:500])
    return result
def pick(item, *keys, default=""):
    for key in keys:
        value = item.get(key) if isinstance(item, dict) else None
        if value is not None: return value
    return default
def product_label(p):
    return str(pick(p, "name", "title", "symbol", "id", default="Product"))
def product_id(p):
    return str(pick(p, "id", "product_id", "product"))
def networks(p):
    value = pick(p, "networks", "delivery_networks", "network", default=[])
    if isinstance(value, str): return [value]
    if isinstance(value, list):
        return [str(x.get("id", x.get("name", x.get("code", x))) if isinstance(x, dict) else x) for x in value]
    return []
