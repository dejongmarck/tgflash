import uuid, logging
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from database import save_user, get_user, set_language, add_order, list_orders, Session, User, Order
from sqlalchemy import select, func
from keyboards import main_menu, language_kb
from i18n import t
from services.flashtoken import FlashToken, unwrap, product_label, product_id, networks, pick
from config import settings

router = Router()
log = logging.getLogger(__name__)
api = FlashToken()
PRODUCT_CACHE = {}

class Purchase(StatesGroup):
    product = State()
    network = State()
    amount = State()
    wallet = State()
    confirm = State()

def lang_of(user):
    return user.language if user else "en"

@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()
    arg = (message.text or "").split(maxsplit=1)
    ref = None
    if len(arg) > 1 and arg[1].startswith("ref_"):
        try: ref = int(arg[1][4:])
        except ValueError: pass
    lang = (message.from_user.language_code or "en")[:2]
    if lang not in ("en","nl","fr","de"): lang = "en"
    user = await save_user(message.from_user.id, lang, ref)
    await message.answer(t(user.language,"welcome"), reply_markup=main_menu(user.language))

@router.message(Command("admin"))
async def admin(message: Message):
    if message.from_user.id not in settings.admin_ids:
        return await message.answer("Not authorized.")
    async with Session() as s:
        users = await s.scalar(select(func.count()).select_from(User))
        orders = await s.scalar(select(func.count()).select_from(Order))
        complete = await s.scalar(select(func.count()).select_from(Order).where(Order.status=="completed"))
    await message.answer(f"<b>Admin overview</b>\nUsers: {users}\nOrders: {orders}\nCompleted: {complete}\nMarkup setting: {settings.markup_percent}%")

@router.message(F.text)
async def menu(message: Message, state: FSMContext):
    user = await get_user(message.from_user.id)
    if not user:
        user = await save_user(message.from_user.id, "en")
    lang = lang_of(user)
    text = message.text
    if text in (t(lang,"language"), "/language"):
        return await message.answer(t(lang,"choose_language"), reply_markup=language_kb())
    if text == t(lang,"help"):
        return await message.answer(t(lang,"help_text"))
    if text == t(lang,"account"):
        try:
            data = await api.account()
            return await message.answer("<b>FlashToken reseller account</b>\n<pre>"+str(data)[:3500]+"</pre>")
        except Exception:
            return await message.answer(t(lang,"account_unavailable"))
    if text == t(lang,"orders"):
        orders = await list_orders(message.from_user.id)
        if not orders: return await message.answer(t(lang,"orders_empty"))
        lines = [f"#{o.provider_order_id} · {o.product_name} · {o.amount:g} · {o.status}" for o in orders]
        return await message.answer("<b>Your recent orders</b>\n" + "\n".join(lines))
    if text == t(lang,"shop"):
        try:
            data = await api.products()
            products = unwrap(data)
            if not products: return await message.answer(t(lang,"no_products"))
            buttons = []
            for p in products[:50]:
                pid = product_id(p)
                if not pid: continue
                PRODUCT_CACHE[pid] = p
                buttons.append([InlineKeyboardButton(text=product_label(p)[:60], callback_data=f"prod:{pid}")])
            return await message.answer(t(lang,"choose_product"), reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
        except Exception as e:
            log.exception("Catalog error")
            return await message.answer("Could not load the FlashToken catalogue. Please try again later.")

@router.callback_query(F.data.startswith("lang:"))
async def language_callback(call: CallbackQuery):
    lang = call.data.split(":")[1]
    await set_language(call.from_user.id, lang)
    await call.message.answer(t(lang,"welcome"), reply_markup=main_menu(lang))
    await call.answer()

@router.callback_query(F.data.startswith("prod:"))
async def product_callback(call: CallbackQuery, state: FSMContext):
    pid = call.data.split(":",1)[1]
    p = PRODUCT_CACHE.get(pid)
    if not p:
        await call.answer("Catalogue expired. Open Shop again.", show_alert=True); return
    ns = networks(p)
    if not ns: ns = [str(pick(p,"delivery_network","network",default="default"))]
    await state.update_data(product_id=pid, product_name=product_label(p), product_data=p)
    await state.set_state(Purchase.network)
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=n[:60], callback_data=f"net:{n}")] for n in ns[:30]])
    await call.message.answer(t(lang_of(await get_user(call.from_user.id)),"choose_network"), reply_markup=kb)
    await call.answer()

@router.callback_query(F.data.startswith("net:"))
async def network_callback(call: CallbackQuery, state: FSMContext):
    net = call.data.split(":",1)[1]
    await state.update_data(network=net)
    await state.set_state(Purchase.amount)
    await call.message.answer(t(lang_of(await get_user(call.from_user.id)),"enter_amount"))
    await call.answer()

@router.message(Purchase.amount)
async def amount_message(message: Message, state: FSMContext):
    try:
        amount = float(message.text.replace(",","."))
        if amount <= 0 or amount > 1_000_000: raise ValueError()
    except Exception:
        return await message.answer("Please enter a valid positive number.")
    await state.update_data(amount=amount)
    await state.set_state(Purchase.wallet)
    await message.answer(t(lang_of(await get_user(message.from_user.id)),"enter_wallet"))

@router.message(Purchase.wallet)
async def wallet_message(message: Message, state: FSMContext):
    wallet = (message.text or "").strip()
    if len(wallet) < 20 or len(wallet) > 160 or any(c.isspace() for c in wallet):
        return await message.answer("That wallet address does not look valid. Please check it and send it again.")
    await state.update_data(wallet=wallet)
    data = await state.get_data()
    user = await get_user(message.from_user.id); lang = lang_of(user)
    p = data.get("product_data", {})
    price = pick(p, "price", "unit_price", "cost", default=None)
    quote = "not available"
    try:
        if price is not None: quote = f"{float(price) * float(data['amount']) * (1 + settings.markup_percent/100):.6g}"
    except Exception: pass
    await state.set_state(Purchase.confirm)
    text = (f"<b>{t(lang,'confirm')}</b>\n"
            f"Product: {data['product_name']}\nNetwork: {data['network']}\n"
            f"Amount to deliver: {data['amount']:g}\nWallet: <code>{wallet}</code>\n"
            + t(lang,"markup_note", pct=settings.markup_percent, quote=quote)
            + "\n\nFlashToken creates and prices the actual checkout. The indicative markup above is not charged unless the provider supports a separate reseller price.")
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang,"buy"), callback_data="order:create")],
        [InlineKeyboardButton(text=t(lang,"cancel"), callback_data="order:cancel")]
    ])
    await message.answer(text, reply_markup=kb)

@router.callback_query(F.data == "order:cancel")
async def cancel_order(call: CallbackQuery, state: FSMContext):
    await state.clear(); await call.message.answer("Order cancelled."); await call.answer()

@router.callback_query(F.data == "order:create")
async def create_order(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if not data.get("product_id"):
        await call.answer("Order session expired. Start again.", show_alert=True); return
    try:
        result = await api.create_order(data["product_id"], data["network"], data["amount"], data["wallet"], f"tg-{call.from_user.id}-{uuid.uuid4().hex}")
        provider_id = str(pick(result,"id","order_id",default=""))
        pay_url = str(pick(result,"payment_url","payment_link","checkout_url","url",default=""))
        if not provider_id or not pay_url:
            log.error("Unexpected create-order response: %s", result)
            await call.message.answer("FlashToken returned an unexpected response. No payment link was shown. Contact support.")
            await state.clear(); await call.answer(); return
        await add_order(telegram_user_id=call.from_user.id, provider_order_id=provider_id,
                        product_id=data["product_id"], product_name=data["product_name"],
                        network=data["network"], amount=data["amount"],
                        status=str(result.get("status","waiting")), payment_status=str(result.get("payment_status","waiting")),
                        payment_url=pay_url)
        user = await get_user(call.from_user.id); lang = lang_of(user)
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="💳 Open official FlashToken checkout", url=pay_url)]])
        await call.message.answer(t(lang,"created", id=provider_id, status=result.get("status","waiting"), url=pay_url), reply_markup=kb)
    except Exception as e:
        log.exception("Order creation failed")
        await call.message.answer("Could not create the order with FlashToken. Please try again later.")
    finally:
        await state.clear()
        await call.answer()
