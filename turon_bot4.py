import asyncio
import logging

from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

# =============================================================
# SOZLAMALAR
# =============================================================
  BOT_TOKEN = "8955157366:AAFib_hwcAejCX93c0oZBKTnzl8NBbi8OlI"# @BotFather'dan olingan token

# Administratorga xabar yuborish uchun (ixtiyoriy). Chat ID ni yozing yoki None qoldiring.
ADMIN_CHAT_ID = 5581384015

# Markaz telefon raqamlari (matnlarda ko'rsatiladi)
CONTACT_PHONE_1 = "+998 99 393 14 45"
CONTACT_PHONE_2 = "+998 78 333 14 45"

logging.basicConfig(level=logging.INFO)

# =============================================================
# KURSLAR RO'YXATI
# =============================================================
# key -> (nomi, davomiyligi, jadvali, izoh)
COURSES = {
    "comp_lit": {
        "title": "Kompyuter savodxonligi",
        "duration": "2 oy",
        "schedule": "6 kun",
        "note": "🎁 1 kunlik BEPUL sinov darsi mavjud",
        "is_trial": True,
    },
    "ai": {
        "title": "AI (sun'iy intellekt)",
        "duration": "1 oy",
        "schedule": "haftasiga 3 kun",
        "note": None,
        "is_trial": False,
    },
    "web_dev": {
        "title": "Web dasturlash",
        "duration": "6 oy",
        "schedule": "haftasiga 3 kun",
        "note": None,
        "is_trial": False,
    },
    "math": {
        "title": "Matematika",
        "duration": "6 oy",
        "schedule": "haftasiga 3 kun",
        "note": None,
        "is_trial": False,
    },
    "russian": {
        "title": "Rus tili",
        "duration": "6 oy",
        "schedule": "haftasiga 3 kun",
        "note": None,
        "is_trial": False,
    },
    "english": {
        "title": "Ingliz tili",
        "duration": "6 oy",
        "schedule": "haftasiga 3 kun",
        "note": None,
        "is_trial": False,
    },
    "android": {
        "title": "Android dasturlash",
        "duration": "1 yil",
        "schedule": "haftasiga 3 kun",
        "note": None,
        "is_trial": False,
    },
    "cefr": {
        "title": "CEFR",
        "duration": "3 oy",
        "schedule": "haftasiga 6 kun",
        "note": None,
        "is_trial": False,
    },
    "preschool": {
        "title": "Maktabgacha tayyorlov",
        "duration": "6 oy",
        "schedule": "5 kun",
        "note": None,
        "is_trial": False,
    },
    "extra_ed": {
        "title": "Maktabdan tashqari ta'lim",
        "duration": "Davomiyligi belgilanmagan (1-4 sinf o'quvchilari uchun)",
        "schedule": "haftasiga 5 kun",
        "note": None,
        "is_trial": False,
    },
    "accounting": {
        "title": "Buxgalteriya va 1C",
        "duration": "3 oy",
        "schedule": "haftasiga 3 kun",
        "note": None,
        "is_trial": False,
    },
}

# =============================================================
# BILIMLAR BAZASI (Knowledge Base)
# =============================================================
INFO_TEXT = (
    "🏢 Turon o'quv markazi\n\n"
    "📍 Manzil: Andijon viloyati, Marhamat tumani, Ipak yo'li ko'chasi, 47-uy\n"
    "🕒 Ish vaqti: 08:00 - 18:00\n"
    "📞 Telefon: " + CONTACT_PHONE_1 + " / " + CONTACT_PHONE_2 + "\n"
    "🎁 Chegirma: Barcha kurslarga (bir oiladan 2 kishiga yoki 10% vaucher bilan)\n"
    "👩‍🏫 O'qituvchilar: 6+ oy tajriba, Ingliz tilida CEFR sertifikatiga ega"
)


def build_courses_text() -> str:
    lines = ["📚 Kurslarimiz:\n"]
    for i, c in enumerate(COURSES.values(), start=1):
        line = f"{i}️⃣ {c['title']} — {c['duration']} | {c['schedule']}"
        if c["note"]:
            line += f"\n     {c['note']}"
        lines.append(line)
    return "\n".join(lines)


COURSES_TEXT = build_courses_text()

CONFIRM_TRIAL_TEXT = (
    "✅ Rahmat! Arizangiz qabul qilindi.\n"
    "Siz Kompyuter savodxonligi kursining 1 kunlik BEPUL sinov darsiga yozildingiz.\n"
    "Tez orada administratorlarimiz siz bilan bog'lanishadi."
)

CONFIRM_APPLICATION_TEXT = (
    "✅ Rahmat! Arizangiz qabul qilindi.\n"
    "Tez orada administratorlarimiz siz bilan bog'lanishadi."
)

# =============================================================
# HOLATLAR (FSM States)
# =============================================================
class RegisterState(StatesGroup):
    waiting_name = State()
    waiting_phone = State()


# =============================================================
# KLAVIATURALAR
# =============================================================
def main_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📚 Kurslar")],
            [KeyboardButton(text="ℹ️ Ma'lumot (manzil, vaqt, chegirma)")],
            [KeyboardButton(text="📝 Kursga yozilish")],
        ],
        resize_keyboard=True,
    )


def courses_choice_kb() -> InlineKeyboardMarkup:
    buttons = []
    for key, c in COURSES.items():
        label = c["title"] + (" (bepul sinov)" if c["is_trial"] else "")
        buttons.append([InlineKeyboardButton(text=label, callback_data=f"apply_{key}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def phone_share_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📞 Raqamni yuborish", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


# =============================================================
# ROUTER va HANDLERLAR
# =============================================================
router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Assalomu alaykum! 👋\n"
        "Men Turon o'quv markazining yordamchisiman.\n"
        "Sizga qanday yordam bera olaman?",
        reply_markup=main_menu_kb(),
    )


@router.message(F.text == "ℹ️ Ma'lumot (manzil, vaqt, chegirma)")
async def show_info(message: Message):
    await message.answer(INFO_TEXT, reply_markup=main_menu_kb())


@router.message(F.text == "📚 Kurslar")
async def show_courses(message: Message):
    await message.answer(COURSES_TEXT, reply_markup=main_menu_kb())


@router.message(F.text == "📝 Kursga yozilish")
async def choose_course(message: Message):
    await message.answer(
        "Qaysi kursga yozilmoqchisiz? Tanlang 👇",
        reply_markup=courses_choice_kb(),
    )


@router.callback_query(F.data.startswith("apply_"))
async def apply_course(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    course_key = callback.data.removeprefix("apply_")
    course = COURSES.get(course_key)
    if not course:
        return

    await state.update_data(course_key=course_key, course_title=course["title"])
    await state.set_state(RegisterState.waiting_name)

    if course["is_trial"]:
        text = (
            f"Siz {course['title']} kursining 1 kunlik BEPUL sinov darsiga "
            f"yozilmoqchisiz.\n\nIsmingizni kiriting:"
        )
    else:
        text = f"Siz {course['title']} kursiga ariza qoldirmoqchisiz.\n\nIsmingizni kiriting:"

    await callback.message.answer(text, reply_markup=ReplyKeyboardRemove())


@router.message(RegisterState.waiting_name)
async def get_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(RegisterState.waiting_phone)
    await message.answer(
        "Telefon raqamingizni kiriting (masalan: +998901234567) "
        "yoki pastdagi tugma orqali yuboring:",
        reply_markup=phone_share_kb(),
    )


@router.message(RegisterState.waiting_phone, F.contact)
async def get_phone_contact(message: Message, state: FSMContext):
    await finish_registration(message, state, message.contact.phone_number)


@router.message(RegisterState.waiting_phone, F.text)
async def get_phone_text(message: Message, state: FSMContext):
    await finish_registration(message, state, message.text)


async def finish_registration(message: Message, state: FSMContext, phone: str):
    data = await state.get_data()
    name = data.get("name", "-")
    course_key = data.get("course_key")
    course_title = data.get("course_title", "-")
    course = COURSES.get(course_key, {})
    is_trial = course.get("is_trial", False)
    await state.clear()

    confirm_text = CONFIRM_TRIAL_TEXT if is_trial else CONFIRM_APPLICATION_TEXT
    await message.answer(confirm_text, reply_markup=main_menu_kb())

    if ADMIN_CHAT_ID:
        bot: Bot = message.bot
        kind = "Bepul sinov darsi (1 kunlik)" if is_trial else "Oddiy ariza"
        await bot.send_message(
            ADMIN_CHAT_ID,
            f"🆕 Yangi {kind}:\n"
            f"📘 Kurs: {course_title}\n"
            f"👤 Ism: {name}\n"
            f"📞 Tel: {phone}\n"
            f"🔗 Username: @{message.from_user.username or '-'}",
        )


@router.message()
async def fallback(message: Message):
    await message.answer(
        "Kechirasiz, savolingizni tushunmadim. Quyidagi menyudan foydalaning 👇",
        reply_markup=main_menu_kb(),
    )


# =============================================================
# ISHGA TUSHIRISH
# =============================================================
async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())