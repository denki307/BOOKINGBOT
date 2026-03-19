import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- CONFIGURATION (Heroku Config Vars moolama varum) ---
TOKEN = os.getenv("BOT_TOKEN")
# OWNER_ID default ah 0 nu vachuruken, Heroku-la un ID kudukanum
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

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
    # User-ku image venumna send_photo kooda use pannalam
    kb = [
        [InlineKeyboardButton(text="SEO 🔍", callback_data="svc_SEO")],
        [InlineKeyboardButton(text="Logo Designing 🎨", callback_data="svc_Logo Designing")],
        [InlineKeyboardButton(text="Video Editing 🎬", callback_data="svc_Video Editing")],
        [InlineKeyboardButton(text="Digital Marketing 📈", callback_data="svc_Digital Marketing")],
        [InlineKeyboardButton(text="Content Creation ✍️", callback_data="svc_Content Creation")]
    ]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=kb)
    
    await message.reply(
        "👋 **Welcome to Brand Network!**\n\nNamba services moolama unga brand-ah reach panna vaikalam. Entha service venum nu select pannunga:",
        reply_markup=reply_markup
    )
    await state.set_state(Booking.choosing_service)

# 2. Service Selection Handle
@dp.callback_query(F.data.startswith("svc_"))
async def service_selected(callback: types.Callback_query, state: FSMContext):
    service = callback.data.split("_")[1]
    await state.update_data(selected_service=service)
    
    await callback.message.edit_text(
        f"✅ Selected: **{service}**\n\nIppo unga **Full Name**-ah send pannunga:"
    )
    await state.set_state(Booking.waiting_for_name)

# 3. Name Collection
@dp.message(Booking.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(user_name=message.text)
    await message.reply("Super! Ippo unga **Phone Number**-ah kudunga (With Country Code):")
    await state.set_state(Booking.waiting_for_phone)

# 4. Final Step: Phone Number & Owner Log
@dp.message(Booking.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    phone = message.text
    service = user_data.get('selected_service')
    name = user_data.get('user_name')
    username = f"@{message.from_user.username}" if message.from_user.username else "No Username"

    # User Confirmation
    await message.reply(
        "🚀 **Booking Request Sent!**\n\nUnga details namba team-ku poiduchu. Seekiram ungala contact pannuvom. Thanks for choosing **Brand Network**!"
    )

    # OWNER-KU DM LOG
    if OWNER_ID != 0:
        log_text = (
            "🔥 **NEW BOOKING RECEIVED!**\n"
            "━━━━━━━━━━━━━━━━━━\n"
            f"👤 **Name:** {name}\n"
            f"📞 **Phone:** {phone}\n"
            f"📂 **Service:** {service}\n"
            f"🔗 **User Profile:** {username}\n"
            f"🆔 **User ID:** `{message.from_user.id}`\n"
            "━━━━━━━━━━━━━━━━━━"
        )
        try:
            await bot.send_message(OWNER_ID, log_text)
        except Exception as e:
            print(f"Error sending log to owner: {e}")
            
    await state.clear()

# Main Entry Point
async def main():
    print("🚀 Brand Network Bot is Starting on Heroku...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
