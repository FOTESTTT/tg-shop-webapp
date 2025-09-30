import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = "8071489395:AAFUuUP2Didqomsdti2p28OSaLW3Ff01lro"
ADMIN_ID = 1038591016  # твой Telegram ID

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Каталог товаров
catalog = {
    "UC": {"60 UC": 81, "120 UC": 162, "240 UC": 340, "325 UC": 420, "660 UC": 820,
           "985 UC": 1270, "1320 UC": 1600, "1800 UC": 2100, "2460 UC": 3000, "3850 UC": 4100},
    "Pass": {"A7 Royale Pass": 980, "A7 ELITE PASS": 2500},
    "Transformer Cars": {"Жёлтый спорткар": 16500, "Серый спорткар": 16500,
                         "Серый грузовик": 16500, "Оранжевый спорткар": 48000},
    "Популярность": {"10 000": 160, "20 000": 320, "50 000": 630},
    "Транспорт": {"Вертолет": 1900, "Приват Джет": 8100}
}

cart = {}
ITEMS_PER_PAGE = 5  # товаров на одной странице

# Главное меню
def main_menu():
    keyboard = [
        [InlineKeyboardButton(text="🛍 Каталог", callback_data="catalog")],
        [InlineKeyboardButton(text="🛒 Корзина", callback_data="cart")],
        [InlineKeyboardButton(text="ℹ️ Помощь", callback_data="help")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# Кнопки категории с пагинацией
def category_menu(page=0):
    categories = list(catalog.keys())
    start = page * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE
    keyboard = [[InlineKeyboardButton(text=cat, callback_data=f"cat_{cat}_0")] for cat in categories[start:end]]
    nav = []
    if start > 0:
        nav.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"catpage_{page-1}"))
    if end < len(categories):
        nav.append(InlineKeyboardButton(text="➡️ Вперед", callback_data=f"catpage_{page+1}"))
    if nav:
        keyboard.append(nav)
    keyboard.append([InlineKeyboardButton(text="⬅️ Главное меню", callback_data="back")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# Кнопки товаров с пагинацией
def items_menu(category, page=0):
    items = list(catalog[category].items())
    start = page * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE
    keyboard = [[InlineKeyboardButton(text=f"{name} - {price}₽", callback_data=f"buy_{category}_{name}")]
                for name, price in items[start:end]]
    nav = []
    if start > 0:
        nav.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"itempage_{category}_{page-1}"))
    if end < len(items):
        nav.append(InlineKeyboardButton(text="➡️ Вперед", callback_data=f"itempage_{category}_{page+1}"))
    if nav:
        keyboard.append(nav)
    keyboard.append([InlineKeyboardButton(text="⬅️ Категории", callback_data="catalog")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# Кнопки корзины
def cart_menu(user_id):
    keyboard = []
    user_cart = cart.get(user_id, {})
    for item, qty in user_cart.items():
        keyboard.append([
            InlineKeyboardButton(text=f"➕ {item}", callback_data=f"inc_{item}"),
            InlineKeyboardButton(text=f"➖ {item}", callback_data=f"dec_{item}"),
            InlineKeyboardButton(text=f"❌ {item}", callback_data=f"del_{item}")
        ])
    if user_cart:
        keyboard.append([InlineKeyboardButton(text="✅ Оформить заказ", callback_data="checkout")])
    keyboard.append([InlineKeyboardButton(text="⬅️ Главное меню", callback_data="back")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# /start
@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer("Привет 👋! Добро пожаловать в магазин 🚀", reply_markup=main_menu())

# Показ корзины
async def show_cart(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user_cart = cart.get(user_id, {})
    if not user_cart:
        await callback.message.edit_text("🛒 Ваша корзина пуста.", reply_markup=main_menu())
        return
    text = "🛒 Ваша корзина:\n"
    total = 0
    for item, qty in user_cart.items():
        price = next((p for cat in catalog.values() if item in cat for p in [cat[item]]), 0)
        text += f"- {item} x{qty} ({price*qty}₽)\n"
        total += price*qty
    text += f"\n💰 Итого: {total}₽"
    await callback.message.edit_text(text, reply_markup=cart_menu(user_id))

# Обработка кнопок
@dp.callback_query()
async def handle_buttons(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    data = callback.data

    if data == "catalog":
        await callback.message.edit_text("📦 Выберите категорию:", reply_markup=category_menu(0))

    elif data.startswith("catpage_"):
        page = int(data.split("_")[1])
        await callback.message.edit_text("📦 Выберите категорию:", reply_markup=category_menu(page))

    elif data.startswith("cat_"):
        parts = data.split("_")
        category = parts[1]
        await callback.message.edit_text(f"📦 {category}:", reply_markup=items_menu(category, 0))

    elif data.startswith("itempage_"):
        _, category, page = data.split("_")
        page = int(page)
        await callback.message.edit_text(f"📦 {category}:", reply_markup=items_menu(category, page))

    elif data.startswith("buy_"):
        _, category, item_name = data.split("_", 2)
        cart.setdefault(user_id, {})
        cart[user_id][item_name] = cart[user_id].get(item_name, 0) + 1
        await callback.answer(f"✅ {item_name} добавлено в корзину!")

    elif data == "cart":
        await show_cart(callback)

    elif data.startswith("inc_"):
        item = data[4:]
        if item in cart.get(user_id, {}):
            cart[user_id][item] += 1
        await show_cart(callback)

    elif data.startswith("dec_"):
        item = data[4:]
        if item in cart.get(user_id, {}):
            cart[user_id][item] -= 1
            if cart[user_id][item] <= 0:
                del cart[user_id][item]
        await show_cart(callback)

    elif data.startswith("del_"):
        item = data[4:]
        if item in cart.get(user_id, {}):
            del cart[user_id][item]
        await show_cart(callback)

    elif data == "checkout":
        user_cart = cart.get(user_id, {})
        if not user_cart:
            await callback.answer("❌ Корзина пуста")
            return
        text = "📦 Новый заказ!\n"
        total = 0
        for item, qty in user_cart.items():
            price = next((p for cat in catalog.values() if item in cat for p in [cat[item]]), 0)
            text += f"- {item} x{qty} ({price*qty}₽)\n"
            total += price*qty
        text += f"\n💰 Итого: {total}₽"
        await bot.send_message(ADMIN_ID, f"Заказ от @{callback.from_user.username or user_id}:\n{text}")
        cart[user_id] = {}
        await callback.message.edit_text("✅ Заказ оформлен!", reply_markup=main_menu())
        await callback.answer("Заказ отправлен админу!")

    elif data == "help":
        await callback.message.edit_text("ℹ️ Для помощи пишите админу", reply_markup=main_menu())

    elif data == "back":
        await callback.message.edit_text("Главное меню:", reply_markup=main_menu())

    else:
        await callback.answer("Неизвестная команда")

InlineKeyboardButton(
    text="✅ Оформить и оплатить",
    web_app=WebAppInfo(url="https://github.com/FOTESTTT/tg-shop-webapp/blob/main/webapp.html")
)


# Запуск
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())


