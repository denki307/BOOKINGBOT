import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery # <--- Fixed import here

# --- CONFIGURATION ---
TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

bot = Bot(token=TOKEN)
dp = Dispatcher()

class Booking(StatesGroup):
    choosing_service = State()
    waiting_for_name = State()
    waiting_for_phone = State()

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    kb = [
        [InlineKeyboardButton(text="SEO 🔍", callback_data="svc_SEO")],
        [InlineKeyboardButton(text="Logo Designing 🎨", callback_data="svc_Logo Designing")],
        [InlineKeyboardButton(text="Video Editing 🎬", callback_data="svc_Video Editing")],
        [InlineKeyboardButton(text="Digital Marketing 📈", callback_data="svc_Digital Marketing")]
    ]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=kb)
    await message.reply("👋 **Welcome to Brand Network!**\n\nSelect a service:", reply_markup=reply_markup)
    await state.set_state(Booking.choosing_service)

# --- FIXED THIS LINE BELOW (CallbackQuery) ---
@dp.callback_query(F.data.startswith("svc_"))
async def service_selected(callback: CallbackQuery, state: FSMContext):
    service = callback.data.split("_")[1]
    await state.update_data(selected_service=service)
    await callback.message.edit_text(f"✅ Selected: **{service}**\n\nIppo unga **Full Name**-ah send pannunga:")
    await state.set_state(Booking.waiting_for_name)

@dp.message(Booking.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(user_name=message.text)
    await message.reply("Super! Ippo unga **Phone Number**-ah kudunga:")
    await state.set_state(Booking.waiting_for_phone)

@dp.message(Booking.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    phone = message.text
    service = user_data.get('selected_service')
    name = user_data.get('user_name')
    username = f"@{message.from_user.username}" if message.from_user.username else "No Username"

    await message.reply("🚀 **Booking Request Sent!**")

    if OWNER_ID != 0:
        log_text = (
            "🔥 **NEW BOOKING!**\n"
            f"👤 Name: {name}\n"
            f"📞 Phone: {phone}\n"
            f"📂 Service: {service}\n"
            f"🔗 User: {username}"
        )
        await bot.send_message(OWNER_ID, log_text)
    await state.clear()

async def main():
    print("Bot is Starting...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
