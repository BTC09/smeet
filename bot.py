import asyncio
import logging
import json
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message, WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import FSInputFile
import os

# ============================================
# НАСТРОЙКИ - СЮДА ВСТАВИТЬ СВОИ ДАННЫЕ
# ============================================
BOT_TOKEN = "8212007178:AAEEp5zfPfsdvysOqdoczkZioKds2f_sWfs"  # ПОЛУЧИТЬ У @BotFather
WEBAPP_URL = "https://btc09.github.io/smeet/"    # СЮДА ЗАГРУЗИШЬ HTML
ADMIN_IDS = [8591334505]  # ТВОЙ TELEGRAM ID (получить у @userinfobot)

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ============================================
# КОМАНДА /start
# ============================================
@dp.message(Command("start"))
async def cmd_start(message: Message):
    text = (
        "✨ <b>SMEET Detailing — Gold Standard</b> ✨\n\n"
        "Добро пожаловать в премиальный детейлинг центр.\n"
        "Нажми кнопку ниже, чтобы открыть приложение и забронировать время."
    )
    
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="📱 ОТКРЫТЬ SMEET APP",
        web_app=WebAppInfo(url=WEBAPP_URL)
    ))
    
    await message.answer(
        text, 
        reply_markup=builder.as_markup(), 
        parse_mode="HTML"
    )

# ============================================
# ПОЛУЧЕНИЕ ЗАКАЗОВ ИЗ MINI APP
# ============================================
@dp.message(F.web_app_data)
async def handle_web_app_data(message: Message):
    """Сюда приходят все заказы из Mini App"""
    try:
        # Получаем данные
        data = json.loads(message.web_app_data.data)
        order_time = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        
        # Формируем КРАСИВОЕ сообщение для админа
        admin_text = (
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🔔 <b>НОВАЯ ЗАПИСЬ SMEET</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            
            f"📅 <b>ДАТА И ВРЕМЯ:</b>\n"
            f"• Запись: {data.get('date', 'Не выбрано')} в {data.get('time', 'Не выбрано')}\n"
            f"• Заявка создана: {order_time}\n\n"
            
            f"👤 <b>КЛИЕНТ:</b>\n"
            f"• ID: <code>{message.from_user.id}</code>\n"
            f"• Имя: {message.from_user.full_name}\n"
            f"• Username: @{message.from_user.username or 'нет'}\n"
            f"• Телефон: {data.get('phone', 'Не указан')}\n\n"
            
            f"🚗 <b>АВТОМОБИЛЬ:</b>\n"
            f"• Марка/модель: {data.get('brand', 'Не указано')}\n"
            f"• Год: {data.get('year', 'Не указан')}\n"
            f"• VIN: <code>{data.get('vin', 'Не указан')}</code>\n\n"
        )
        
        # Добавляем услуги
        services = data.get('services', [])
        if services:
            admin_text += f"✨ <b>ВЫБРАННЫЕ УСЛУГИ:</b>\n"
            for s in services:
                admin_text += f"  • {s}\n"
            admin_text += "\n"
        
        # Добавляем дополнительные опции
        extras = data.get('extras', [])
        if extras:
            admin_text += f"➕ <b>ДОПОЛНИТЕЛЬНО:</b>\n"
            for e in extras:
                admin_text += f"  • {e}\n"
            admin_text += "\n"
        else:
            admin_text += f"➕ <b>ДОПОЛНИТЕЛЬНО:</b> нет\n\n"
        
        # Напоминание
        reminder_map = {
            '1h': 'За 1 час',
            '3h': 'За 3 часа',
            '12h': 'За 12 часов',
            '24h': 'За 24 часа'
        }
        reminder_text = reminder_map.get(data.get('reminder', '1h'), 'За 1 час')
        admin_text += f"⏰ <b>НАПОМИНАНИЕ:</b> {reminder_text}\n\n"
        
        # ИТОГО
        admin_text += (
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💰 <b>ИТОГО К ОПЛАТЕ:</b> {data.get('total', 0):,} ₽\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"<i>📌 Статус: ожидает подтверждения</i>"
        )
        
        # Отправляем админу
        for admin_id in ADMIN_IDS:
            try:
                await bot.send_message(admin_id, admin_text, parse_mode="HTML")
            except:
                pass
        
        # Отправляем подтверждение клиенту
        client_text = (
            f"✅ <b>Заявка успешно отправлена!</b>\n\n"
            f"📅 Вы записаны на: <b>{data.get('date')} в {data.get('time')}</b>\n\n"
            f"🔔 Напоминание: {reminder_text}\n"
            f"📞 Телефон для связи: {data.get('phone', 'не указан')}\n\n"
            f"Наш менеджер свяжется с вами для подтверждения записи.\n"
            f"Спасибо, что выбираете SMEET!"
        )
        
        await message.answer(client_text, parse_mode="HTML")
        
        # Логируем в консоль
        logging.info(f"Новый заказ от {message.from_user.full_name}: {data.get('total')}₽")
        
    except Exception as e:
        logging.error(f"Ошибка при обработке заказа: {e}")
        await message.answer("❌ Произошла ошибка при отправке заявки. Попробуйте еще раз.")

# ============================================
# КОМАНДА ДЛЯ ПРОСМОТРА СТАТИСТИКИ
# ============================================
@dp.message(Command("stats"))
async def cmd_stats(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔ Доступ запрещен")
        return
    
    # Здесь можно добавить статистику из БД
    stats_text = (
        "📊 <b>Статистика SMEET</b>\n\n"
        "✅ Бот активен\n"
        "✅ Mini App загружен\n"
        f"👤 Ваш ID: {message.from_user.id}\n\n"
        f"📅 Сегодня: {datetime.now().strftime('%d.%m.%Y')}"
    )
    
    await message.answer(stats_text, parse_mode="HTML")

# ============================================
# ЗАПУСК БОТА
# ============================================
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
