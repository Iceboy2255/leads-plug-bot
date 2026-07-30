
import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load Token from Environment Variable (Railway config)
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# --- KEYBOARDS ---

def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("📧 Email Leads", callback_data="email_leads"),
         InlineKeyboardButton("📱 SMS Leads", callback_data="sms_leads")],
        [InlineKeyboardButton("🪙 Crypto Leads", callback_data="crypto_leads")],
        [InlineKeyboardButton("💰 Wallet", callback_data="wallet"),
         InlineKeyboardButton("❓ FAQ", callback_data="faq")]
    ]
    return InlineKeyboardMarkup(keyboard)

def email_countries_keyboard():
    countries = [
        ("Australia", "au"), ("Brazil", "br"),
        ("Canada", "ca"), ("France", "fr"),
        ("Germany", "de"), ("Hungary", "hu"),
        ("Italy", "it"), ("Spain", "es"),
        ("UK", "uk"), ("USA", "us")
    ]
    keyboard = [[InlineKeyboardButton(name, callback_data=f"email_country_{code}")] for name, code in countries]
    keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="main_menu")])
    return InlineKeyboardMarkup(keyboard)

def email_categories_keyboard(country_name):
    categories = [
        ("🪙 Crypto Exchanges", "crypto_ex"),
        ("🏦 Banks & Financial", "banks"),
        ("🏢 Business Registries", "biz_reg"),
        ("📡 Mobile Networks", "mobile"),
        ("🔗 Ledgers & Nodes", "ledgers")
    ]
    keyboard = [[InlineKeyboardButton(name, callback_data=f"email_cat_{code}")] for name, code in categories]
    keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="email_leads")])
    return InlineKeyboardMarkup(keyboard)

# --- HANDLERS ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "Welcome to @Leadsplug!\n\n"
        "Tap 'Email Leads' or 'SMS Leads' to browse inventories.\n"
        "Tap 'Wallet' to check balance or 'FAQ' for help."
    )
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.message.edit_text(welcome_text, reply_markup=main_menu_keyboard())
    else:
        await update.message.reply_text(welcome_text, reply_markup=main_menu_keyboard())

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "main_menu":
        await start(update, context)

    elif data == "email_leads":
        text = "Current Balance: £0\n\nPlease select a country:"
        await query.message.edit_text(text, reply_markup=email_countries_keyboard())

    elif data.startswith("email_country_"):
        country_code = data.split("_")[2].upper()
        context.user_data['selected_country'] = country_code
        text = f"Country: 🇺🇸 {country_code}\nStock: 225,575,000 total records\n\nSelect a category:"
        await query.message.edit_text(text, reply_markup=email_categories_keyboard(country_code))

    elif data == "sms_leads":
        await query.message.edit_text("SMS Leads module coming online...", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Back", callback_data="main_menu")]
        ]))

    elif data == "wallet":
        await query.message.edit_text("Your current balance is £0. Top up features via backend.", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Back", callback_data="main_menu")]
        ]))

    elif data == "faq":
        await query.message.edit_text("FAQs:\n1. How to buy? Select leads -> confirm -> pay.", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Back", callback_data="main_menu")]
        ]))

def main():
    if not TOKEN:
        logger.error("No TELEGRAM_BOT_TOKEN found in environment variables!")
        return

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))

    application.run_polling()

if __name__ == "__main__":
    main()
