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

def unwrap(data):
    if isinstance(data, list): return data
    if isinstance(data, dict):
        for key in ("products", "data", "items", "result"):
            value = data.get(key)
            if isinstance(value, list): return value
            if isinstance(value, dict):
                for nested in ("products", "items", "results"):
                    if isinstance(value.get(nested), list): return value[nested]
    return []
def pick(item, *keys, default=""):
    for key in keys:
        value = item.get(key) if isinstance(item, dict) else None
        if value is not None: return value
    return default
def product_label(p):
    return str(pick(p, "shortName", "name", "title", "symbol", "id", default="Product"))
def product_id(p):
    return str(pick(p, "productKey", "slug", "id", "product_id", "product", default=""))
def networks(p):
    value = pick(p, "networks", "delivery_networks", "network", default=[])
    if isinstance(value, str): return [value]
    if isinstance(value, list):
        return [str(x.get("id", x.get("name", x.get("code", x))) if isinstance(x, dict) else x) for x in value]
    return []
