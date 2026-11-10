# FlashToken Telegram Reseller Bot

Multilingual Telegram bot (English, Dutch, French, German) using the documented FlashToken Reseller API.

## Important payment and markup limitations

The official API documentation says:
- Customers pay using FlashToken's payment methods; resellers cannot replace payment credentials.
- `POST /orders` accepts `product`, `delivery_network`, `amount`, and `bsc_address`, and returns an order ID and payment link.
- The `amount` field is the quantity to deliver, not a reseller surcharge.
- FlashToken's 30% commission is credited after delivery (`completed`) and paid manually by the service owner.

Therefore this bot **does not pretend to collect payment to your own wallet**. It opens the official FlashToken checkout. The configured 40% is currently an *indicative resale quote only* where a product unit price is present in the catalogue; it is clearly labelled as not being charged by FlashToken. Do not advertise it as collected revenue. To actually charge your own 40% markup, integrate a separate payment provider and confirm payment before creating the FlashToken supplier order. That requires a provider account and a verified payment/webhook flow.

API reference: https://flashtoken.shop/api-docs

## Features
- Four languages, auto-detected from Telegram and user-selectable.
- Product catalogue from FlashToken.
- Product/network/quantity/receiving wallet order flow.
- FlashToken checkout link.
- Order history and automatic status polling.
- Basic admin overview (`/admin`).
- PostgreSQL support for Railway; SQLite fallback for local testing.
- Referral start parameter is recorded when the referrer already exists.

## Deploy to Railway
1. Create a Telegram bot with @BotFather.
2. Push this repository to GitHub.
3. In Railway, create a project from the GitHub repository.
4. Add a PostgreSQL service in Railway.
5. In the bot service Variables, set:
   - `TELEGRAM_BOT_TOKEN`
   - `FLASHTOKEN_API_KEY`
   - `ADMIN_IDS` (your numeric Telegram user ID; comma-separated for multiple admins)
   - `DATABASE_URL` (use Railway's PostgreSQL connection variable; ensure it is a `postgresql://` URL)
   - `MARKUP_PERCENT=40`
   - `ORDER_POLL_SECONDS=8`
6. Deploy. The worker runs `python bot.py`.

## Local run
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Set environment variables in your shell or use a dotenv runner.
python bot.py
```

## Security
- Never commit `.env` or API keys.
- Use Railway Variables for secrets.
- Keep `ADMIN_IDS` restricted to trusted Telegram account IDs.
- The bot never asks customers to send funds to a wallet supplied in chat.
