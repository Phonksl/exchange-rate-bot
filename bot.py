import os
import logging
from keep_alive import keep_alive
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from api_service import get_currency_rates, get_history_7_days
from keyboard import main_kb, get_currency_selection_kb, get_history_kb


load_dotenv()


TOKEN = os.getenv('API_TOKEN')


logging.basicConfig(level=logging.INFO)


bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

class ConverterState(StatesGroup):
    waiting_for_amount = State()
    waiting_for_currency_from = State()
    waiting_for_currency_to = State()

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Вітаємо! Я бот для моніторингу курсу валют (за даними НБУ).\nОберіть дію:", reply_markup=main_kb)

@dp.message_handler(lambda message: message.text == "📊 Поточний курс")
async def show_rates(message: types.Message):
    rates = get_currency_rates()
    if rates:
        text = "📊 Актуальний офіційний курс (НБУ):\n\n"
        text += f"🇺🇸 USD: {rates['USD']:.2f} ₴\n"
        text += f"🇪🇺 EUR: {rates['EUR']:.2f} ₴\n"
        text += f"🇵🇱 PLN: {rates['PLN']:.2f} ₴\n"
        text += f"🇬🇧 GBP: {rates['GBP']:.2f} ₴\n"
        text += f"🇨🇭 CHF: {rates['CHF']:.2f} ₴\n"
        text += f"🇨🇦 CAD: {rates['CAD']:.2f} ₴\n"
        text += f"🇯🇵 JPY: {rates['JPY']:.2f} ₴\n"
        text += f"🇨🇿 CZK: {rates['CZK']:.2f} ₴\n"
        await message.reply(text)
    else:
        await message.reply("❌ Помилка отримання даних.")
@dp.message_handler(lambda message: message.text == "ℹ️ Допомога")
async def show_help(message: types.Message):
    await message.reply("🔹 Поточний курс — дані від НБУ.\n🔹 Конвертер — перевід між популярними валютами.\n🔹 Історія — динаміка за тиждень.")


@dp.message_handler(lambda message: message.text == "📈 Історія за 7 днів")
async def ask_history_currency(message: types.Message):
    await message.reply("Оберіть валюту для перегляду історії (до гривні):", reply_markup=get_history_kb())

@dp.callback_query_handler(lambda c: c.data.startswith('hist_'))
async def process_history(callback_query: types.CallbackQuery):
    currency = callback_query.data.split('_')[1]
    
    await bot.send_message(callback_query.from_user.id, f"⏳ Завантажую історію для {currency} від НБУ...")
    history_data = get_history_7_days(currency)
    
    if history_data:
        text = f"📈 Офіційний курс {currency} за 7 днів:\n\n" + "\n".join(history_data)
    else:
        text = "❌ Не вдалося завантажити історію."
        
    await bot.send_message(callback_query.from_user.id, text)
    await bot.answer_callback_query(callback_query.id)

# --- КОНВЕРТЕР ---
@dp.message_handler(lambda message: message.text == "💱 Конвертер валют")
async def start_converter(message: types.Message):
    await message.reply("Введіть суму, яку хочете конвертувати:")
    await ConverterState.waiting_for_amount.set()

@dp.message_handler(state=ConverterState.waiting_for_amount)
async def process_amount(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text.replace(',', '.'))
        await state.update_data(amount=amount)
        await message.reply("З якої валюти переводимо?", reply_markup=get_currency_selection_kb("from"))
        await ConverterState.waiting_for_currency_from.set()
    except ValueError:
        await message.reply("❌ Введіть число (наприклад, 100).")

@dp.callback_query_handler(lambda c: c.data.startswith('from_'), state=ConverterState.waiting_for_currency_from)
async def process_currency_from(callback_query: types.CallbackQuery, state: FSMContext):
    currency_from = callback_query.data.split('_')[1]
    await state.update_data(currency_from=currency_from)
    
    await bot.edit_message_text(f"Ви обрали: {currency_from}\nТепер оберіть, В ЯКУ валюту переводимо:", 
                                chat_id=callback_query.message.chat.id, 
                                message_id=callback_query.message.message_id,
                                reply_markup=get_currency_selection_kb("to"))
    await ConverterState.waiting_for_currency_to.set()

@dp.callback_query_handler(lambda c: c.data.startswith('to_'), state=ConverterState.waiting_for_currency_to)
async def process_currency_to(callback_query: types.CallbackQuery, state: FSMContext):
    currency_to = callback_query.data.split('_')[1]
    data = await state.get_data()
    amount = data.get('amount')
    currency_from = data.get('currency_from')
    
    rates = get_currency_rates()
    if not rates:
        await bot.send_message(callback_query.from_user.id, "❌ Помилка отримання актуальних курсів.")
        await state.finish()
        return


    rate_from = rates[currency_from]
    rate_to = rates[currency_to]
    
    amount_in_uah = amount * rate_from
    final_result = amount_in_uah / rate_to
    
    result_text = f"✅ Результат конвертації (за курсом НБУ):\n\n**{amount} {currency_from} = {final_result:.2f} {currency_to}**"
    
    await bot.edit_message_text(result_text, 
                                chat_id=callback_query.message.chat.id, 
                                message_id=callback_query.message.message_id,
                                parse_mode="Markdown")
    await state.finish()

if __name__ == '__main__':
    keep_alive() 
    executor.start_polling(dp, skip_updates=True) 