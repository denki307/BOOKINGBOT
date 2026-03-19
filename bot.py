import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

# --- CONFIGURATION ---
TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", "8516457288"))

# --- LINKS & ASSETS ---
START_IMAGE = "https://graph.org/file/eb34c7fe13246dbe38ff4-2a6c67002ce93021ce.jpg"
SUPPORT_LINK = "https://t.me/TheBrandNetwork_Official"
CHANNEL_LINK = "https://t.me/BrandNetwork_DM"
OWNER_LINK = "tg://user?id=8516457288"

bot = Bot(token=TOKEN)
dp = Dispatcher()

class Booking(StatesGroup):
    choosing_service = State()
    waiting_for_name = State()
    waiting_for_phone = State()

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    kb = [
        [
            InlineKeyboardButton(text="SEO 🔍", callback_data="svc_SEO"),
            InlineKeyboardButton(text="Logo Designing 🎨", callback_data="svc_Logo Designing")
        ],
        [
            InlineKeyboardButton(text="Video Editing 🎬", callback_data="svc_Video Editing"),
            InlineKeyboardButton(text="Digital Marketing 📈", callback_data="svc_Digital Marketing")
        ],
        [InlineKeyboardButton(text="Content Creation 🎥", callback_data="svc_Content Creation")],
        [
            InlineKeyboardButton(text="Owner 👑", url=OWNER_LINK),
            InlineKeyboardButton(text="Support 🛠️", url=SUPPORT_LINK)
        ],
        [InlineKeyboardButton(text="Join Our Channel 📢", url=CHANNEL_LINK)]
    ]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=kb)
    
    # Sending Image with Caption
    await message.answer_photo(
        photo=START_IMAGE,
        caption=(
            "👋 **Welcome to Brand Network!**\n\n"
            "We help you scale your brand with professional services. "
            "Please select a service below to start your booking:"
        ),
        reply_markup=reply_markup
    )
    await state.set_state(Booking.choosing_service)

@dp.callback_query(F.data.startswith("svc_"))
async def service_selected(callback: CallbackQuery, state: FSMContext):
    service = callback.data.split("_")[1]
    await state.update_data(selected_service=service)
    
    # Using delete and send new message or editing caption
    await callback.message.delete()
    await callback.message.answer(
        f"✅ Selected Service: **{service}**\n\nPlease enter your **Full Name**:"
    )
    await state.set_state(Booking.waiting_for_name)

@dp.message(Booking.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(user_name=message.text)
    await message.reply("Great! Now please provide your **Phone Number**:")
    await state.set_state(Booking.waiting_for_phone)

@dp.message(Booking.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    phone = message.text
    service = user_data.get('selected_service')
    name = user_data.get('user_name')
    username = f"@{message.from_user.username}" if message.from_user.username else "No Username"

    await message.reply(
        "🚀 **Booking Request Sent Successfully!**\n\n"
        "Our team will contact you shortly. Thank you for choosing **Brand Network**!"
    )

    if OWNER_ID != 0:
        log_text = (
            "🔥 **NEW BOOKING ALERT!**\n"
            "━━━━━━━━━━━━━━━━━━\n"
            f"👤 **Name:** {name}\n"
            f"📞 **Phone:** {phone}\n"
            f"📂 **Service:** {service}\n"
            f"🔗 **User:** {username}\n"
            f"🆔 **ID:** `{message.from_user.id}`\n"
            "━━━━━━━━━━━━━━━━━━"
        )
        try:
            await bot.send_message(OWNER_ID, log_text)
        except Exception as e:
            print(f"Log Error: {e}")
            
    await state.clear()

async def main():
    print("🚀 Brand Network Bot is live with Image Support!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
