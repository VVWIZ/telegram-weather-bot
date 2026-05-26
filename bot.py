import json
import os
import sys
import requests

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "6968503274:AAHWZmuZGu74HXZkuyemFhQsBWGTIOBHW00"
USERS_FILE = "users.json"

WEATHER_DESC = {
    "Sunny": "Солнечно", "Clear": "Ясно", "Partly cloudy": "Переменная облачность",
    "Cloudy": "Облачно", "Overcast": "Пасмурно", "Mist": "Туман", "Fog": "Туман",
    "Light rain": "Лёгкий дождь", "Moderate rain": "Умеренный дождь",
    "Heavy rain": "Сильный дождь", "Light snow": "Лёгкий снег",
    "Moderate snow": "Умеренный снег", "Heavy snow": "Сильный снег",
    "Thunderstorm": "Гроза", "Blizzard": "Метель", "Patchy rain possible": "Возможен дождь",
    "Patchy snow possible": "Возможен снег", "Light drizzle": "Морось",
}


def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False)


def get_weather(lat, lon):
    url = f"https://wttr.in/{lat},{lon}?format=j1"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    c = data["current_condition"][0]
    desc_en = c["weatherDesc"][0]["value"]
    desc = WEATHER_DESC.get(desc_en, desc_en)
    temp = c["temp_C"]
    feels = c["FeelsLikeC"]
    humidity = c["humidity"]
    wind = c["windspeedKmph"]
    return (
        f"🌤 *Погода сейчас*\n"
        f"🌡 Температура: *{temp}°C* (ощущается {feels}°C)\n"
        f"☁️ Состояние: {desc}\n"
        f"💧 Влажность: {humidity}%\n"
        f"💨 Ветер: {wind} км/ч"
    )


def get_rate():
    url = "https://api.exchangerate-api.com/v4/latest/USD"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    rate = data["rates"]["KZT"]
    return f"💵 *Курс USD → KZT*: *{rate:.2f} ₸*"


def location_keyboard():
    keyboard = [[KeyboardButton("📍 Поделиться геолокацией", request_location=True)]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет!\n\n"
        "Я покажу тебе *актуальную погоду* и *курс тенге к доллару* — "
        "на любое твоё сообщение.\n\n"
        "Сначала поделись геолокацией 👇",
        reply_markup=location_keyboard(),
        parse_mode="Markdown"
    )


async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = load_users()
    user_id = str(update.message.from_user.id)
    lat = update.message.location.latitude
    lon = update.message.location.longitude
    users[user_id] = {"lat": lat, "lon": lon}
    save_users(users)
    await send_info(update, lat, lon)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = load_users()
    user_id = str(update.message.from_user.id)

    if user_id not in users:
        await update.message.reply_text(
            "📍 Сначала поделись геолокацией — нажми кнопку ниже.",
            reply_markup=location_keyboard()
        )
        return

    lat = users[user_id]["lat"]
    lon = users[user_id]["lon"]
    await send_info(update, lat, lon)


async def send_info(update: Update, lat, lon):
    try:
        weather = get_weather(lat, lon)
        rate = get_rate()
        await update.message.reply_text(
            f"{weather}\n\n{rate}",
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f"Ошибка: {e}")
        await update.message.reply_text("⚠️ Не удалось получить данные. Попробуй через минуту.")


def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.LOCATION, handle_location))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ Бот запущен. Нажми Ctrl+C чтобы остановить.")
    app.run_polling()


if __name__ == "__main__":
    main()
