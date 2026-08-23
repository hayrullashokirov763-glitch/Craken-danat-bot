import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

class S(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()

threading.Thread(target=lambda: HTTPServer(('0.0.0.0', 10000), S).serve_forever(), daemon=True).start()
import os
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

BOT_TOKEN = os.getenv("BOT_TOKEN", "8239144356:AAFcWdPNt-oY_RkPPodHGjull6TonE_oNlk")

# ID SOZLAMALARI:
ADMIN_GROUP_ID = -1004251107671  # Cheklar boradigan Telegram Guruh ID si (minus bilan boshlanadi)
ADMIN_USERNAME = "craken_donat_admin" # Admin shaxsiy usernamesi (@ siz)
KARTA_NUM = "5440810301878483" # Admin karta raqami

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

class DonationState(StatesGroup):
    waiting_for_id_nick = State()
    waiting_for_check = State()

TEXTS = {
    'uz': {
        'welcome': "Assalomu alaykum! Donat botimizga xush kelibsiz. O'yinni tanlang:",
        'admin_contact': f"Ushbu o'yin bo'yicha donat qilish uchun adminga murojaat qiling: @craken_donat_admin",
        'select_package': "Kerakli valyuta paketini tanlang (narxlar so'mda, 15% ustama bilan):",
        'ask_id_nick': "Iltimos, o'yindagi **ID** va **Nickname (Tahlallusingiz)**ni birgalikda yuboring:",
        'send_payment': "To'lovni amalga oshiring:\n\n💳 **Karta:** `{karta}`\n💰 **Summa:** {price}\n\nTo'lovni amalga oshirgach, **chek (rasm)**ni shu yerga yuboring.",
        'confirm_btn': "✅ To'lovni tasdiqlayman",
        'check_received': "✅ Chek qabul qilindi!\n\nTo'lov 24 soat ichida hisobingizga tushiriladi. Agarda muammo paydo bo'lsa, adminga yozishingiz mumkin: @{admin}",
        'ask_check_first': "Iltimos, avval to'lov chekini (rasmini) yuboring!"
    },
    'ru': {
        'welcome': "Здравствуйте! Добро пожаловать в донат бот. Выберите игру:",
        'admin_contact': f"Для доната в эту игру напишите админу: @craken_donat_admin",
        'select_package': "Выберите нужный пакет (цены в сумах с учетом 15% надбавки):",
        'ask_id_nick': "Пожалуйста, отправьте ваш игровой **ID** и **Никнейм**:",
        'send_payment': "Совершите оплату:\n\n💳 **Карта:** `{karta}`\n💰 **Сумма:** {price}\n\nПосле оплаты отправьте **чек (фото)** сюда.",
        'confirm_btn': "✅ Подтверждаю оплату",
        'check_received': "✅ Чек получен!\n\nОплата будет зачислена в течение 24 часов. В случае проблем напишите админу: @{admin}",
        'ask_check_first': "Пожалуйста, сначала отправьте чек оплаты (фото)!"
    },
    'en': {
        'welcome': "Welcome to our donation bot! Select a game:",
        'admin_contact': f"To donate for this game, please contact the admin: @craken_donat_admin",
        'select_package': "Select the desired package (prices in UZS with 15% markup):",
        'ask_id_nick': "Please send your in-game **ID** and **Nickname**:",
        'send_payment': "Make the payment:\n\n💳 **Card:** `{karta}`\n💰 **Amount:** {price}\n\nAfter payment, send the **receipt (photo)** here.",
        'confirm_btn': "✅ Confirm Payment",
        'check_received': "✅ Receipt received!\n\nYour payment will be processed within 24 hours. If any issue arises, contact admin: @{admin}",
        'ask_check_first': "Please send the payment receipt (photo) first!"
    }
}

# Narxlar So'mda (+15% ustama qo'shilgan)
GAMES_DATA = {
    "pubg": {
        "name": "🔫 PUBG Mobile",
        "items": [
            ("60 UC", "15 000 so'm"),
            ("300 + 25 UC", "72 000 so'm"),
            ("600 + 60 UC", "147 000 so'm"),
            ("1500 + 300 UC", "375 000 so'm"),
            ("3000 + 850 UC", "753 000 so'm"),
            ("6000 + 2100 UC", "1 492 000 so'm")
        ]
    },
    "mlbb": {
        "name": "🛡️ Mobile Legends",
        "items": [
            ("50 Almaz", "15 000 so'm"),
            ("150 Almaz", "43 000 so'm"),
            ("250 Almaz", "72 000 so'm"),
            ("500 Almaz", "147 000 so'm"),
            ("1000 Almaz", "299 000 so'm"),
            ("1500 Almaz", "450 000 so'm")
        ]
    },
    "ff": {
        "name": "🔥 Free Fire",
        "items": [
            ("100 Almaz", "17 000 so'm"),
            ("310 Almaz", "51 000 so'm"),
            ("520 Almaz", "79 000 so'm"),
            ("1060 Almaz", "170 000 so'm"),
            ("2180 Almaz", "328 000 so'm")
        ]
    },
    "so2": {
        "name": "💥 Standoff 2",
        "items": [
            ("100 Gold", "34 000 so'm"),
            ("500 Gold", "145 000 so'm"),
            ("1000 Gold", "256 000 so'm"),
            ("3000 Gold", "555 000 so'm")
        ]
    }
}

def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="lang_uz"),
         InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
         InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")]
    ])

@dp.message(CommandStart())
async def start_cmd(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Iltimos, tilni tanlang / Выберите язык / Select language:", reply_markup=main_menu())

@dp.callback_query(F.data.startswith("lang_"))
async def select_lang(callback: CallbackQuery, state: FSMContext):
    lang = callback.data.split("_")[1]
    await state.update_data(lang=lang)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔫 PUBG Mobile", callback_data="g_pubg"), InlineKeyboardButton(text="🛡️ Mobile Legends", callback_data="g_mlbb")],
        [InlineKeyboardButton(text="🔥 Free Fire", callback_data="g_ff"), InlineKeyboardButton(text="💥 Standoff 2", callback_data="g_so2")],
        [InlineKeyboardButton(text="🏰 Clash of Clans", callback_data="g_admin"), InlineKeyboardButton(text="👑 Clash Royale", callback_data="g_admin")],
        [InlineKeyboardButton(text="⭐ Brawl Stars", callback_data="g_admin"), InlineKeyboardButton(text="🎮 Boshqa o'yin", callback_data="g_admin")]
    ])
    await callback.message.edit_text(TEXTS[lang]['welcome'], reply_markup=kb)

@dp.callback_query(F.data == "g_admin")
async def show_admin_contact(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get('lang', 'uz')
    await callback.message.answer(TEXTS[lang]['admin_contact'])
    await callback.answer()

@dp.callback_query(F.data.startswith("g_"))
async def show_game_packages(callback: CallbackQuery, state: FSMContext):
    game_key = callback.data.split("_")[1]
    data = await state.get_data()
    lang = data.get('lang', 'uz')
    
    game = GAMES_DATA[game_key]
    await state.update_data(game_name=game['name'])
    
    buttons = [[InlineKeyboardButton(text=f"{amt} — {prc}", callback_data=f"pkg_{game_key}_{i}")] for i, (amt, prc) in enumerate(game['items'])]
    await callback.message.edit_text(f"<b>{game['name']}</b>\n\n{TEXTS[lang]['select_package']}", parse_mode="HTML", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@dp.callback_query(F.data.startswith("pkg_"))
async def ask_user_details(callback: CallbackQuery, state: FSMContext):
    _, game_key, idx = callback.data.split("_")
    item = GAMES_DATA[game_key]["items"][int(idx)]
    
    await state.update_data(package=item[0], price=item[1])
    data = await state.get_data()
    lang = data.get('lang', 'uz')
    
    await state.set_state(DonationState.waiting_for_id_nick)
    await callback.message.answer(TEXTS[lang]['ask_id_nick'], parse_mode="Markdown")
    await callback.answer()

@dp.message(DonationState.waiting_for_id_nick)
async def receive_id_nick(message: Message, state: FSMContext):
    await state.update_data(user_info=message.text)
    data = await state.get_data()
    lang = data.get('lang', 'uz')
    
    text = TEXTS[lang]['send_payment'].format(karta=KARTA_NUM, price=data['price'])
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=TEXTS[lang]['confirm_btn'], callback_data="confirm_pay")]])
    
    await state.set_state(DonationState.waiting_for_check)
    await message.answer(text, parse_mode="Markdown", reply_markup=kb)

@dp.message(DonationState.waiting_for_check, F.photo)
async def receive_check_photo(message: Message, state: FSMContext):
    await state.update_data(check_photo_id=message.photo[-1].file_id)
    data = await state.get_data()
    lang = data.get('lang', 'uz')
    
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=TEXTS[lang]['confirm_btn'], callback_data="confirm_pay")]])
    await message.answer("📸 Chek qabul qilindi. Pastdagi tasdiqlash tugmasini bosing:", reply_markup=kb)

@dp.callback_query(F.data == "confirm_pay", DonationState.waiting_for_check)
async def check_confirmation(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get('lang', 'uz')
    
    if not data.get('check_photo_id'):
        await callback.answer(TEXTS[lang]['ask_check_first'], show_alert=True)
        return

    admin_msg = (
        f"📥 **YANGI BUYURTMA (CHEK)!**\n\n"
        f"👤 **Mijoz:** @{callback.from_user.username} (ID: `{callback.from_user.id}`)\n"
        f"🎮 **O'yin:** {data['game_name']}\n"
        f"📦 **Paket:** {data['package']}\n"
        f"💰 **Tushishi kerak bo'lgan summa:** {data['price']}\n"
        f"🆔 **O'yin ID / Nick:** {data['user_info']}"
    )
    
    # Chekni Admin Guruhiga yuborish
    await bot.send_photo(chat_id=ADMIN_GROUP_ID, photo=data['check_photo_id'], caption=admin_msg, parse_mode="Markdown")
    
    await callback.message.answer(TEXTS[lang]['check_received'].format(admin=ADMIN_USERNAME))
    await state.clear()
    await callback.answer()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
