import asyncio, logging
from database import pending_orders, update_order
from services.flashtoken import FlashToken
from config import settings

log = logging.getLogger(__name__)

async def status_poller(bot):
    api = FlashToken()
    while True:
        try:
            for local in await pending_orders():
                try:
                    data = await api.order(local.provider_order_id)
                    status = str(data.get("status", local.status)).lower()
                    payment = str(data.get("payment_status", local.payment_status)).lower()
                    updated = await update_order(local.provider_order_id, status, payment)
                    if updated and status in ("completed", "cancelled", "expired"):
                        message = {
                            "completed": "✅ <b>Order completed!</b> Your order has been delivered.",
                            "cancelled": "❌ <b>Order cancelled.</b> Contact support if you need help.",
                            "expired": "⌛ <b>Order expired.</b> Please create a new order if you still want to buy."
                        }.get(status)
                        if message:
                            await bot.send_message(updated.telegram_user_id, message)
                except Exception as e:
                    log.warning("Could not check order %s: %s", local.provider_order_id, e)
        except Exception:
            log.exception("Order polling cycle failed")
        await asyncio.sleep(max(5, settings.poll_interval))
