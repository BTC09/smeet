import asyncio
import logging
import json
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message, WebAppInfo, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

# ============================================
# 🔥 ВСТАВЬ СВОИ ДАННЫЕ 🔥
# ============================================
BOT_TOKEN = "8212007178:AAEEp5zfPfsdvysOqdoczkZioKds2f_sWfs"  # Твой токен от @BotFather
ADMIN_IDS = [8591334505]              # Твой ID от @userinfobot
WEBAPP_URL = "https://btc09.github.io/smeet/"  # Ссылка на GitHub Pages

# ============================================
# 🚀 ЗАПУСК БОТА
# ============================================
logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: Message):
    """Отправляет кнопку с Mini App"""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="📱 ОТКРЫТЬ SMEET",
        web_app=WebAppInfo(url=WEBAPP_URL)
    ))
    
    await message.answer(
        "✨ <b>SMEET Detailing</b> — премиальный детейлинг\n\n"
        "Нажми кнопку ниже, чтобы выбрать услуги и забронировать время.",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )

@dp.message(F.web_app_data)
async def handle_booking(message: Message):
    """Сюда приходят заказы из Mini App"""
    try:
        data = json.loads(message.web_app_data.data)
        order_time = datetime.now().strftime("%d.%m.%Y %H:%M")
        
        # Расшифровка напоминания
        reminder_text = {
            '1h': 'За 1 час',
            '3h': 'За 3 часа',
            '12h': 'За 12 часов',
            '24h': 'За 24 часа'
        }.get(data.get('reminder'), 'За 1 час')
        
        # Формируем красивое сообщение
        admin_text = (
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🔔 <b>НОВАЯ ЗАПИСЬ SMEET</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📅 <b>Дата:</b> {data.get('date', 'Не выбрана')}\n"
            f"⏰ <b>Время:</b> {data.get('time', 'Не выбрано')}\n"
            f"👤 <b>Клиент:</b> {message.from_user.full_name}\n"
            f"📞 <b>Телефон:</b> {data.get('phone', 'Не указан')}\n\n"
            f"🚗 <b>Автомобиль:</b>\n"
            f"• Марка: {data.get('brand', 'Не указано')}\n"
            f"• Год: {data.get('year', 'Не указан')}\n"
            f"• VIN: {data.get('vin', 'Не указан')}\n\n"
            f"⏱️ <b>Напоминание:</b> {reminder_text}\n\n"
            f"✨ <b>Выбранные услуги:</b>\n"
        )
        
        for s in data.get('services', []):
            admin_text += f"  • {s}\n"
        
        if data.get('extras'):
            admin_text += f"\n➕ <b>Дополнительно:</b>\n"
            for e in data.get('extras'):
                admin_text += f"  • {e}\n"
        
        admin_text += (
            f"\n━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💰 <b>ИТОГО:</b> {data.get('total', 0):,} ₽\n"
            f"━━━━━━━━━━━━━━━━━━━━━━"
        )
        
        # Отправляем админу
        for admin_id in ADMIN_IDS:
            try:
                await bot.send_message(admin_id, admin_text, parse_mode="HTML")
            except:
                pass
        
        # Подтверждение клиенту
        await message.answer(
            f"✅ <b>Заявка принята!</b>\n\n"
            f"Вы записаны на {data.get('date')} в {data.get('time')}\n\n"
            f"Мы напомним вам {reminder_text.lower()}.\n"
            f"Спасибо за выбор SMEET!",
            parse_mode="HTML"
        )
        
    except Exception as e:
        logging.error(f"Ошибка: {e}")
        await message.answer("❌ Произошла ошибка. Попробуйте еще раз.")

async def main():
    print("="*50)
    print("🚀 SMEET БОТ ЗАПУЩЕН!")
    print("="*50)
    print(f"🤖 Токен: {BOT_TOKEN[:10]}...")
    print(f"👑 Админы: {ADMIN_IDS}")
    print(f"🌐 WebApp URL: {WEBAPP_URL}")
    print("="*50)
    print("📨 Ожидаю заказы...")
    print("="*50)
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
