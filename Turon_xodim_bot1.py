import asyncio
import logging

from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    Message,
    CallbackQuery,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

# =============================================================
# SOZLAMALAR
# =============================================================
BOT_TOKEN = "8404550660:AAFJ0iJ9tRHMzJ_ygXYyH4iNBW7lx8TyZfM"  # @BotFather'dan olingan token

# Natijalarni adminga (HR/rahbarga) yuborish uchun. Chat ID'ingizni yozing.
ADMIN_CHAT_ID = 5581384015

logging.basicConfig(level=logging.INFO)

# =============================================================
# 20 TA SAVOL (A/B)
# =============================================================
QUESTIONS = [
    ("Men belgilangan topshiriq asosida tartibli ishlayman",
     "Men erkinlikda o'zim tashabbus ko'rsatishni yoqtiraman"),
    ("Menga aniqlik va ko'rsatmalar muhim",
     "Noaniq vaziyatlarda o'zim qaror qabul qilishni xohlayman"),
    ("Ishonchli tizim va barqarorlikni qadrlayman",
     "Yangi vazifalar va chaqiriqlardan ilhom olaman"),
    ("Harakatlarimni reja asosida quraman",
     "Imkoniyatlarni ko'rib turib tez moslashaman"),
    ("Men yetkazilgan topshiriqni mukammal bajaraman",
     "Men natijaga yetishish uchun o'zim yo'l tanlayman"),
    ("O'zimga berilgan chegaralar doirasida samarali ishlayman",
     "Chegaralarni kengaytirishni va o'zgarishni qidiraman"),
    ("Muammolarni rahbarim bilan hal qilishni afzal bilaman",
     "Muammolarni o'zim hal qilishga harakat qilaman"),
    ("Menga muhit, jarayon va aniqlik muhim",
     "Menga tezlik, o'sish va natija muhim"),
    ("Tavakkal qilishdan oldin barcha risklarni o'lchayman",
     "Riskni o'z vaqtida qabul qilish — bu o'sishning bir qismi"),
    ("Tartibli jarayonlarda o'zimni qulay his qilaman",
     "Tez o'zgaruvchi vaziyatlarda motivatsiyam ortadi"),
    ("Stabil jamoada aniq rolga ega bo'lishni afzal bilaman",
     "Jamoani o'zgartiradigan fikr va energiyani olib kiraman"),
    ("Bir pozitsiyada chuqur ishlashni yoqtiraman",
     "Doim yangi mas'uliyat va vazifalarga o'sishni istayman"),
    ("O'rgatish va yo'l ko'rsatishni yaxshi qabul qilaman",
     "O'rgatish va yo'l ko'rsatishni o'zimga vazifa deb bilaman"),
    ("Jamoada qanday ishlashni menga ko'rsatishsa, tez o'zlashtiraman",
     "Jamoada o'z strategiyam bilan boshqalarga yo'l ochaman"),
    ("Mijozlar bilan tayyor ssenariy asosida ishlashni yoqtiraman",
     "Mijoz xarakteriga qarab yondashuvni o'zim belgilayman"),
    ("Maqsadga tizimli va asta-sekin yondashaman",
     "Maqsadga keskin va natijaga yo'naltirilgan usul bilan boraman"),
    ("Har doim yo'riqnoma asosida ishlayman",
     "O'zimga ishonaman va mustaqil qaror qabul qilaman"),
    ("Men topshiriqlarni bajaruvchi rolini yaxshi bajaraman",
     "Men jarayonni boshqaruvchi rolga intilaman"),
    ("Avval strategiyani chuqur o'rganaman",
     "Tez test qilib natijani ko'raman va yo'nalishni moslashtiraman"),
    ("Jarayondagi aniqlik menga ishonch beradi",
     "Noaniqlikda yo'l topish — bu mening kuchim"),
]

TOTAL_QUESTIONS = len(QUESTIONS)

# =============================================================
# NATIJA MATNLARI (SWOT) — faqat adminga yuboriladi
# =============================================================
RESULT_A_TITLE = "🚀 SPRINTER"
RESULT_A_TEXT = (
    f"{RESULT_A_TITLE}\n"
    "Kuchli start, motivatsiyasi yuqori. Qisqa muddatda katta natija ko'rsatadi, "
    "kreativ va tez fikrlaydi, insonlarni tez ilhomlantiradi.\n\n"
    "💪 Kuchli tomonlari:\n"
    "• Kuchli start, motivatsiyasi yuqori\n"
    "• Qisqa muddatda katta natija\n"
    "• Kreativ va tez fikrlovchi\n"
    "• Insonlarni tez ilhomlantiradi\n\n"
    "⚠️ Zaif tomonlari:\n"
    "• Tez zerikadi\n"
    "• Uzoq muddatli loyihalarda charchaydi\n"
    "• Tugatmaslik odati bor\n"
    "• Emotsiyaga bog'liq ishlaydi\n\n"
    "🌱 Imkoniyatlari:\n"
    "• Qisqa sprintlar bilan tez-tez motivatsiya yangilash\n"
    "• Boshqalarni ilhomlantirib liderga aylanish\n"
    "• Tez natija orqali ishonch qozonish\n"
    "• Qisqa muddatli loyihalar orqali katta daromad topishi mumkin\n\n"
    "🔺 Xavflari:\n"
    "• Tez qaror qilishi oqibatida katta muammolar yuzaga kelishi mumkin\n"
    "• Juda tez o'zgarishi tufayli atrofidagilarga salbiy ta'sir o'tkazishi mumkin\n"
    "• Biror ishni boshlashdan ko'ra tugatishi juda qiyin"
)

RESULT_B_TITLE = "🏃 MARAFONCHI"
RESULT_B_TEXT = (
    f"{RESULT_B_TITLE}\n"
    "Sekin, lekin barqaror harakat qiladi. Uzoq muddatli maqsadlarga erishishda "
    "kuchli. Sezilarli sabr-toqat, qat'iyat va tizimlilik bilan ajralib turadi. "
    "Doimiy harakatda bo'ladi va oxirigacha yetadi, hatto sekin bo'lsa ham.\n\n"
    "💪 Kuchli tomonlari:\n"
    "• Sabrli, barqaror\n"
    "• Disiplinaga asoslangan\n"
    "• Yakuniy natijadan motivatsiya oladi\n"
    "• Kichik odatlar bilan yirik tizimlarni boshqaradi\n\n"
    "⚠️ Zaif tomonlari:\n"
    "• Sekin boshlaydi\n"
    "• Yangi loyihalarda sust\n"
    "• Boshlang'ich bosqichda motivatsiya past\n"
    "• Qisqa muddatli rejalar bilan qiynaladi\n\n"
    "🌱 Imkoniyatlari:\n"
    "• Katta tizimlarni boshqarish\n"
    "• Doimiy odatlar bilan uzoq muddatli o'zgarish qilish\n"
    "• Ustoz, yetakchi, murabbiyga aylanish\n\n"
    "🔺 Xavflari:\n"
    "• Asta-sekinlik bahona bo'lib qolishi mumkin\n"
    "• Doimiy holatga \"komfort zonasi\" sifatida yopishib olish\n"
    "• O'zgarishga qarshilik ko'rsatish"
)

# =============================================================
# HOLATLAR (FSM State)
# =============================================================
class QuizState(StatesGroup):
    waiting_name = State()
    in_progress = State()


# =============================================================
# KLAVIATURALAR
# =============================================================
def start_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="▶️ Testni boshlash", callback_data="start_quiz")]]
    )


def question_kb(index: int) -> InlineKeyboardMarkup:
    a_text, b_text = QUESTIONS[index]
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"A) {a_text}", callback_data="ans_a")],
            [InlineKeyboardButton(text=f"B) {b_text}", callback_data="ans_b")],
        ]
    )


# =============================================================
# ROUTER va HANDLERLAR
# =============================================================
router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Assalomu alaykum! 👋\n\n"
        "Bu — <b>Turon xodimlar uslub testi</b>.\n"
        f"Sizga {TOTAL_QUESTIONS} ta savol beriladi, har birida A yoki B "
        "variantini tanlaysiz.\n\n"
        "Boshlaymizmi?",
        reply_markup=start_kb(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "start_quiz")
async def start_quiz(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(QuizState.waiting_name)
    await callback.message.answer(
        "Ismingiz va familiyangizni kiriting:",
        reply_markup=ReplyKeyboardRemove(),
    )


@router.message(QuizState.waiting_name)
async def get_name(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text, index=0, score_a=0, score_b=0)
    await state.set_state(QuizState.in_progress)
    await ask_question(message, 0)


async def ask_question(message: Message, index: int):
    a_text, b_text = QUESTIONS[index]
    await message.answer(
        f"<b>{index + 1}-savol / {TOTAL_QUESTIONS}</b>\n\n"
        f"A) {a_text}\n\n"
        f"B) {b_text}",
        reply_markup=question_kb(index),
        parse_mode="HTML",
    )


@router.callback_query(QuizState.in_progress, F.data.in_({"ans_a", "ans_b"}))
async def handle_answer(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    index = data.get("index", 0)
    score_a = data.get("score_a", 0)
    score_b = data.get("score_b", 0)

    if callback.data == "ans_a":
        score_a += 1
    else:
        score_b += 1

    next_index = index + 1

    if next_index >= TOTAL_QUESTIONS:
        full_name = data.get("full_name", "-")
        await state.clear()
        await finish_quiz(callback.message, score_a, score_b, full_name, callback.from_user)
        return

    await state.update_data(index=next_index, score_a=score_a, score_b=score_b)
    await ask_question(callback.message, next_index)


async def finish_quiz(message: Message, score_a: int, score_b: int, full_name: str, user):
    # Xodimga faqat umumiy tasdiqlash xabari ko'rsatiladi, natija ko'rsatilmaydi
    if score_a == score_b:
        await message.answer(
            "✅ Test yakunlandi! Rahmat.\n"
            "Siz 50 ga 50 ishladingiz.\n"
            "Natijalar administratorga yuborildi."
        )
    else:
        await message.answer(
            "✅ Test yakunlandi! Rahmat.\n"
            "Natijalar administratorga yuborildi."
        )

    if score_a == score_b:
        result_text = RESULT_A_TEXT + "\n\n" + ("=" * 20) + "\n\n" + RESULT_B_TEXT
        result_title = "⚖️ TENG (50/50) — SPRINTER va MARAFONCHI aralash"
    elif score_a > score_b:
        result_text = RESULT_B_TEXT
        result_title = RESULT_B_TITLE
    else:
        result_text = RESULT_A_TEXT
        result_title = RESULT_A_TITLE

    if ADMIN_CHAT_ID:
        bot: Bot = message.bot
        await bot.send_message(
            ADMIN_CHAT_ID,
            f"📊 Yangi test natijasi:\n"
            f"👤 Ism-familiya: {full_name}\n"
            f"🔗 Telegram: @{user.username or '-'}\n"
            f"A: {score_a} ta | B: {score_b} ta\n"
            f"🏷 Natija: {result_title}\n\n"
            f"{result_text}",
        )


@router.message()
async def fallback(message: Message):
    await message.answer(
        "Testni boshlash uchun /start buyrug'ini yuboring.",
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