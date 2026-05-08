"""
Trip Checklist Bot — Harvard Friends Visit to Kazakhstan
May 13–17

Requirements:
  pip install python-telegram-bot==20.7

Run:
  BOT_TOKEN=your_token python trip_bot.py

Get token: @BotFather → /newbot
"""

import json
import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_TOKEN_HERE")

# ─────────────────────────────────────────────
# CHECKLISTS
# ─────────────────────────────────────────────

CHECKLISTS = {
    "prep": {
        "title": "📋 Подготовка до поездки",
        "items": [
            "Подтвердить бронирование отелей (Астана + Буробай)",
            "Выслать гостям финальную агенду с деталями",
            "Уточнить рейсы и время прилёта каждого гостя 13 мая",
            "Организовать трансфер из аэропорта Астана (13 мая)",
            "Заказать автобус Астана → Буробай (15 мая, 8:30)",
            "Подтвердить рейсы Астана → Алматы (16 мая, 18:30–20:30)",
            "Уточнить пищевые предпочтения / аллергии всех гостей",
            "Подготовить welcome-пакеты / сувениры по Казахстану",
            "Подтвердить гида для тура по Астане (14 мая)",
            "Согласовать визиты на объекты BI Group (14 мая)",
            "Согласовать посещение штаб-квартиры BI Group (14 мая)",
            "Подтвердить встречу в Family Office (14 мая, 15:30)",
            "Подготовить ужин дома: меню, сервировка, персонал",
            "Уточнить тему и формат форума в автобусе (15 мая)",
            "Согласовать визит в школу iQanat Буробай: директор + лучшие ученики",
            "Подтвердить гида для тура по Буробаю (15 мая)",
            "Организовать хайкинг в горах (16 мая, 8:00)",
            "Подготовить материалы для Форума ч.2 (16 мая, 11:00)",
            "Продумать активности 16 мая (14:00–17:00)",
            "Подтвердить трансфер Буробай → аэропорт Астана (16 мая)",
            "Подтвердить гида по Алматы + объекты BI (17 мая)",
            "Уточнить Option 1 / Option 2 у каждого гостя (17 мая)",
        ],
    },
    "may13": {
        "title": "✈️ 13 мая — Прилёт в Астану",
        "items": [
            "Трансфер из аэропорта: водители на месте, таблички с именами",
            "Номера в отеле готовы к заселению",
            "Welcome-подарки / amenities разложены в номерах",
            "Поделиться контактами координатора с каждым гостем",
            "Сообщить гостям расписание на 14 мая",
        ],
    },
    "may14": {
        "title": "🏙️ 14 мая — Астана",
        "items": [
            "Завтрак: ресторан и время подтверждены",
            "Гид и транспорт у отеля в 9:00",
            "Объекты BI Group для осмотра подготовлены",
            "Штаб-квартира BI: пропуска, материалы, встречающие готовы",
            "Обед: ресторан забронирован на 13:00",
            "Family Office: встреча подтверждена на 15:30",
            "Маршрут и трансфер до дома на 17:30",
            "Ужин дома: готово (меню, сервировка, напитки, персонал)",
            "Оповестить гостей о выезде из отеля 15 мая в 8:30",
        ],
    },
    "may15": {
        "title": "🌲 15 мая — Астана → Буробай",
        "items": [
            "Чекаут из отеля: багаж собран, счета закрыты",
            "Автобус у отеля в 8:30 — подтвердить с водителем",
            "Гид для тура по Астане (8:30–10:00) на месте",
            "Материалы для форума в автобусе распечатаны / загружены",
            "Вода и снеки в автобусе",
            "Бронь в отеле Буробая подтверждена, ранний чекин если нужен",
            "Обед в отеле: время и меню согласованы",
            "iQanat школа: директор, ученики и экскурсия подтверждены",
            "Гид для тура по Буробаю (15:30–17:00) готов",
            "Ужин: ресторан / место забронировано",
        ],
    },
    "may16": {
        "title": "⛰️ 16 мая — Буробай → Алматы",
        "items": [
            "Хайкинг (8:00): маршрут, гид, трекинговая обувь / экипировка",
            "Перекус после хайкинга организован",
            "Форум ч.2 (11:00): площадка, материалы, модератор готовы",
            "Обед (13:00): ресторан подтверждён",
            "Активности (14:00–17:00): программа утверждена",
            "Чекаут из отеля: багаж собран, счета закрыты",
            "Трансфер Буробай → аэропорт Астана (выезд ~15:00)",
            "Регистрация на рейс: проверить онлайн-чекин",
            "Рейс Астана–Алматы 18:30 — все на борту",
            "Трансфер из аэропорта Алматы в отель",
        ],
    },
    "may17": {
        "title": "🍎 17 мая — Алматы",
        "items": [
            "Гид и транспорт у отеля в 8:30",
            "Объекты BI Group в Алматы: посещения согласованы",
            "Обед (12:30): ресторан забронирован",
            "Option 1 (продолжение программы): расписание выслано гостям",
            "Option 2 (вылет): трансферы до аэропорта организованы",
            "Прощальные подарки / памятные сувениры подготовлены",
        ],
    },
}

# ─────────────────────────────────────────────
# STATE: user_id → { checklist_key → set of done indices }
# ─────────────────────────────────────────────
state: dict[int, dict[str, set]] = {}


def get_user_state(user_id: int) -> dict[str, set]:
    if user_id not in state:
        state[user_id] = {key: set() for key in CHECKLISTS}
    return state[user_id]


def checklist_keyboard(user_id: int, key: str) -> InlineKeyboardMarkup:
    done = get_user_state(user_id)[key]
    items = CHECKLISTS[key]["items"]
    buttons = []
    for i, item in enumerate(items):
        label = ("✅ " if i in done else "⬜ ") + item
        buttons.append([InlineKeyboardButton(label, callback_data=f"toggle:{key}:{i}")])

    # Progress line
    pct = int(len(done) / len(items) * 100)
    progress_label = f"Прогресс: {len(done)}/{len(items)} ({pct}%)"
    buttons.append([InlineKeyboardButton(progress_label, callback_data="noop")])
    buttons.append([
        InlineKeyboardButton("✔️ Отметить все", callback_data=f"all:{key}"),
        InlineKeyboardButton("↩️ Сбросить", callback_data=f"reset:{key}"),
    ])
    buttons.append([InlineKeyboardButton("« Главное меню", callback_data="menu")])
    return InlineKeyboardMarkup(buttons)


def main_menu_keyboard() -> InlineKeyboardMarkup:
    buttons = []
    for key, data in CHECKLISTS.items():
        buttons.append([InlineKeyboardButton(data["title"], callback_data=f"open:{key}")])
    return InlineKeyboardMarkup(buttons)


# ─────────────────────────────────────────────
# HANDLERS
# ─────────────────────────────────────────────

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = (
        "🇰🇿 *Чек-листы поездки — Казахстан, май 2025*\n\n"
        "Выбери раздел, чтобы отмечать выполненные пункты.\n"
        "Прогресс сохраняется до перезапуска бота."
    )
    await update.message.reply_text(
        text, parse_mode="Markdown", reply_markup=main_menu_keyboard()
    )


async def button(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    if data == "menu":
        await query.edit_message_text(
            "🇰🇿 *Чек-листы поездки — Казахстан, май 2025*\n\nВыбери раздел:",
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard(),
        )

    elif data == "noop":
        return

    elif data.startswith("open:"):
        key = data.split(":")[1]
        title = CHECKLISTS[key]["title"]
        await query.edit_message_text(
            f"*{title}*\n\nОтмечай выполненные пункты 👇",
            parse_mode="Markdown",
            reply_markup=checklist_keyboard(user_id, key),
        )

    elif data.startswith("toggle:"):
        _, key, idx = data.split(":")
        idx = int(idx)
        done = get_user_state(user_id)[key]
        if idx in done:
            done.discard(idx)
        else:
            done.add(idx)
        title = CHECKLISTS[key]["title"]
        await query.edit_message_text(
            f"*{title}*\n\nОтмечай выполненные пункты 👇",
            parse_mode="Markdown",
            reply_markup=checklist_keyboard(user_id, key),
        )

    elif data.startswith("all:"):
        key = data.split(":")[1]
        items = CHECKLISTS[key]["items"]
        get_user_state(user_id)[key] = set(range(len(items)))
        title = CHECKLISTS[key]["title"]
        await query.edit_message_text(
            f"*{title}*\n\nОтмечай выполненные пункты 👇",
            parse_mode="Markdown",
            reply_markup=checklist_keyboard(user_id, key),
        )

    elif data.startswith("reset:"):
        key = data.split(":")[1]
        get_user_state(user_id)[key] = set()
        title = CHECKLISTS[key]["title"]
        await query.edit_message_text(
            f"*{title}*\n\nОтмечай выполненные пункты 👇",
            parse_mode="Markdown",
            reply_markup=checklist_keyboard(user_id, key),
        )


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    print("Bot started. Press Ctrl+C to stop.")
    app.run_polling()


if __name__ == "__main__":
    main()
