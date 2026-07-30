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

# Load Token from Environment Variable
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# --- COMPREHENSIVE COUNTRY LIST (Two-Column Grid Layout) ---
ALL_COUNTRIES = [
    ("AUSTRALIA", "australia"), ("AUSTRIA", "austria"),
    ("BELGIUM", "belgium"), ("BRAZIL", "brazil"),
    ("CANADA", "canada"), ("CAYMAN ISLAND", "cayman_island"),
    ("CHILE", "chile"), ("COLOMBIA", "colombia"),
    ("CROATIA", "croatia"), ("CURACO", "curaco"),
    ("CYPRUS", "cyprus"), ("CZECH REPUBLIC", "czech_republic"),
    ("DENMARK", "denmark"), ("DOMINICAN REPUBLIC", "dominican_republic"),
    ("ECUADOR", "ecuador"), ("ESTONIA", "estonia"),
    ("FINLAND", "finland"), ("FRANCE", "france"),
    ("GERMANY", "germany"), ("GREECE", "greece"),
    ("HONG KONG", "hong_kong"), ("HUNGARY", "hungary"),
    ("ICELAND", "iceland"), ("INDONESIA", "indonesia"),
    ("IRELAND", "ireland"), ("ISRAEL", "israel"),
    ("ITALY", "italy"), ("LATVIA", "latvia"),
    ("LITHUANIA", "lithuania"), ("LUXEMBOURG", "luxembourg"),
    ("MACAO", "macao"), ("MALAYSIA", "malaysia"),
    ("MALTA", "malta"), ("MYANMAR", "myanmar"),
    ("NEPAL", "nepal"), ("NETHERLANDS", "netherlands"),
    ("NEW ZEALAND", "new_zealand"), ("NORWAY", "norway"),
    ("PHILIPPINES", "philippines"), ("POLAND", "poland"),
    ("PORTUGAL", "portugal"), ("ROMANIA", "romania"),
    ("RUSSIA", "russia"), ("SINGAPORE", "singapore"),
    ("SLOVAKIA", "slovakia"), ("SLOVENIA", "slovenia"),
    ("SOUTH AFRICA", "south_africa"), ("SPAIN", "spain"),
    ("SWEDEN", "sweden"), ("SWITZERLAND", "switzerland"),
    ("THAILAND", "thailand"), ("UK", "uk"),
    ("UKRAINE", "ukraine"), ("USA", "usa"),
    ("VIETNAM", "vietnam")
]

# --- CRYPTO EXCHANGES (Single Column List) ---
CRYPTO_EXCHANGES = [
    ("Binance", "binance"),
    ("Bybit", "bybit"),
    ("Coinbase", "coinbase"),
    ("OKX", "okx"),
    ("Upbit", "upbit"),
    ("Bitget", "bitget"),
    ("Kraken", "kraken"),
    ("Kucoin", "kucoin"),
    ("Mexc", "mexc"),
    ("Bitfinex", "bitfinex")
]

# --- STANDARD LEADS PRICING TIERS (Email, SMS, Crypto) ---
PRICING_TIERS = [
    ("1k - £200", "1k_200"),
    ("2k - £380", "2k_380"),
    ("3k - £540", "3k_540"),
    ("4k - £680", "4k_680"),
    ("5k - £800", "5k_800"),
    ("10k - £1500", "10k_1500"),
    ("15k - £2100", "15k_2100"),
    ("20k - £2600", "20k_2600"),
    ("25k - £3000", "25k_3000")
]

# --- CORRECT BANK LEADS PRICING TIERS ---
BANK_PRICING_TIERS = [
    ("1k — £100", "1k_100"),
    ("2k — £180", "2k_180"),
    ("3k — £270", "3k_270"),
    ("4k — £360", "4k_360"),
    ("5k — £425", "5k_425"),
    ("6k — £480", "6k_480"),
    ("7k — £560", "7k_560"),
    ("8k — £600", "8k_600"),
    ("10k — £700", "10k_700"),
    ("15k — £900", "15k_900"),
    ("20k — £1,100", "20k_1100"),
    ("25k — £1,500", "25k_1500"),
    ("30k — £1,700", "30k_1700"),
    ("50k — £2,000", "50k_2000"),
    ("100k — £3,000", "100k_3000")
]

# --- MAJOR BANKS MAPPING BY COUNTRY ---
COUNTRY_BANKS = {
    "uk": [("Barclays", "barclays"), ("HSBC", "hsbc"), ("Lloyds", "lloyds"), ("NatWest", "natwest"), ("Santander", "santander"), ("Halifax", "halifax"), ("Nationwide", "nationwide"), ("Monzo", "monzo"), ("Starling", "starling")],
    "usa": [("Chase", "chase"), ("Bank of America", "bank_of_america"), ("Wells Fargo", "wells_fargo"), ("Citibank", "citibank"), ("Capital One", "capital_one"), ("US Bank", "us_bank"), ("PNC", "pnc"), ("TD Bank", "td_bank")],
    "australia": [("Commonwealth Bank", "commbank"), ("Westpac", "westpac"), ("ANZ", "anz"), ("NAB", "nab")],
    "canada": [("RBC", "rbc"), ("TD Canada Trust", "td"), ("Scotiabank", "scotiabank"), ("BMO", "bmo"), ("CIBC", "cibc")],
    "germany": [("Deutsche Bank", "deutsche"), ("Commerzbank", "commerzbank"), ("Sparkasse", "sparkasse"), ("N26", "n26")],
    "france": [("BNP Paribas", "bnp"), ("Credit Agricole", "credit_agricole"), ("Societe Generale", "socgen")],
    # Default fallback for other countries
    "default": [("National Bank", "national_bank"), ("Commercial Bank", "commercial_bank"), ("Retail Bank", "retail_bank"), ("Digital Bank", "digital_bank")]
}

# --- KEYBOARD BUILDERS ---

def main_menu_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("Email Leads", callback_data="category_email"),
            InlineKeyboardButton("SMS Leads", callback_data="category_sms"),
            InlineKeyboardButton("Crypto Leads", callback_data="category_crypto")
        ],
        [
            InlineKeyboardButton("Bank Leads", callback_data="category_bank"),
            InlineKeyboardButton("Wallet", callback_data="wallet"),
            InlineKeyboardButton("FAQ", callback_data="faq")
        ],
        [
            InlineKeyboardButton("Channel", url="https://t.me/Leadsplug")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def pricing_tiers_keyboard(back_target):
    keyboard = [[InlineKeyboardButton(label, callback_data=f"price_{val}")] for label, val in PRICING_TIERS]
    keyboard.append([InlineKeyboardButton("Back", callback_data=back_target)])
    return InlineKeyboardMarkup(keyboard)

def bank_pricing_tiers_keyboard(back_target):
    keyboard = [[InlineKeyboardButton(label, callback_data=f"bank_price_{val}")] for label, val in BANK_PRICING_TIERS]
    keyboard.append([InlineKeyboardButton("Back", callback_data=back_target)])
    return InlineKeyboardMarkup(keyboard)

def countries_keyboard(prefix, back_target):
    keyboard = []
    for i in range(0, len(ALL_COUNTRIES), 2):
        row = [InlineKeyboardButton(ALL_COUNTRIES[i][0], callback_data=f"{prefix}_{ALL_COUNTRIES[i][1]}")]
        if i + 1 < len(ALL_COUNTRIES):
            row.append(InlineKeyboardButton(ALL_COUNTRIES[i+1][0], callback_data=f"{prefix}_{ALL_COUNTRIES[i+1][1]}"))
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton("Back", callback_data=back_target)])
    return InlineKeyboardMarkup(keyboard)

def banks_keyboard(country_code, back_target):
    banks = COUNTRY_BANKS.get(country_code, COUNTRY_BANKS["default"])
    keyboard = [[InlineKeyboardButton(name, callback_data=f"bank_name_{code}")] for name, code in banks]
    keyboard.append([InlineKeyboardButton("Back", callback_data=back_target)])
    return InlineKeyboardMarkup(keyboard)

def crypto_exchanges_keyboard(back_target):
    keyboard = [[InlineKeyboardButton(name, callback_data=f"crypto_ex_{code}")] for name, code in CRYPTO_EXCHANGES]
    keyboard.append([InlineKeyboardButton("Back", callback_data=back_target)])
    return InlineKeyboardMarkup(keyboard)

# --- HANDLERS ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "Welcome to LeadsPlug.\n\n"
        "Please select an option from the menu below:"
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

    # --- CATEGORY SELECTION ---
    elif data.startswith("category_"):
        cat_type = data.split("_")[1]
        context.user_data['selected_category'] = cat_type

        if cat_type == "bank":
            # Flow: Bank Leads -> Country Selection Menu
            text = "Please select a country:"
            await query.message.edit_text(text, reply_markup=countries_keyboard("bank_country", "main_menu"))
        else:
            # Standard Leads Flow (Email, SMS, Crypto) -> Amount Selection
            text = "Please select the amount of leads you want to purchase:"
            await query.message.edit_text(text, reply_markup=pricing_tiers_keyboard("main_menu"))

    # --- STANDARD LEADS FLOW ---
    elif data.startswith("price_"):
        tier_code = data.split("_")[1]
        context.user_data['selected_tier'] = tier_code
        
        text = "Please select a country:"
        cat_type = context.user_data.get('selected_category', 'crypto')
        await query.message.edit_text(text, reply_markup=countries_keyboard("lead_country", f"category_{cat_type}"))

    elif data.startswith("lead_country_"):
        country_code = data.split("_")[2]
        context.user_data['selected_country'] = country_code
        tier = context.user_data.get('selected_tier', 'package')
        
        text = (
            "Current Balance: £0\n"
            "Please select a crypto option:"
        )
        await query.message.edit_text(text, reply_markup=crypto_exchanges_keyboard(f"price_{tier}"))

    # --- CORRECT BANK LEADS FLOW ---
    elif data.startswith("bank_country_"):
        country_code = data.split("_")[2]
        context.user_data['selected_bank_country'] = country_code
        
        text = f"Please select a major bank for {country_code.upper()}:"
        await query.message.edit_text(text, reply_markup=banks_keyboard(country_code, "category_bank"))

    elif data.startswith("bank_name_"):
        bank_code = data.split("_")[2]
        context.user_data['selected_bank_name'] = bank_code
        
        text = "Please select the amount of bank leads you want to purchase:"
        country = context.user_data.get('selected_bank_country', 'uk')
        # Crucial fix: Passing back to the bank's country list using prefix 'bank_country_' so it loops correctly
        await query.message.edit_text(text, reply_markup=bank_pricing_tiers_keyboard(f"bank_country_{country}"))

    elif data.startswith("bank_price_"):
        tier_code = data.split("_")[1]
        context.user_data['selected_bank_tier'] = tier_code
        
        text = (
            "Current Balance: £0\n"
            "Please select a crypto option:"
        )
        bank_name = context.user_data.get('selected_bank_name', 'bank')
        await query.message.edit_text(text, reply_markup=crypto_exchanges_keyboard(f"bank_name_{bank_name}"))

    # --- CHECKOUT / PAYMENT CONFIRMATION ---
    elif data.startswith("crypto_ex_"):
        exchange_code = data.split("_")[2]
        context.user_data['selected_exchange'] = exchange_code
        
        category = context.user_data.get('selected_category', 'leads')
        exchange = exchange_code.capitalize()

        if category == "bank":
            country = context.user_data.get('selected_bank_country', 'global')
            bank = context.user_data.get('selected_bank_name', 'bank')
            tier = context.user_data.get('selected_bank_tier', 'package')
            back_target = f"bank_name_{bank}"

            text = (
                f"Order Summary\n\n"
                f"Category: BANK LEADS\n"
                f"Country: {country.upper()}\n"
                f"Bank Institution: {bank.upper()}\n"
                f"Package Tier: {tier.upper()} Leads\n"
                f"Payment Method: {exchange}\n\n"
                f"Status: Ready for checkout. Please contact administration to complete payment."
            )
        else:
            tier = context.user_data.get('selected_tier', 'package')
            country = context.user_data.get('selected_country', 'global')
            back_target = f"lead_country_{country}"

            text = (
                f"Order Summary\n\n"
                f"Category: {category.upper()} LEADS\n"
                f"Package: {tier.upper()} Leads\n"
                f"Country: {country.upper()}\n"
                f"Payment Method: {exchange}\n\n"
                f"Status: Ready for checkout. Please contact administration to complete payment."
            )

        keyboard = [
            [InlineKeyboardButton("Back", callback_data=back_target)],
            [InlineKeyboardButton("Main Menu", callback_data="main_menu")]
        ]
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

    # --- WALLET & TOP UP FLOW ---
    elif data == "wallet":
        text = (
            "Current Balance: £0\n\n"
            "Please select a crypto option to top up your balance:"
        )
        await query.message.edit_text(text, reply_markup=crypto_exchanges_keyboard("main_menu"))

    # --- FAQ SECTION ---
    elif data == "faq":
        text = (
            "Frequently Asked Questions\n\n"
            "1. Select your desired leads category from the main menu.\n"
            "2. Choose your target country and specific parameters.\n"
            "3. Complete your transaction via secure crypto payment options."
        )
        keyboard = [[InlineKeyboardButton("Back", callback_data="main_menu")]]
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

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
