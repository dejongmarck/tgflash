from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from i18n import t

def main_menu(lang):
return ReplyKeyboardMarkup(
keyboard=[
[
KeyboardButton(text=t(lang, “shop”)),
KeyboardButton(text=t(lang, “orders”))
],
[
KeyboardButton(text=t(lang, “account”)),
KeyboardButton(text=t(lang, “language”))
],
[
KeyboardButton(text=t(lang, “help”))
]
],
resize_keyboard=True
)

def language_kb():
return InlineKeyboardMarkup(
inline_keyboard=[
[
InlineKeyboardButton(text=“🇬🇧 English”, callback_data=“lang:en”),
InlineKeyboardButton(text=“🇳🇱 Nederlands”, callback_data=“lang:nl”)
],
[
InlineKeyboardButton(text=“🇫🇷 Français”, callback_data=“lang:fr”),
InlineKeyboardButton(text=“🇩🇪 Deutsch”, callback_data=“lang:de”)
]
]
)