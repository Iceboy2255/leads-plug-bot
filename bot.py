import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from datetime import datetime

# --- CRASH-PROOF & ZERO TERMINAL LOGS CONFIGURATION ---
logging.basicConfig(level=logging.CRITICAL)
logger = logging.getLogger(__name__)

# Load Token from Environment Variable
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# --- ADMIN CONFIGURATION ---
ADMIN_TELEGRAM_ID = 7280810198
ADMIN_GROUP_ID = -1003907566721
COMMAND_PASSWORD = "myprince"

# --- GLOBAL SYSTEM STATES ---
BOT_ACTIVE = True
USER_DATABASE = set()
ORDER_COUNTER = 928172
INVENTORY_STOCK = {
    "default": 25,
    "Leads Bundle A": 15,
    "Leads Bundle B": 5
}
PAYMENT_RECORDS = set()
ACTIVE_ORDERS = {}
BROADCAST_STATE = set()

# In-memory storage for user join dates
USER_JOIN_DATES = {}

# --- HUMAN CHAT-STYLE LOG HELPER ---
async def send_log_to_group(bot, log_text: str):
    try:
        await bot.send_message(
            chat_id=ADMIN_GROUP_ID,
            text=log_text
        )
    except Exception:
        pass

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

LEDGER_COUNTRIES = [
    ("United Kingdom", "uk"), ("United States", "usa"),
    ("Canada", "canada"), ("Australia", "australia"),
    ("Germany", "germany"), ("France", "france"),
    ("Netherlands", "netherlands"), ("Sweden", "sweden")
]

HARDWARE_DEVICES = [
    ("Blockstream Jade", "blockstream_jade"), ("SafePal S1", "safepal_s1"),
    ("SafePal X1", "safepal_x1"), ("Tangem Card", "tangem_card"),
    ("Tangem Ring", "tangem_ring"), ("CoolWallet Pro", "coolwallet_pro"),
    ("CoolWallet S", "coolwallet_s"), ("OneKey Classic", "onekey_classic"),
    ("Ledger Flex", "ledger_flex"), ("Ledger Stax", "ledger_stax"),
    ("Trezor Model One", "trezor_model_one"), ("Trezor Safe 3", "trezor_safe_3"),
    ("Trezor Safe 5", "trezor_safe_5"), ("ELLIPAL Titan 2.0", "ellipal_titan_2"),
    ("ELLIPAL Titan Mini", "ellipal_titan_mini"), ("Keystone 3 Pro", "keystone_3_pro"),
    ("Ledger Nano S Plus", "ledger_nano_s_plus"), ("Ledger Nano X", "ledger_nano_x")
]

LEDGER_DEVICE_PRICING_TIERS = [
    ("1k = £350", "1k_350"), ("2k = £600", "2k_600"), ("3k = £800", "3k_800"),
    ("4k = £950", "4k_950"), ("5k = £1,100", "5k_1100"), ("10k = £1,800", "10k_1800"),
    ("15k = £2,400", "15k_2400"), ("20k = £2,900", "20k_2900"), ("25k = £3,300", "25k_3300")
]

CRYPTO_EXCHANGES = [
    ("Binance", "binance"), ("Bybit", "bybit"), ("Coinbase", "coinbase"),
    ("OKX", "okx"), ("Upbit", "upbit"), ("Bitget", "bitget"),
    ("Kraken", "kraken"), ("Kucoin", "kucoin"), ("Mexc", "mexc"), ("Bitfinex", "bitfinex")
]

PAYMENT_WALLETS = [
    ("BTC", "btc", "bc1q6cyn934d3vlmgyghr6znnqyl3j4hluk883h70a"),
    ("ETH", "eth", "0x44ceA102871A7270785585909a4eBe13A157D614"),
    ("USDT", "usdt", "TVYa8uBeMZem8MwePaVii5PjEydrK3e8it"),
    ("LTC", "ltc", "LgHLihB2f48nh13F7Byu8yiEAVRhuBMEXL")
]

WALLET_ADDRESSES = {code: addr for _, code, addr in PAYMENT_WALLETS}

PRICING_TIERS = [
    ("1k - £200", "1k_200"), ("2k - £380", "2k_380"), ("3k - £540", "3k_540"),
    ("4k - £680", "4k_680"), ("5k - £800", "5k_800"), ("10k - £1500", "10k_1500"),
    ("15k - £2100", "15k_2100"), ("20k - £2600", "20k_2600"), ("25k - £3000", "25k_3000")
]

SMS_FEMALE_PRICING_TIERS = [
    ("1K - £45", "1k_45"), ("2K - £69", "2k_69"), ("3K - £87", "3k_87"),
    ("4K - £105", "4k_105"), ("5K - £115", "5k_115"), ("10K - £175", "10k_175"),
    ("15K - £255", "15k_255"), ("20K - £315", "2k_315"), ("25k - £375", "25k_375"),
    ("30k - £455", "30k_455"), ("35k - £505", "35k_505"), ("40k - £535", "40k_535"),
    ("45k - £555", "45k_555"), ("50k - £575", "50k_575"), ("100k - £715", "100k_715"),
    ("200k - £1015", "200k_1015"), ("500k - £1615", "500k_1615"), ("1M - £2015", "1m_2015")
]

SMS_MALE_PRICING_TIERS = [
    ("1K - £30", "1k_30"), ("2K - £54", "2k_54"), ("3K - £72", "3k_72"),
    ("4K - £90", "4k_90"), ("5K - £100", "5k_100"), ("10K - £160", "10k_160"),
    ("15K - £240", "15k_240"), ("20K - £300", "20k_300"), ("25k - £360", "25k_360"),
    ("30k - £440", "30k_440"), ("35k - £490", "35k_490"), ("40k - £520", "40k_520"),
    ("45k - £540", "45k_540"), ("50k - £560", "50k_560"), ("100k - £700", "100k_700"),
    ("200k - £1000", "200k_1000"), ("500k - £1600", "500k_1600"), ("1M - £2000", "1m_2000")
]

BANK_PRICING_TIERS = [
    ("1k — £100", "1k_100"), ("2k — £180", "2k_180"), ("3k — £270", "3k_270"),
    ("4k — £360", "4k_360"), ("5k — £425", "5k_425"), ("6k — £480", "6k_480"),
    ("7k — £560", "7k_560"), ("8k — £600", "8k_600"), ("10k — £700", "10k_700"),
    ("15k — £900", "15k_900"), ("20k — £1,100", "20k_1100"), ("25k — £1,500", "25k_1500"),
    ("30k — £1,700", "30k_1700"), ("50k — £2,000", "50k_2000"), ("100k — £3,000", "100k_3000")
]

EMAIL_PRICING_TIERS = [
    ("1K — £40", "1k_40"), ("5K — £250", "5k_250"), ("10K — £400", "10k_400"),
    ("25K — £750", "25k_750"), ("50K — £850", "50k_850"), ("75K — £1,450", "75k_1450"),
    ("100K — £2,650", "100k_2650"), ("250K — £4,150", "250k_4150"), ("500K — £7,450", "500k_7450"),
    ("750K — £9,950", "750k_9950"), ("1M — £13,950", "1m_13950")
]

EMAIL_CATEGORIES = [
    ("Business", "business"), ("Crypto", "crypto"), ("Gaming", "gaming"),
    ("Music", "music"), ("Shopping", "shopping"), ("Social Media", "social_media")
]

EMAIL_SUBCATEGORIES = {
    "business": [
        ("E-commerce Owners", "ecommerce_owners"), ("Real Estate Investors", "real_estate_investors"),
        ("Small Business Owners", "small_business_owners"), ("Dropshippers", "dropshippers"),
        ("Agency Owners", "agency_owners"), ("Consultants & Coaches", "consultants_coaches"),
        ("Startup Founders", "startup_founders"), ("Import/Export Businesses", "import_export_businesses"),
        ("Local Service Businesses", "local_service_businesses"), ("B2B Companies", "b2b_companies")
    ],
    "crypto": [
        ("Binance", "binance"), ("Coinbase", "coinbase"), ("Kraken", "kraken"),
        ("Bybit", "bybit"), ("OKX", "okx"), ("KuCoin", "kucoin"),
        ("Bitstamp", "bitstamp"), ("Gate.io", "gate_io"), ("Gemini", "gemini"), ("MEXC", "mexc")
    ],
    "gaming": [
        ("eSports Players", "esports_players"), ("Casino/Betting Users", "casino_betting_users"), ("Gaming Communities", "gaming_communities")
    ],
    "music": [
        ("Apple Music Users", "apple_music_users"), ("Spotify Users", "spotify_users")
    ],
    "shopping": [
        ("Online Shoppers", "online_shoppers"), ("Amazon Users", "amazon_users"),
        ("Shopify Customers", "shopify_customers"), ("Subscription Buyers", "subscription_buyers")
    ],
    "social_media": [
        ("Instagram Users", "instagram_users"), ("TikTok Users", "tiktok_users"),
        ("Twitter (X) Users", "twitter_users"), ("Facebook Users", "facebook_users"),
        ("LinkedIn Users", "linkedin_users"), ("YouTube Users", "youtube_users")
    ]
}

categories = EMAIL_SUBCATEGORIES

COUNTRY_BANKS = {
    "australia": [
        ("Commonwealth Bank", "commonwealth_bank"), ("Westpac Bank", "westpac_bank"), ("ANZ Bank", "anz_bank"),
        ("National Australia Bank", "national_australia_bank"), ("Macquarie Bank", "macquarie_bank"), ("Bendigo Bank", "bendigo_bank")
    ],
    "uk": [
        ("HSBC", "hsbc"), ("Barclays", "barclays"), ("Lloyds Bank", "lloyds_bank"), ("NatWest", "natwest"),
        ("Santander UK", "santander_uk"), ("TSB Bank", "tsb_bank"), ("Starling Bank", "starling_bank"), ("Monzo Bank", "monzo_bank")
    ],
    "usa": [
        ("JPMorgan Chase", "jpmorgan_chase"), ("Bank of America", "bank_of_america"), ("Wells Fargo", "wells_fargo"),
        ("Citibank", "citibank"), ("Capital One", "capital_one"), ("Ally Bank", "ally_bank")
    ],
    "default": [
        ("National Bank", "national_bank"), ("Commercial Bank", "commercial_bank"), ("Retail Bank", "retail_bank")
    ]
}

# --- KEYBOARD BUILDERS ---

def main_menu_keyboard(user_id=None):
    keyboard = [
        [
            InlineKeyboardButton("Email Leads", callback_data="category_email"),
            InlineKeyboardButton("Aged SMS Leads", callback_data="category_sms"),
            InlineKeyboardButton("Crypto Leads", callback_data="category_crypto")
        ],
        [
            InlineKeyboardButton("Bank Leads", callback_data="category_bank"),
            InlineKeyboardButton("Wallet", callback_data="wallet"),
            InlineKeyboardButton("FAQ", callback_data="faq")
        ],
        [
            InlineKeyboardButton("Channel", url="https://t.me/Leadssplugv3")
        ]
    ]
    if user_id == ADMIN_TELEGRAM_ID:
        keyboard.insert(0, [InlineKeyboardButton("📊 Admin Panel", callback_data="admin_panel")])
    return InlineKeyboardMarkup(keyboard)

def admin_panel_keyboard():
    keyboard = [
        [InlineKeyboardButton("📊 Dashboard", callback_data="adm_dash"), InlineKeyboardButton("📦 Orders", callback_data="adm_orders")],
        [InlineKeyboardButton("👥 Users", callback_data="adm_users"), InlineKeyboardButton("💰 Revenue", callback_data="adm_revenue")],
        [InlineKeyboardButton("📢 Broadcast", callback_data="adm_bc")],
        [InlineKeyboardButton("🟢 Start Bot", callback_data="adm_start"), InlineKeyboardButton("🔴 Stop Bot", callback_data="adm_stop")],
        [InlineKeyboardButton("⬅️ Back", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def crypto_leads_home_keyboard(back_target):
    keyboard = [
        [
            InlineKeyboardButton("Crypto Exchange Leads", callback_data="crypto_sub_exchange"),
            InlineKeyboardButton("Ledger Device Leads", callback_data="crypto_sub_ledger")
        ],
        [
            InlineKeyboardButton("Back", callback_data=back_target)
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def pricing_tiers_keyboard(back_target):
    keyboard = [[InlineKeyboardButton(label, callback_data=f"price_{val}")] for label, val in PRICING_TIERS]
    keyboard.append([InlineKeyboardButton("Back", callback_data=back_target)])
    return InlineKeyboardMarkup(keyboard)

def ledger_device_pricing_keyboard(back_target):
    keyboard = [[InlineKeyboardButton(label, callback_data=f"ledger_price_{val}")] for label, val in LEDGER_DEVICE_PRICING_TIERS]
    keyboard.append([InlineKeyboardButton("Back", callback_data=back_target)])
    return InlineKeyboardMarkup(keyboard)

def sms_pricing_tiers_keyboard(gender, back_target):
    tiers = SMS_FEMALE_PRICING_TIERS if gender == "female" else SMS_MALE_PRICING_TIERS
    keyboard = [[InlineKeyboardButton(label, callback_data=f"sms_price_{gender}_{val}")] for label, val in tiers]
    keyboard.append([InlineKeyboardButton("Back", callback_data=back_target)])
    return InlineKeyboardMarkup(keyboard)

def sms_gender_keyboard(back_target):
    keyboard = [
        [
            InlineKeyboardButton("Female", callback_data="sms_gender_female"),
            InlineKeyboardButton("Male", callback_data="sms_gender_male")
        ],
        [
            InlineKeyboardButton("Back", callback_data=back_target)
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def bank_pricing_tiers_keyboard(back_target):
    keyboard = [[InlineKeyboardButton(label, callback_data=f"bank_price_{val}")] for label, val in BANK_PRICING_TIERS]
    keyboard.append([InlineKeyboardButton("Back", callback_data=back_target)])
    return InlineKeyboardMarkup(keyboard)

def email_pricing_tiers_keyboard(back_target):
    keyboard = [[InlineKeyboardButton(label, callback_data=f"email_price_{val}")] for label, val in EMAIL_PRICING_TIERS]
    keyboard.append([InlineKeyboardButton("Back", callback_data=back_target)])
    return InlineKeyboardMarkup(keyboard)

def email_categories_keyboard(back_target):
    keyboard = [[InlineKeyboardButton(name, callback_data=f"email_cat_{code}")] for name, code in EMAIL_CATEGORIES]
    keyboard.append([InlineKeyboardButton("Back", callback_data=back_target)])
    return InlineKeyboardMarkup(keyboard)

def email_subcategories_keyboard(subcats, back_target):
    keyboard = [[InlineKeyboardButton(name, callback_data=f"email_sub_{code}")] for name, code in subcats]
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

def ledger_countries_keyboard(back_target):
    keyboard = []
    for i in range(0, len(LEDGER_COUNTRIES), 2):
        row = [InlineKeyboardButton(LEDGER_COUNTRIES[i][0], callback_data=f"ledger_country_{LEDGER_COUNTRIES[i][1]}")]
        if i + 1 < len(LEDGER_COUNTRIES):
            row.append(InlineKeyboardButton(LEDGER_COUNTRIES[i+1][0], callback_data=f"ledger_country_{LEDGER_COUNTRIES[i+1][1]}"))
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton("Back", callback_data=back_target)])
    return InlineKeyboardMarkup(keyboard)

def hardware_devices_keyboard(back_target):
    keyboard = []
    for i in range(0, len(HARDWARE_DEVICES), 2):
        row = [InlineKeyboardButton(HARDWARE_DEVICES[i][0], callback_data=f"ledger_device_{HARDWARE_DEVICES[i][1]}")]
        if i + 1 < len(HARDWARE_DEVICES):
            row.append(InlineKeyboardButton(HARDWARE_DEVICES[i+1][0], callback_data=f"ledger_device_{HARDWARE_DEVICES[i+1][1]}"))
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

def wallet_page_keyboard(back_target):
    keyboard = [
        [InlineKeyboardButton("BTC", callback_data="pay_btc"), InlineKeyboardButton("ETH", callback_data="pay_eth")],
        [InlineKeyboardButton("USDT", callback_data="pay_usdt"), InlineKeyboardButton("LTC", callback_data="pay_ltc")],
        [InlineKeyboardButton("I PAID", callback_data="verify_payment")],
        [InlineKeyboardButton("Back", callback_data=back_target)]
    ]
    return InlineKeyboardMarkup(keyboard)

def topup_keyboard(back_target):
    keyboard = [
        [InlineKeyboardButton("£50", callback_data="topup_50"), InlineKeyboardButton("£100", callback_data="topup_100")],
        [InlineKeyboardButton("£150", callback_data="topup_150"), InlineKeyboardButton("£200", callback_data="topup_200")],
        [InlineKeyboardButton("£250", callback_data="topup_250"), InlineKeyboardButton("£300", callback_data="topup_300")],
        [InlineKeyboardButton("£350", callback_data="topup_350"), InlineKeyboardButton("£400", callback_data="topup_400")],
        [InlineKeyboardButton("£450", callback_data="topup_450"), InlineKeyboardButton("£500", callback_data="topup_500")],
        [InlineKeyboardButton("£750", callback_data="topup_750"), InlineKeyboardButton("£1000", callback_data="topup_1000")],
        [InlineKeyboardButton("Custom Amount", callback_data="topup_custom")],
        [InlineKeyboardButton("Back", callback_data=back_target)]
    ]
    return InlineKeyboardMarkup(keyboard)

# --- CORE HANDLERS ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user:
        USER_DATABASE.add(user.id)
        if user.id not in USER_JOIN_DATES:
            USER_JOIN_DATES[user.id] = datetime.now().strftime("%m-%d-%Y")

    # Start / Stop Check
    if not BOT_ACTIVE and user and user.id != ADMIN_TELEGRAM_ID:
        if update.callback_query:
            await update.callback_query.answer("Bot temporarily unavailable", show_alert=True)
        else:
            await update.message.reply_text("Bot temporarily unavailable")
        return

    if user and user.id != ADMIN_TELEGRAM_ID:
        uname = f"@{user.username}" if user.username else f"{user.first_name} ({user.id})"
        await send_log_to_group(
            context.bot,
            f"{uname} just started the bot"
        )

    welcome_text = (
        "Welcome to LeadsPlug.\n\n"
        "Please select an option from the menu below:"
    )
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.message.edit_text(welcome_text, reply_markup=main_menu_keyboard(user.id if user else None))
    else:
        await update.message.reply_text(welcome_text, reply_markup=main_menu_keyboard(user.id if user else None))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user = update.effective_user

    if user:
        USER_DATABASE.add(user.id)
        if user.id not in USER_JOIN_DATES:
            USER_JOIN_DATES[user.id] = datetime.now().strftime("%m-%d-%Y")

    # Start / Stop Check
    global BOT_ACTIVE, ORDER_COUNTER
    if not BOT_ACTIVE and data != "admin_panel" and not data.startswith("adm_") and user.id != ADMIN_TELEGRAM_ID:
        await query.edit_message_text("Bot temporarily unavailable")
        return

    uname = f"@{user.username}" if user.username else f"{user.first_name}"
    user_identifier = f"{uname} ({user.id})"

    if user.id != ADMIN_TELEGRAM_ID or not data.startswith("adm_"):
        await send_log_to_group(context.bot, f"{user_identifier} clicked {data}")

    if data == "main_menu":
        await start(update, context)

    # --- ADMIN PANEL LOGIC ---
    elif data == "admin_panel":
        if user.id != ADMIN_TELEGRAM_ID:
            await query.edit_message_text("❌ Unauthorized access.")
            return
        await query.edit_message_text("🔒 **Admin Control Panel**", reply_markup=admin_panel_keyboard(), parse_mode="Markdown")

    elif data == "adm_start":
        if user.id == ADMIN_TELEGRAM_ID:
            BOT_ACTIVE = True
            await send_log_to_group(context.bot, f"{user_identifier} started the bot")
            await query.edit_message_text("🟢 Bot status changed to: ACTIVE", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_panel")]]))

    elif data == "adm_stop":
        if user.id == ADMIN_TELEGRAM_ID:
            BOT_ACTIVE = False
            await send_log_to_group(context.bot, f"{user_identifier} stopped the bot")
            await query.edit_message_text("🔴 Bot status changed to: STOPPED", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_panel")]]))

    elif data == "adm_dash":
        if user.id == ADMIN_TELEGRAM_ID:
            dash_text = (
                f"📊 **Dashboard Statistics**\n\n"
                f"• Status: {'🟢 Active' if BOT_ACTIVE else '🔴 Stopped'}\n"
                f"• Registered Users: {len(USER_DATABASE)}\n"
                f"• Stock Available: {INVENTORY_STOCK.get('default', 25)}\n"
                f"• Total Orders: {ORDER_COUNTER - 928172}"
            )
            await query.edit_message_text(dash_text, parse_mode="Markdown", reply_markup=admin_panel_keyboard())

    elif data == "adm_orders":
        if user.id == ADMIN_TELEGRAM_ID:
            orders_summary = f"📦 **Active Tracked Orders**\nTotal Processed: {ORDER_COUNTER - 928172}\nRecent state synchronized."
            await query.edit_message_text(orders_summary, parse_mode="Markdown", reply_markup=admin_panel_keyboard())

    elif data == "adm_users":
        if user.id == ADMIN_TELEGRAM_ID:
            await query.edit_message_text(f"👥 **Total Unique Users:** {len(USER_DATABASE)}", parse_mode="Markdown", reply_markup=admin_panel_keyboard())

    elif data == "adm_revenue":
        if user.id == ADMIN_TELEGRAM_ID:
            revenue_calc = (ORDER_COUNTER - 928172) * 50.00
            await query.edit_message_text(f"💰 **Estimated Revenue:** £{revenue_calc:.2f}", parse_mode="Markdown", reply_markup=admin_panel_keyboard())

    elif data == "adm_bc":
        if user.id == ADMIN_TELEGRAM_ID:
            BROADCAST_STATE.add(user.id)
            await query.edit_message_text("📢 **Broadcast Mode:** Please send the message you want to broadcast to all users.", parse_mode="Markdown", reply_markup=admin_panel_keyboard())

    # --- SMART STOCK & ORDER CREATION TRIGGER ---
    elif data.startswith(("price_", "ledger_price_", "sms_price_", "bank_price_", "email_price_")):
        if INVENTORY_STOCK.get("default", 25) <= 0:
            await send_log_to_group(context.bot, f"{user_identifier} tried to buy fullz, but no credits")
            await query.edit_message_text("Out of stock")
            return

        ORDER_COUNTER += 1
        order_id = f"ORD-{ORDER_COUNTER}"
        
        context.user_data['current_order_id'] = order_id
        context.user_data['order_time'] = datetime.now()

        product_name = data.split("_")[0]
        context.user_data['order_product'] = product_name

        await send_log_to_group(
            context.bot,
            f"{user_identifier} created order #{order_id} for {product_name} (Global) - £50+"
        )

        # Route to wallet selection
        tier_parts = data.split("_")
        back_target = "main_menu"
        if product_name == "price":
            country = context.user_data.get('selected_crypto_country', 'uk')
            back_target = f"crypto_country_{country}"
        elif product_name == "ledger":
            device_code = context.user_data.get('selected_ledger_device', 'ledger_nano_x')
            back_target = f"ledger_device_{device_code}"
        elif product_name == "sms":
            gender = tier_parts[1] if len(tier_parts) > 1 else "female"
            back_target = f"sms_gender_{gender}"
        elif product_name == "bank":
            bank_name = context.user_data.get('selected_bank_name', 'bank')
            back_target = f"bank_name_{bank_name}"
        elif product_name == "email":
            subcat_code = context.user_data.get('selected_email_subcat', 'ecommerce_owners')
            back_target = f"email_sub_{subcat_code}"

        text = (
            "==============================\n"
            "💳 **Select Payment Wallet**\n"
            "==============================\n\n"
            "Please choose your preferred cryptocurrency to complete the payment.\n\n"
            "<i>Minimum deposit: £50</i>"
        )
        await query.message.edit_text(text, reply_markup=wallet_page_keyboard(back_target), parse_mode="HTML")

    elif data == "verify_payment":
        order_id = context.user_data.get('current_order_id')
        if not order_id or user.id not in ACTIVE_ORDERS and order_id not in [o.get("id") for o in ACTIVE_ORDERS.values()]:
            pass

        await send_log_to_group(context.bot, f"{user_identifier} clicked \"I PAID\" for order #{order_id}")

        payment_signature = f"{order_id}-{user.id}"
        if payment_signature in PAYMENT_RECORDS:
            await query.edit_message_text(
                "❌ Payment not detected or incorrect\n"
                "Please send exact amount to correct wallet and try again"
            )
            return

        PAYMENT_RECORDS.add(payment_signature)
        chosen_crypto = context.user_data.get('selected_crypto', 'BTC')

        await send_log_to_group(
            context.bot,
            f"{user_identifier} payment confirmed for order #{order_id} ({chosen_crypto})"
        )

        # Smart Stock Reduction
        if INVENTORY_STOCK.get("default", 25) > 0:
            INVENTORY_STOCK["default"] -= 1

        file_name = "verified_leads_export.csv"
        await send_log_to_group(context.bot, f"{user_identifier} received file for order #{order_id}")

        await query.edit_message_text("✅ Payment confirmed. Your leads have been delivered.")
        await context.bot.send_document(
            chat_id=user.id,
            document=b"email,phone,name\nlead1@example.com,+123456789,John Doe",
            filename=file_name
        )

    # --- CATEGORY SELECTION ---
    elif data.startswith("category_"):
        cat_type = data.split("_")[1]
        context.user_data['selected_category'] = cat_type
        await send_log_to_group(context.bot, f"{user_identifier} is browsing through {cat_type}")

        if cat_type == "bank":
            text = "Please select a country:"
            await query.message.edit_text(text, reply_markup=countries_keyboard("bank_country", "main_menu"))
        elif cat_type == "email":
            text = "Please select a country:"
            await query.message.edit_text(text, reply_markup=countries_keyboard("email_country", "main_menu"))
        elif cat_type == "crypto":
            text = "Please select an option:"
            await query.message.edit_text(text, reply_markup=crypto_leads_home_keyboard("main_menu"))
        elif cat_type == "sms":
            text = "Please select a country:"
            await query.message.edit_text(text, reply_markup=countries_keyboard("sms_country", "main_menu"))
        else:
            text = "Please select an option:"
            await query.message.edit_text(text, reply_markup=main_menu_keyboard(user.id))

    # --- CRYPTO LEADS SUB-MENU FLOW ---
    elif data == "crypto_sub_exchange":
        text = "Please select a crypto exchange:"
        await query.message.edit_text(text, reply_markup=crypto_exchanges_keyboard("category_crypto"))

    elif data == "crypto_sub_ledger":
        text = "Please select a country:"
        await query.message.edit_text(text, reply_markup=ledger_countries_keyboard("category_crypto"))

    elif data.startswith("ledger_country_"):
        country_code = data.split("_")[2]
        context.user_data['selected_ledger_country'] = country_code
        text = "Please select a hardware wallet device:"
        await query.message.edit_text(text, reply_markup=hardware_devices_keyboard("crypto_sub_ledger"))

    elif data.startswith("ledger_device_"):
        device_code = data.split("_")[2]
        context.user_data['selected_ledger_device'] = device_code
        text = "Please select the amount of leads you want to purchase:"
        await query.message.edit_text(text, reply_markup=ledger_device_pricing_keyboard(f"ledger_country_{context.user_data.get('selected_ledger_country', 'uk')}"))

    # --- EMAIL LEADS FLOW ---
    elif data.startswith("email_country_"):
        country_code = data.split("_")[2]
        context.user_data['selected_email_country'] = country_code
        text = "Please select an email leads category:"
        await query.message.edit_text(text, reply_markup=email_categories_keyboard("category_email"))

    elif data.startswith("email_cat_"):
        cat_code = "_".join(data.split("_")[2:])
        context.user_data['selected_email_category'] = cat_code
        subcategories = categories.get(cat_code, [])
        text = "Select Social Media Lead Type" if cat_code == "social_media" else "Please select a subcategory:"
        back_target = f"email_country_{context.user_data.get('selected_email_country', 'uk')}"
        await query.message.edit_text(text, reply_markup=email_subcategories_keyboard(subcategories, back_target))

    elif data.startswith("email_sub_"):
        subcat_code = "_".join(data.split("_")[2:])
        context.user_data['selected_email_subcat'] = subcat_code
        text = "Please select the amount of leads you want to purchase:"
        cat_code = context.user_data.get('selected_email_category', 'business')
        back_target = f"email_cat_{cat_code}"
        await query.message.edit_text(text, reply_markup=email_pricing_tiers_keyboard(back_target))

    # --- CRYPTO EXCHANGE LEADS FLOW ---
    elif data.startswith("crypto_ex_"):
        exchange_code = data.split("_")[2]
        context.user_data['selected_exchange'] = exchange_code
        text = "Please select a country:"
        await query.message.edit_text(text, reply_markup=countries_keyboard("crypto_country", "crypto_sub_exchange"))

    elif data.startswith("crypto_country_"):
        country_code = data.split("_")[2]
        context.user_data['selected_crypto_country'] = country_code
        text = "Please select the amount of leads you want to purchase:"
        await query.message.edit_text(text, reply_markup=pricing_tiers_keyboard(f"crypto_ex_{context.user_data.get('selected_exchange', 'binance')}"))

    # --- AGED SMS LEADS FLOW ---
    elif data.startswith("sms_country_"):
        country_code = data.split("_")[2]
        context.user_data['selected_country'] = country_code
        text = "Please select gender:"
        await query.message.edit_text(text, reply_markup=sms_gender_keyboard("category_sms"))

    elif data.startswith("sms_gender_"):
        gender = data.split("_")[2]
        context.user_data['selected_gender'] = gender
        text = "Please select the amount of leads you want to purchase:"
        country = context.user_data.get('selected_country', 'uk')
        await query.message.edit_text(text, reply_markup=sms_pricing_tiers_keyboard(gender, f"sms_country_{country}"))

    # --- BANK LEADS FLOW ---
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
        await query.message.edit_text(text, reply_markup=bank_pricing_tiers_keyboard(f"bank_country_{country}"))

    # --- WALLET & TOP UP FLOW ---
    elif data == "wallet":
        user_id_val = query.from_user.id
        join_date = USER_JOIN_DATES.get(user_id_val, datetime.now().strftime("%m-%d-%Y"))
        await send_log_to_group(context.bot, f"{user_identifier} opened the wallet")
        text = (
            "==================================\n"
            f"🪪 ID: {user_id_val}\n"
            f"💰 Balance: £0.00\n"
            f"🗓 Join Date: {join_date}\n"
            "==================================\n\n"
            "Select a top-up amount below:\n"
            "<i>Minimum top-up: £50</i>"
        )
        await query.message.edit_text(text, reply_markup=topup_keyboard("main_menu"), parse_mode="HTML")

    elif data.startswith("topup_"):
        amount = data.split("_")[1]
        await send_log_to_group(context.bot, f"{user_identifier} opened the topup page for £{amount}")
        wallet_addr = WALLET_ADDRESSES.get("btc", "bc1q6cyn934d3vlmgyghr6znnqyl3j4hluk883h70a")
        text = (
            f"Top-up Amount: £{amount}\n\n"
            f"BTC Wallet Address:\n`{wallet_addr}`\n\n"
            f"<i>Minimum top-up: £50</i>"
        )
        await query.message.edit_text(text, reply_markup=wallet_page_keyboard("wallet"), parse_mode="HTML")

    elif data.startswith("pay_"):
        coin = data.split("_")[1].upper()
        context.user_data['selected_crypto'] = coin
        wallet_addr = WALLET_ADDRESSES.get(coin.lower(), "N/A")
        text = (
            "==============================\n"
            f"**{coin} Payment Wallet**\n"
            "==============================\n\n"
            "Send the required amount to the address below:\n\n"
            f"`{wallet_addr}`\n\n"
            "<i>Minimum deposit: £50</i>"
        )
        await query.message.edit_text(text, reply_markup=wallet_page_keyboard("wallet"), parse_mode="HTML")

    # --- FAQ SECTION ---
    elif data == "faq":
        text = (
            "📌 **FAQ**\n\n"
            "1. Select your desired leads category from the main menu.\n"
            "2. Choose your target country and specific parameters.\n"
            "3. Complete your transaction via secure crypto payment options.\n"
            "4. Contact support for custom or fresh lead requests (data can be generated on demand).\n\n"
            "📊 **Services Information:**\n\n"
            "• SMS Send Outs – 100% landing rate\n"
            "• Email Blast Services available\n"
            "• Crypto & Bank SID (No Spam)\n\n"
            "📞 **Support:**\n\n"
            "Official Bot Support: @Leadsplugv3"
        )
        keyboard = [[InlineKeyboardButton("Back", callback_data="main_menu")]]
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

# --- BROADCAST SYSTEM & PASSWORD AUTH HANDLER ---
async def text_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text

    if not user:
        return

    if text == COMMAND_PASSWORD and user.id == ADMIN_TELEGRAM_ID:
        await update.message.reply_text("🔓 Password accepted. Admin Access Granted.")
        return

    if user.id == ADMIN_TELEGRAM_ID and user.id in BROADCAST_STATE:
        BROADCAST_STATE.remove(user.id)
        success_count = 0
        for target_id in USER_DATABASE:
            try:
                await context.bot.send_message(chat_id=target_id, text=f"📢 **Announcement:**\n\n{text}", parse_mode="Markdown")
                success_count += 1
            except Exception:
                pass
        await update.message.reply_text(f"✅ Broadcast successfully sent to {success_count} users.")
        return

def main():
    if not TOKEN:
        return

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_message_handler))

    application.run_polling()

if __name__ == "__main__":
    main()