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
import hashlib
import sqlite3
import time

# --- CRASH-PROOF & ZERO TERMINAL LOGS CONFIGURATION ---
logging.basicConfig(level=logging.CRITICAL)
logger = logging.getLogger(__name__)

# Load Token from Environment Variable
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# --- ADMIN CONFIGURATION ---
ADMIN_TELEGRAM_ID = 7280810198
ADMIN_GROUP_ID = -1003907566721
COMMAND_PASSWORD = "myprince"

# Secure hash for the admin command password (SHA-256 of "myprince")
COMMAND_PASSWORD_HASH = hashlib.sha256(COMMAND_PASSWORD.encode()).hexdigest()

# --- DATABASE SETUP & HELPERS ---
DB_NAME = 'bot_users.db'

def init_db():
    """Initializes the SQLite database and creates tables if they don't exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            joined_at TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS balances (
            user_id INTEGER PRIMARY KEY,
            balance REAL DEFAULT 0.0
        )
    ''')
    conn.commit()
    conn.close()

def save_user(user_id, username=None):
    """Saves a user to SQLite database permanently."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    join_date = datetime.now().strftime("%m-%d-%Y")
    cursor.execute('''
        INSERT OR IGNORE INTO users (user_id, username, joined_at)
        VALUES (?, ?, ?)
    ''', (user_id, username, join_date))
    conn.commit()
    conn.close()

def get_all_user_ids():
    """Fetches all stored user IDs from the SQLite database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users")
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]

def get_user_ids_by_filter(filter_type="all"):
    """Fetches user IDs based on timeframe (all, today)."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    today_str = datetime.now().strftime("%m-%d-%Y")
    
    if filter_type == "today":
        cursor.execute("SELECT user_id FROM users WHERE joined_at = ?", (today_str,))
    else:
        cursor.execute("SELECT user_id FROM users")
        
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]

def get_user_count():
    """Returns total unique user count."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    conn.close()
    return count

def is_user_exists(user_id):
    """Checks if user exists in database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

def get_user_join_date(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT joined_at FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row and row[0] else datetime.now().strftime("%m-%d-%Y")

def get_user_balance(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM balances WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else 0.0

def set_user_balance(user_id, amount):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO balances (user_id, balance) VALUES (?, ?)
        ON CONFLICT(user_id) DO UPDATE SET balance = ?
    ''', (user_id, amount, amount))
    conn.commit()
    conn.close()

# Initialize Database immediately
init_db()

# --- GLOBAL SYSTEM STATES ---
BOT_ACTIVE = True
ORDER_COUNTER = 928172
INVENTORY_STOCK = {
    "default": 25,
    "Leads Bundle A": 15,
    "Leads Bundle B": 5
}
PAYMENT_RECORDS = set()
ACTIVE_ORDERS = {}
BROADCAST_STATE = set()

# --- HELPER FOR CRYPTO AMOUNTS ---
def calculate_crypto_amount(gbp_val, coin):
    rates = {"BTC": 60000.0, "ETH": 2500.0, "LTC": 70.0, "USDT": 1.0}
    rate = rates.get(coin, 1.0)
    try:
        val = float(gbp_val) / rate
    except Exception:
        val = 50.0 / rate
    
    if coin == "BTC":
        return f"{val:.5f}"
    elif coin == "ETH":
        return f"{val:.4f}"
    elif coin == "LTC":
        return f"{val:.3f}"
    else:
        return f"{val:.2f}"

def get_small_unit(coin, amount_str):
    try:
        val = float(amount_str)
        if coin == "BTC":
            return f"({int(val * 100000000)} sats)"
        elif coin == "ETH":
            return f"({int(val * 1000000000000000000)} wei)"
        elif coin == "LTC":
            return f"({int(val * 100000000)} litoshis)"
        else:
            return f"({int(val * 100)} cents)"
    except Exception:
        return "(units)"

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
    ("Kraken", "kraken"), ("Kucoin", "kucoin"), ("MEXC", "mexc"), ("Bitfinex", "bitfinex"),
    ("Crypto.com", "crypto_com"), ("Gate.io", "gate_io"), ("HTX", "htx"),
    ("Gemini", "gemini"), ("Bitstamp", "bitstamp"), ("CoinW", "coinw"),
    ("BingX", "bingx"), ("Phemex", "phemex"), ("BitMart", "bitmart"),
    ("LBank", "lbank"), ("WhiteBIT", "whitebit"), ("CoinEx", "coinex"),
    ("XT.COM", "xt_com"), ("Deepcoin", "deepcoin"), ("Toobit", "toobit"),
    ("BTCC", "btcc"), ("AscendEX", "ascendex"), ("Poloniex", "poloniex"),
    ("Bitrue", "bitrue"), ("ProBit Global", "probit_global"), ("Coinstore", "coinstore"),
    ("DigiFinex", "digifinex"), ("Bitunix", "bitunix"), ("WEEX", "weex"),
    ("BloFin", "blofin"), ("Bitso", "bitso"), ("Mercado Bitcoin", "mercado_bitcoin"),
    ("Coincheck", "coincheck"), ("bitFlyer", "bitflyer"), ("Zaif", "zaif"),
    ("Bithumb", "bithumb"), ("Korbit", "korbit"), ("GOPAX", "gopax"),
    ("Coinone", "coinone"), ("Independent Reserve", "independent_reserve"),
    ("BTC Markets", "btc_markets"), ("Swyftx", "swyftx"), ("CoinSpot", "coinspot"),
    ("NDAX", "ndax"), ("Bitbuy", "bitbuy")
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
    ("15K - £240", "15k_240"), ("20K - £300", "2k_300"), ("25k - £360", "25k_360"),
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
    "uk": [
        ("HSBC UK", "hsbc_uk"), ("Barclays", "barclays"), ("Lloyds Bank", "lloyds_bank"),
        ("NatWest", "natwest"), ("Santander UK", "santander_uk"), ("Halifax", "halifax"),
        ("Nationwide", "nationwide"), ("Royal Bank of Scotland", "royal_bank_of_scotland"),
        ("TSB", "tsb"), ("Metro Bank", "metro_bank"), ("Monzo", "monzo"),
        ("Starling Bank", "starling_bank"), ("Virgin Money", "virgin_money"),
        ("Co-operative Bank", "co_operative_bank"), ("Bank of Scotland", "bank_of_scotland"),
        ("First Direct", "first_direct"), ("Chase UK", "chase_uk"), ("Kroo", "kroo"),
        ("Revolut", "revolut"), ("Wise", "wise"), ("BBVA", "bbva"), ("Zopa Bank Ltd.", "zopa_bank_ltd")
    ],
    "usa": [
        ("JPMorgan Chase", "jpmorgan_chase"), ("Bank of America", "bank_of_america"),
        ("Wells Fargo", "wells_fargo"), ("Citibank", "citibank"), ("U.S. Bank", "us_bank"),
        ("PNC Bank", "pnc_bank"), ("Truist Bank", "truist_bank"), ("Capital One", "capital_one"),
        ("TD Bank", "td_bank"), ("BMO Bank", "bmo_bank"), ("Citizens Bank", "citizens_bank"),
        ("Fifth Third Bank", "fifth_third_bank"), ("KeyBank", "keybank"), ("Huntington Bank", "huntington_bank"),
        ("Regions Bank", "regions_bank"), ("M&T Bank", "mt_bank"), ("Ally Bank", "ally_bank"),
        ("Discover Bank", "discover_bank"), ("Navy Federal Credit Union", "navy_federal_credit_union"),
        ("Goldman Sachs Bank USA", "goldman_sachs_bank_usa")
    ],
    "australia": [
        ("Commonwealth Bank", "commonwealth_bank"), ("Westpac Bank", "westpac_bank"), ("ANZ Bank", "anz_bank"),
        ("National Australia Bank", "national_australia_bank"), ("Macquarie Bank", "macquarie_bank"), ("Bendigo Bank", "bendigo_bank")
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
            InlineKeyboardButton("Aged Leads", callback_data="category_sms"),
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
        [InlineKeyboardButton("📢 Broadcast (All Users)", callback_data="adm_bc"), InlineKeyboardButton("📢 Broadcast (Today)", callback_data="adm_bc_today")],
        [InlineKeyboardButton("🟢 Start Bot", callback_data="adm_start"), InlineKeyboardButton("🔴 Stop Bot", callback_data="adm_stop")],
        [InlineKeyboardButton("⬅️ Back", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def crypto_leads_home_keyboard(back_target):
    keyboard = [
        [
            InlineKeyboardButton("Crypto Exchange Leads", callback_data="crypto_sub_exchange_page_0"),
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

def sms_pricing_tiers_keyboard(gender, age_range, back_target):
    tiers = SMS_FEMALE_PRICING_TIERS if gender == "female" else SMS_MALE_PRICING_TIERS
    keyboard = [[InlineKeyboardButton(label, callback_data=f"sms_price_{gender}_{age_range}_{val}")] for label, val in tiers]
    keyboard.append([InlineKeyboardButton("Back", callback_data=back_target)])
    return InlineKeyboardMarkup(keyboard)

def sms_gender_keyboard(back_target):
    keyboard = [
        [
            InlineKeyboardButton("Female Leads", callback_data="sms_gender_female"),
            InlineKeyboardButton("Male Leads", callback_data="sms_gender_male")
        ],
        [
            InlineKeyboardButton("Back", callback_data=back_target)
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def sms_age_ranges_keyboard(gender, back_target):
    age_ranges = [
        ("18–24", "18_24"), ("25–34", "25_34"), ("35–44", "35_44"), ("45–54", "45_54"),
        ("55–64", "55_64"), ("65–74", "65_74"), ("75–84", "75_84"), ("85–94", "85_94")
    ]
    keyboard = []
    for i in range(0, len(age_ranges), 2):
        row = [InlineKeyboardButton(age_ranges[i][0], callback_data=f"sms_age_{gender}_{age_ranges[i][1]}")]
        if i + 1 < len(age_ranges):
            row.append(InlineKeyboardButton(age_ranges[i+1][0], callback_data=f"sms_age_{gender}_{age_ranges[i+1][1]}"))
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton("Back", callback_data=back_target)])
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

def crypto_exchanges_keyboard(page=0, back_target="category_crypto"):
    page_size = 10
    total_exchanges = len(CRYPTO_EXCHANGES)
    total_pages = (total_exchanges + page_size - 1) // page_size
    
    if page < 0:
        page = 0
    elif page >= total_pages:
        page = total_pages - 1
        
    start_idx = page * page_size
    end_idx = min(start_idx + page_size, total_exchanges)
    
    keyboard = []
    for i in range(start_idx, end_idx):
        name, code = CRYPTO_EXCHANGES[i]
        keyboard.append([InlineKeyboardButton(name, callback_data=f"crypto_ex_{code}")])
        
    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"crypto_sub_exchange_page_{page - 1}"))
    if page < total_pages - 1:
        nav_row.append(InlineKeyboardButton("Next ➡️", callback_data=f"crypto_sub_exchange_page_{page + 1}"))
        
    if nav_row:
        keyboard.append(nav_row)
        
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
        username = user.username or "NoUsername"
        save_user(user.id, username)

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
        username = user.username or "NoUsername"
        save_user(user.id, username)

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
                f"• Registered Users: {get_user_count()}\n"
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
            await query.edit_message_text(f"👥 **Total Unique Users:** {get_user_count()}", parse_mode="Markdown", reply_markup=admin_panel_keyboard())

    elif data == "adm_revenue":
        if user.id == ADMIN_TELEGRAM_ID:
            revenue_calc = (ORDER_COUNTER - 928172) * 50.00
            await query.edit_message_text(f"💰 **Estimated Revenue:** £{revenue_calc:.2f}", parse_mode="Markdown", reply_markup=admin_panel_keyboard())

    elif data == "adm_bc":
        if user.id == ADMIN_TELEGRAM_ID:
            BROADCAST_STATE.add(user.id)
            context.user_data['broadcast_filter'] = 'all'
            await query.edit_message_text("📢 **Broadcast Mode (All Users - New & Old):** Please send the message you want to broadcast.", parse_mode="Markdown", reply_markup=admin_panel_keyboard())

    elif data == "adm_bc_today":
        if user.id == ADMIN_TELEGRAM_ID:
            BROADCAST_STATE.add(user.id)
            context.user_data['broadcast_filter'] = 'today'
            await query.edit_message_text("📢 **Broadcast Mode (Today's Users):** Please send the message you want to broadcast.", parse_mode="Markdown", reply_markup=admin_panel_keyboard())

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

        selected_crypto = context.user_data.get('selected_crypto', 'BTC')
        wallet_addr = WALLET_ADDRESSES.get(selected_crypto.lower(), WALLET_ADDRESSES['btc'])
        crypto_amt = calculate_crypto_amount(50, selected_crypto)

        text = (
            f"Send exactly {crypto_amt} {selected_crypto} to the address below to get 50 credits\n\n"
            f"{wallet_addr}\n\n"
            "IMPORTANT:\n"
            "!! Deposits are refundable (terms may apply)\n"
            f"!! Double check the {selected_crypto} amount before sending\n"
            "!! Anything UNDER or ABOVE the exact amount may delay processing\n"
            "!! You will be funded after network confirmation\n"
            "!! By sending, you agree to these terms\n"
            f"!! DO NOT send in £ — send ONLY in {selected_crypto}"
        )
        back_target = "main_menu"
        await query.message.edit_text(text, reply_markup=wallet_page_keyboard(back_target))

    elif data == "verify_payment":
        order_id = context.user_data.get('current_order_id', 'UNKNOWN')
        await send_log_to_group(context.bot, f"{uname} clicked \"I PAID\" for order #{order_id}")

        waiting_text = (
            "⏳ Payment submitted for review.\n\n"
            "Our team is verifying your transaction.\n"
            "You will be credited shortly."
        )
        await query.message.edit_text(waiting_text)

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
    elif data.startswith("crypto_sub_exchange_page_"):
        page_num = int(data.split("_")[-1])
        text = "Please select a crypto exchange:"
        await query.message.edit_text(text, reply_markup=crypto_exchanges_keyboard(page=page_num, back_target="category_crypto"))

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
        exchange_code = "_".join(data.split("_")[2:])
        context.user_data['selected_exchange'] = exchange_code
        text = "Please select a country:"
        await query.message.edit_text(text, reply_markup=countries_keyboard("crypto_country", "crypto_sub_exchange_page_0"))

    elif data.startswith("crypto_country_"):
        country_code = data.split("_")[2]
        context.user_data['selected_crypto_country'] = country_code
        text = "Please select the amount of leads you want to purchase:"
        await query.message.edit_text(text, reply_markup=pricing_tiers_keyboard(f"crypto_ex_{context.user_data.get('selected_exchange', 'binance')}"))

    # --- AGED LEADS FLOW ---
    elif data.startswith("sms_country_"):
        country_code = data.split("_")[2]
        context.user_data['selected_country'] = country_code
        text = "Please select gender:"
        await query.message.edit_text(text, reply_markup=sms_gender_keyboard("category_sms"))

    elif data.startswith("sms_gender_"):
        gender = data.split("_")[2]
        context.user_data['selected_gender'] = gender
        text = "Please select an age range:"
        country = context.user_data.get('selected_country', 'uk')
        await query.message.edit_text(text, reply_markup=sms_age_ranges_keyboard(gender, f"sms_country_{country}"))

    elif data.startswith("sms_age_"):
        parts = data.split("_")
        gender = parts[2]
        age_range = "_".join(parts[3:])
        context.user_data['selected_age_range'] = age_range
        text = "Please select the amount of leads you want to purchase:"
        await query.message.edit_text(text, reply_markup=sms_pricing_tiers_keyboard(gender, age_range, f"sms_gender_{gender}"))

    # --- BANK LEADS FLOW ---
    elif data.startswith("bank_country_"):
        country_code = data.split("_")[2]
        context.user_data['selected_bank_country'] = country_code
        text = f"Please select a major bank for {country_code.upper()}:"
        await query.message.edit_text(text, reply_markup=banks_keyboard(country_code, "category_bank"))

    elif data.startswith("bank_name_"):
        bank_code = data.split("_")[2:]
        bank_code_str = "_".join(bank_code)
        context.user_data['selected_bank_name'] = bank_code_str
        text = "Please select the amount of bank leads you want to purchase:"
        country = context.user_data.get('selected_bank_country', 'uk')
        await query.message.edit_text(text, reply_markup=bank_pricing_tiers_keyboard(f"bank_country_{country}"))

    # --- WALLET & TOP UP FLOW ---
    elif data == "wallet":
        user_id_val = query.from_user.id
        join_date = get_user_join_date(user_id_val)
        current_bal = get_user_balance(user_id_val)
        await send_log_to_group(context.bot, f"{user_identifier} opened the wallet")
        text = (
            "==================================\n"
            f"🪪 ID: {user_id_val}\n"
            f"💰 Balance: £{current_bal:.2f}\n"
            f"🗓 Join Date: {join_date}\n"
            "==================================\n\n"
            "Select a top-up amount below:\n"
            "<i>Minimum top-up: £50</i>"
        )
        await query.message.edit_text(text, reply_markup=topup_keyboard("main_menu"), parse_mode="HTML")

    elif data.startswith("topup_"):
        amount = data.split("_")[1]
        context.user_data['topup_amount'] = amount
        await send_log_to_group(context.bot, f"{user_identifier} opened the topup page for £{amount}")
        
        selected_crypto = context.user_data.get('selected_crypto', 'BTC')
        wallet_addr = WALLET_ADDRESSES.get(selected_crypto.lower(), WALLET_ADDRESSES['btc'])
        crypto_amt = calculate_crypto_amount(amount, selected_crypto)

        text = (
            f"Send exactly {crypto_amt} {selected_crypto} to the address below to get {amount} credits\n\n"
            f"{wallet_addr}\n\n"
            "IMPORTANT:\n"
            "!! Deposits are refundable (terms may apply)\n"
            f"!! Double check the {selected_crypto} amount before sending\n"
            "!! Anything UNDER or ABOVE the exact amount may delay processing\n"
            "!! You will be funded after network confirmation\n"
            "!! By sending, you agree to these terms\n"
            f"!! DO NOT send in £ — send ONLY in {selected_crypto}"
        )
        await query.message.edit_text(text, reply_markup=wallet_page_keyboard("wallet"))

    elif data.startswith("pay_"):
        coin = data.split("_")[1].upper()
        context.user_data['selected_crypto'] = coin
        wallet_addr = WALLET_ADDRESSES.get(coin.lower(), "N/A")
        amount = context.user_data.get('topup_amount', '50')
        crypto_amt = calculate_crypto_amount(amount, coin)

        text = (
            f"Send exactly {crypto_amt} {coin} to the address below to get {amount} credits\n\n"
            f"{wallet_addr}\n\n"
            "IMPORTANT:\n"
            "!! Deposits are refundable (terms may apply)\n"
            f"!! Double check the {coin} amount before sending\n"
            "!! Anything UNDER or ABOVE the exact amount may delay processing\n"
            "!! You will be funded after network confirmation\n"
            "!! By sending, you agree to these terms\n"
            f"!! DO NOT send in £ — send ONLY in {coin}"
        )
        await query.message.edit_text(text, reply_markup=wallet_page_keyboard("wallet"))

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

# --- ADMIN MANUAL CONFIRM COMMAND ---
async def confirm_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user or user.id != ADMIN_TELEGRAM_ID:
        return

    args = context.args
    if len(args) < 3:
        await update.message.reply_text("❌ Usage: /confirm {user_id} {amount} {crypto}")
        return

    try:
        target_user_id = int(args[0])
        amount = float(args[1])
        crypto = args[2].upper()
    except ValueError:
        await update.message.reply_text("❌ Invalid format. Use numbers for user_id and amount.")
        return

    if not is_user_exists(target_user_id):
        save_user(target_user_id)

    current_bal = get_user_balance(target_user_id) + amount
    set_user_balance(target_user_id, current_bal)

    success_msg = (
        "✅ Payment confirmed. Your account has been funded.\n\n"
        f"Amount Added: £{amount:.2f}\n\n"
        f"Your Balance: £{current_bal:.2f}"
    )

    attached_file = update.message.document or update.message.photo or update.message.audio or update.message.video

    try:
        await context.bot.send_message(chat_id=target_user_id, text=success_msg)
        if attached_file:
            if update.message.document:
                file_id = update.message.document.file_id
                await context.bot.send_document(chat_id=target_user_id, document=file_id)
            elif update.message.photo:
                file_id = update.message.photo[-1].file_id
                await context.bot.send_photo(chat_id=target_user_id, photo=file_id)
        await update.message.reply_text(f"✅ Successfully confirmed payment and credited user {target_user_id} with £{amount:.2f}")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Credited user balance, but failed to send message/file to user: {e}")

# --- ADMIN COMMAND: /userbal ---
async def userbal_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user or user.id != ADMIN_TELEGRAM_ID:
        await update.message.reply_text("❌ Unauthorized access.")
        return

    args = context.args
    if len(args) < 3:
        await update.message.reply_text("❌ Usage: /userbal {user_id} {amount} {password}")
        return

    try:
        target_user_id = int(args[0])
        amount = float(args[1])
        password_input = args[2]
    except ValueError:
        await update.message.reply_text("❌ Invalid format. User ID and amount must be numeric.")
        return

    input_hash = hashlib.sha256(password_input.encode()).hexdigest()
    if input_hash != COMMAND_PASSWORD_HASH:
        await update.message.reply_text("❌ Incorrect password.")
        return

    if amount < 0:
        await update.message.reply_text("❌ Amount cannot be negative.")
        return

    set_user_balance(target_user_id, amount)
    if not is_user_exists(target_user_id):
        save_user(target_user_id)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    audit_log_text = (
        f"📋 **Audit Log: Balance Update**\n"
        f"• Admin ID: {user.id}\n"
        f"• Target User ID: {target_user_id}\n"
        f"• New Balance Set: £{amount:.2f}\n"
        f"• Timestamp: {timestamp}"
    )
    await send_log_to_group(context.bot, audit_log_text)

    user_msg = f"✅ Balance update: £{amount:g} has been added to your balance."
    try:
        await context.bot.send_message(chat_id=target_user_id, text=user_msg)
    except Exception as e:
        await update.message.reply_text(f"⚠️ Balance updated successfully, but failed to notify user: {e}")
        return

    admin_confirmation = (
        "✅ Balance updated successfully\n\n"
        f"User ID: {target_user_id}\n"
        f"Amount: £{amount:g}"
    )
    await update.message.reply_text(admin_confirmation)

# --- ADMIN COMMAND: /senduser ---
async def senduser_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user or user.id != ADMIN_TELEGRAM_ID:
        await update.message.reply_text("❌ Unauthorized access.")
        return

    args = context.args
    if len(args) < 2:
        await update.message.reply_text("❌ Usage: /senduser {user_id} {message}")
        return

    try:
        target_user_id = int(args[0])
    except ValueError:
        await update.message.reply_text("❌ Invalid User ID. Must be a numeric Telegram ID.")
        return

    message_text = " ".join(args[1:])

    try:
        await context.bot.send_message(chat_id=target_user_id, text=message_text)
        await update.message.reply_text("✅ Message sent successfully.")
    except Exception as e:
        await update.message.reply_text(f"❌ Failed to send message to user {target_user_id}. Error: {e}")

# --- ADMIN COMMAND: /sendalluser ---
async def sendalluser_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user or user.id != ADMIN_TELEGRAM_ID:
        await update.message.reply_text("❌ Unauthorized access.")
        return

    args = context.args
    if not args:
        await update.message.reply_text("❌ Usage: /sendalluser {your message here}")
        return

    message_text = " ".join(args)
    all_users = get_all_user_ids()
    success_count = 0
    fail_count = 0

    for target_id in all_users:
        try:
            await context.bot.send_message(
                chat_id=target_id, 
                text=f"📢 **Announcement:**\n\n{message_text}", 
                parse_mode="Markdown"
            )
            success_count += 1
            time.sleep(0.04) # Rate limit protection to prevent Telegram API blocks
        except Exception:
            fail_count += 1

    await update.message.reply_text(
        f"✅ Broadcast complete.\n\n"
        f"• Successfully sent: {success_count}\n"
        f"• Failed (blocked/inactive): {fail_count}"
    )

# --- ADMIN COMMAND: /sendtoday ---
async def sendtoday_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user or user.id != ADMIN_TELEGRAM_ID:
        await update.message.reply_text("❌ Unauthorized access.")
        return

    args = context.args
    if not args:
        await update.message.reply_text("❌ Usage: /sendtoday {your message here}")
        return

    message_text = " ".join(args)
    today_users = get_user_ids_by_filter("today")
    success_count = 0
    fail_count = 0

    for target_id in today_users:
        try:
            await context.bot.send_message(
                chat_id=target_id, 
                text=f"📢 **Announcement:**\n\n{message_text}", 
                parse_mode="Markdown"
            )
            success_count += 1
            time.sleep(0.04)
        except Exception:
            fail_count += 1

    await update.message.reply_text(
        f"✅ Broadcast to today's new users complete.\n\n"
        f"• Successfully sent: {success_count}\n"
        f"• Failed: {fail_count}"
    )

# --- BROADCAST SYSTEM & PASSWORD AUTH HANDLER ---
async def text_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text

    if not user:
        return

    input_hash = hashlib.sha256(text.encode()).hexdigest()
    if input_hash == COMMAND_PASSWORD_HASH and user.id == ADMIN_TELEGRAM_ID:
        await update.message.reply_text("🔓 Password accepted. Admin Access Granted.")
        return

    if user.id == ADMIN_TELEGRAM_ID and user.id in BROADCAST_STATE:
        BROADCAST_STATE.remove(user.id)
        filter_type = context.user_data.get('broadcast_filter', 'all')
        target_users = get_user_ids_by_filter(filter_type)
        
        success_count = 0
        for target_id in target_users:
            try:
                await context.bot.send_message(chat_id=target_id, text=f"📢 **Announcement:**\n\n{text}", parse_mode="Markdown")
                success_count += 1
                time.sleep(0.04)
            except Exception:
                pass
        
        target_label = "today's users" if filter_type == "today" else "all users (new & old)"
        await update.message.reply_text(f"✅ Broadcast successfully sent to {success_count} ({target_label}).")
        return

def main():
    if not TOKEN:
        return

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("confirm", confirm_command))
    application.add_handler(CommandHandler("userbal", userbal_command))
    application.add_handler(CommandHandler("senduser", senduser_command))
    application.add_handler(CommandHandler("sendalluser", sendalluser_command))
    application.add_handler(CommandHandler("sendtoday", sendtoday_command))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_message_handler))
    application.run_polling()

if __name__ == "__main__":
    main()



