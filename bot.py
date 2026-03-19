import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- CONFIGURATION ---
TOKEN = "YOUR_BOT_TOKEN_HERE"
OWNER_ID = 123456789  # @userinfobot vachu un ID-ah inga podu

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Step-by-step details collect panna States
class Booking(StatesGroup):
    choosing_service = State()
    waiting_for_name = State()
    waiting_for_phone = State()

# 1. Start Command & Service Selection
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    kb = [
        [InlineKeyboardButton(text="SEO 🔍", callback_data="svc_SEO")],
        [InlineKeyboardButton(text="Logo Designing 🎨", callback_data="svc_Logo Designing")],
        [InlineKeyboardButton(text="Video Editing 🎬", callback_data="svc_Video Editing")],
        [InlineKeyboardButton(text="Digital Marketing 📈", callback_data="svc_Digital Marketing")]
    ]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=kb)
    
    await message.reply(
        "👋 **Welcome to Brand Network!**\n\nUngaluku entha service venum nu select pannunga:",
        reply_markup=reply_markup
    )
    await state.set_state(Booking.choosing_service)

# 2. Service Selection Handle Pandrathu
@dp.callback_query(F.data.startswith("svc_"))
async def service_selected(callback: types.Callback_query, state: FSMContext):
    service = callback.data.split("_")[1]
    await state.update_data(selected_service=service)
    
    await callback.message.edit_text(f"✅ Selected: **{service}**\n\nIppo unga **Full Name**-ah send pannunga:")
    await state.set_state(Booking.waiting_for_name)

# 3. Name vangurathu
@dp.message(Booking.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(user_name=message.text)
    await message.reply("Super! Ippo unga **Phone Number**-ah kudunga:")
    await state.set_state(Booking.waiting_for_phone)

# 4. Final Step: Phone Number & Owner Log
@dp.message(Booking.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    phone = message.text
    service = user_data['selected_service']
    name = user_data['user_name']
    username = f"@{message.from_user.username}" if message.from_user.username else "No Username"

    # User-ku message
    await message.reply("🚀 **Booking Request Sent!**\nNamba team ungala seekiram contact pannuvanga. Thanks!")

    # OWNER-KU DM LOG (Main Feature)
    log_text = (
        "📩 **NEW BOOKING LOG**\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"👤 **Name:** {name}\n"
        f"📞 **Phone:** {phone}\n"
        f"📂 **Service:** {service}\n"
        f"🔗 **User:** {username}\n"
        f"🆔 **ID:** `{message.from_user.id}`\n"
        "━━━━━━━━━━━━━━━━━━"
    )
    
    await bot.send_message(OWNER_ID, log_text)
    await state.clear() # Reset state for next booking

# Bot Run panna
async def main():
    print("Bot is Running...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

