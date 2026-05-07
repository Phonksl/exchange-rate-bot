from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Головне нижнє меню (тільки 4 основні кнопки)
main_kb = ReplyKeyboardMarkup(resize_keyboard=True)
main_kb.add(KeyboardButton("📊 Поточний курс"), KeyboardButton("💱 Конвертер валют"))
main_kb.add(KeyboardButton("📈 Історія за 7 днів"), KeyboardButton("ℹ️ Допомога"))

# Розширена клавіатура для конвертера (всі ходові валюти)
def get_currency_selection_kb(prefix):
    kb = InlineKeyboardMarkup(row_width=3)
    kb.add(
        InlineKeyboardButton("🇺🇸 USD", callback_data=f"{prefix}_USD"),
        InlineKeyboardButton("🇪🇺 EUR", callback_data=f"{prefix}_EUR"),
        InlineKeyboardButton("🇵🇱 PLN", callback_data=f"{prefix}_PLN"),
        InlineKeyboardButton("🇬🇧 GBP", callback_data=f"{prefix}_GBP"),
        InlineKeyboardButton("🇨🇭 CHF", callback_data=f"{prefix}_CHF"),
        InlineKeyboardButton("🇨🇦 CAD", callback_data=f"{prefix}_CAD"),
        InlineKeyboardButton("🇯🇵 JPY", callback_data=f"{prefix}_JPY"),
        InlineKeyboardButton("🇨🇿 CZK", callback_data=f"{prefix}_CZK"),
        InlineKeyboardButton("🇺🇦 UAH", callback_data=f"{prefix}_UAH")
    )
    return kb

# Клавіатура для історії (тільки фіксовані кнопки популярних валют)
def get_history_kb():
    kb = InlineKeyboardMarkup(row_width=3)
    kb.add(
        InlineKeyboardButton("🇺🇸 USD", callback_data="hist_USD"),
        InlineKeyboardButton("🇪🇺 EUR", callback_data="hist_EUR"),
        InlineKeyboardButton("🇵🇱 PLN", callback_data="hist_PLN"),
        InlineKeyboardButton("🇬🇧 GBP", callback_data="hist_GBP"),
        InlineKeyboardButton("🇨🇭 CHF", callback_data="hist_CHF"),
        InlineKeyboardButton("🇨🇦 CAD", callback_data="hist_CAD"),
        InlineKeyboardButton("🇯🇵 JPY", callback_data="hist_JPY"),
        InlineKeyboardButton("🇨🇿 CZK", callback_data="hist_CZK"),
    )
    return kb