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

# --- CRYPTO EXCHANGES (Single Column List) for General Wallet Top-Up Only ---
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

# --- PAYMENT WALLETS (BTC, ETH, USDT, LTC) ---
PAYMENT_WALLETS = [
    ("BTC", "btc"),
    ("ETH", "eth"),
    ("USDT", "usdt"),
    ("LTC", "ltc")
]

# --- STANDARD LEADS PRICING TIERS (SMS, Crypto) ---
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

# --- BANK LEADS PRICING TIERS ---
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

# --- EMAIL LEADS PRICING TIERS ---
EMAIL_PRICING_TIERS = [
    ("1K — £40", "1k_40"),
    ("5K — £250", "5k_250"),
    ("10K — £400", "10k_400"),
    ("25K — £750", "25k_750"),
    ("50K — £850", "50k_850"),
    ("75K — £1,450", "75k_1450"),
    ("100K — £2,650", "100k_2650"),
    ("250K — £4,150", "250k_4150"),
    ("500K — £7,450", "500k_7450"),
    ("750K — £9,950", "750k_9950"),
    ("1M — £13,950", "1m_13950")
]

# --- EMAIL LEAD CATEGORIES ---
EMAIL_CATEGORIES = [
    ("Business", "business"),
    ("Crypto", "crypto"),
    ("Gaming", "gaming"),
    ("Music", "music"),
    ("Shopping", "shopping"),
    ("Social Media", "social_media")
]

# --- MAJOR BANKS MAPPING FOR ALL COUNTRIES ---
COUNTRY_BANKS = {
    "australia": [("Commonwealth Bank", "commbank"), ("Westpac", "westpac"), ("ANZ", "anz"), ("NAB", "nab"), ("Macquarie Bank", "macquarie")],
    "austria": [("Erste Bank", "erste"), ("Raiffeisen Bank", "raiffeisen"), ("UniCredit Bank Austria", "unicredit_austria"), ("BAWAG P.S.K.", "bawag")],
    "belgium": [("KBC Bank", "kbc"), ("Belfius", "belfius"), ("BNP Paribas Fortis", "bnp_fortis"), ("ING Belgium", "ing_belgium")],
    "brazil": [("Itaú Unibanco", "itau"), ("Banco Bradesco", "bradesco"), ("Banco do Brasil", "banco_do_brasil"), ("Santander Brasil", "santander_brasil"), ("Nubank", "nubank")],
    "canada": [("RBC", "rbc"), ("TD Canada Trust", "td"), ("Scotiabank", "scotiabank"), ("BMO", "bmo"), ("CIBC", "cibc")],
    "cayman_island": [("Butterfield Bank", "butterfield"), ("CIBC FirstCaribbean", "cibc_fc"), ("RBTT Bank", "rbtt"), ("NCB Cayman", "ncb_cayman")],
    "chile": [("Banco de Chile", "banco_de_chile"), ("Banco Santander Chile", "santander_chile"), ("BCI", "bci"), ("Banco Estado", "banco_estado")],
    "colombia": [("Bancolombia", "bancolombia"), ("Banco de Bogotá", "banco_bogota"), ("Davivienda", "davivienda"), ("BBVA Colombia", "bbva_colombia")],
    "croatia": [("Zagrebačka banka", "zaba"), ("Privredna banka Zagreb", "pbz"), ("Erste & Steiermärkische Bank", "erste_croatia"), ("OTP banka", "otp_croatia")],
    "curaco": [("MCB Bank", "mcb"), ("Vidanova Bank", "vidanova"), ("Banco di Caribe", "banco_di_caribe"), ("RBC Royal Bank", "rbc_curacao")],
    "cyprus": [("Bank of Cyprus", "bank_of_cyprus"), ("Hellenic Bank", "hellenic"), ("Alpha Bank Cyprus", "alpha_cyprus"), ("Eurobank Cyprus", "eurobank_cyprus")],
    "czech_republic": [("Česká spořitelna", "ceska"), ("ČSOB", "csob"), ("Komerční banka", "komercni"), ("Moneta Money Bank", "moneta")],
    "denmark": [("Danske Bank", "danske"), ("Jyske Bank", "jyske"), ("Sydbank", "sydbank"), ("Nykredit", "nykredit")],
    "dominican_republic": [("Banco BHD", "bhd"), ("Banco Popular Dominicano", "popular"), ("Banreservas", "banreservas"), ("Banco León", "leon")],
    "ecuador": [("Banco Pichincha", "pichincha"), ("Banco Guayaquil", "guayaquil"), ("Produbanco", "produbanco"), ("Banco Internacional", "internacional_ec")],
    "estonia": [("Swedbank Estonia", "swedbank_ee"), ("SEB Pank", "seb_ee"), ("LHV Pank", "lhv"), ("Luminor", "luminor_ee")],
    "finland": [("Nordea", "nordea_fi"), ("OP Financial Group", "op_group"), ("Danske Bank Finland", "danske_fi"), ("S-Pankki", "s_pankki")],
    "france": [("BNP Paribas", "bnp"), ("Credit Agricole", "credit_agricole"), ("Societe Generale", "socgen"), ("BPCE", "bpce"), ("La Banque Postale", "la_banque_postale")],
    "germany": [("Deutsche Bank", "deutsche"), ("Commerzbank", "commerzbank"), ("Sparkasse", "sparkasse"), ("N26", "n26"), ("DZ Bank", "dz_bank")],
    "greece": [("National Bank of Greece", "nbg"), ("Piraeus Bank", "piraeus"), ("Alpha Bank", "alpha_gr"), ("Eurobank", "eurobank_gr")],
    "hong_kong": [("HSBC Hong Kong", "hsbc_hk"), ("BOC Hong Kong", "bochk"), ("Hang Seng Bank", "hang_seng"), ("Standard Chartered HK", "sc_hk")],
    "hungary": [("OTP Bank", "otp_hu"), ("K&H Bank", "k_h"), ("Erste Bank Hungary", "erste_hu"), ("MBH Bank", "mbh")],
    "iceland": [("Landsbankinn", "landsbankinn"), ("Íslandsbanki", "islandsbanki"), ("Arion Bank", "arion")],
    "indonesia": [("Bank Mandiri", "mandiri"), ("Bank Rakyat Indonesia (BRI)", "bri"), ("Bank Central Asia (BCA)", "bca"), ("Bank Negara Indonesia (BNI)", "bni")],
    "ireland": [("AIB", "aib"), ("Bank of Ireland", "boi"), ("Permanent TSB", "ptsb"), ("KBC Ireland", "kbc_ireland")],
    "israel": [("Bank Hapoalim", "hapoalim"), ("Bank Leumi", "leumi"), ("Israel Discount Bank", "discount"), ("Mizrahi Tefahot", "mizrahi")],
    "italy": [("Intesa Sanpaolo", "intesa"), ("UniCredit", "unicredit_it"), ("Banco BPM", "banco_bpm"), ("Monte dei Paschi di Siena", "mps")],
    "latvia": [("Swedbank Latvija", "swedbank_lv"), ("SEB Latvija", "seb_lv"), ("Citadele Bank", "citadele"), ("Luminor Latvia", "luminor_lv")],
    "lithuania": [("Swedbank Lietuvoje", "swedbank_lt"), ("SEB Lietuvoje", "seb_lt"), ("Šiaulių bankas", "siauliu"), ("Luminor Lithuania", "luminor_lt")],
    "luxembourg": [("BCEE", "bcee"), ("BIL", "bil"), ("BGL BNP Paribas", "bgl_bnp"), ("Raiffeisen Luxembourg", "raiffeisen_lu")],
    "macao": [("BOC Macau", "boc_macau"), ("Tai Fung Bank", "tai_fung"), ("Banco Nacional Ultramarino", "bnu"), ("ICBC Macau", "icbc_macau")],
    "malaysia": [("Maybank", "maybank"), ("CIMB Bank", "cimb"), ("Public Bank Berhad", "public_bank"), ("RHB Bank", "rhb")],
    "malta": [("Bank of Valletta", "bov"), ("HSBC Bank Malta", "hsbc_malta"), ("APS Bank", "aps"), ("MeDirect", "medirect")],
    "myanmar": [("KBZ Bank", "kbz"), ("AYA Bank", "aya"), ("CB Bank", "cb_bank"), ("Yoma Bank", "yoma")],
    "nepal": [("Nabil Bank", "nabil"), ("Global IME Bank", "global_ime"), ("Nepal Investment Mega Bank", "nimb"), ("NIC Asia Bank", "nic_asia")],
    "netherlands": [("ING Bank", "ing_nl"), ("Rabobank", "rabobank"), ("ABN AMRO", "abn_amro"), ("SNS Bank", "sns")],
    "new_zealand": [("ANZ New Zealand", "anz_nz"), ("ASB Bank", "asb"), ("BNZ", "bnz"), ("Westpac NZ", "westpac_nz")],
    "norway": [("DNB", "dnb"), ("Nordea Norge", "nordea_no"), ("Danske Bank Norges", "danske_no"), ("Sbanken", "sbanken")],
    "philippines": [("BDO Unibank", "bdo"), ("Bank of the Philippine Islands (BPI)", "bpi"), ("Land Bank of the Philippines", "landbank"), ("Metrobank", "metrobank")],
    "poland": [("PKO Bank Polski", "pko"), ("Bank Pekao", "pekao"), ("Santander Bank Polska", "santander_pl"), ("mBank", "mbank")],
    "portugal": [("Caixa Geral de Depósitos", "cgd"), ("Millennium bcp", "bcp"), ("Novo Banco", "novo_banco"), ("BPI", "bpi_pt")],
    "romania": [("Banca Comercială Română (BCR)", "bcr"), ("BRD - Groupe Société Générale", "brd"), ("Banca Transilvania", "banca_transilvania"), ("ING Romania", "ing_ro")],
    "russia": [("Sberbank", "sberbank"), ("VTB Bank", "vtb"), ("Gazprombank", "gazprombank"), ("Alfa-Bank", "alfa_bank")],
    "singapore": [("DBS Bank", "dbs"), ("OCBC Bank", "ocbc"), ("UOB", "uob")],
    "slovakia": [("Slovenská sporiteľňa", "slovenska"), ("VÚB banka", "vub"), ("Tatra banka", "tatra"), ("UniCredit Bank Slovakia", "unicredit_sk")],
    "slovenia": [("NLB", "nlb"), ("NKBM", "nkbm"), ("SKB banka", "skb"), ("Intesa Sanpaolo Bank Slovenia", "intesa_si")],
    "south_africa": [("Standard Bank", "standard_bank"), ("FirstRand (FNB)", "fnb"), ("Absa Bank", "absa"), ("Nedbank", "nedbank")],
    "spain": [("Banco Santander", "santander_es"), ("BBVA", "bbva"), ("CaixaBank", "caixabank"), ("Sabadell", "sabadell")],
    "sweden": [("Swedbank", "swedbank"), ("SEB", "seb"), ("Handelsbanken", "handelsbanken"), ("Nordea", "nordea_se")],
    "switzerland": [("UBS", "ubs"), ("Zurich Cantonal Bank", "zkb"), ("Raiffeisen Switzerland", "raiffeisen_ch"), ("PostFinance", "postfinance")],
    "thailand": [("Bangkok Bank", "bangkok_bank"), ("Kasikornbank (KBank)", "kbank"), ("Siam Commercial Bank (SCB)", "scb"), ("Krungthai Bank", "krungthai")],
    "uk": [("Barclays", "barclays"), ("HSBC", "hsbc"), ("Lloyds", "lloyds"), ("NatWest", "natwest"), ("Santander", "santander"), ("Halifax", "halifax"), ("Nationwide", "nationwide"), ("Monzo", "monzo"), ("Starling", "starling")],
    "ukraine": [("PrivatBank", "privatbank"), ("Oschadbank", "oschadbank"), ("Universal Bank (monobank)", "monobank_ua"), ("Raiffeisen Bank Aval", "raiffeisen_ua")],
    "usa": [("Chase", "chase"), ("Bank of America", "bank_of_america"), ("Wells Fargo", "wells_fargo"), ("Citibank", "citibank"), ("Capital One", "capital_one"), ("US Bank", "us_bank"), ("PNC", "pnc"), ("TD Bank", "td_bank")],
    "vietnam": [("Vietcombank", "vietcombank"), ("Techcombank", "techcombank"), ("VietinBank", "vietinbank"), ("BIDV", "bidv"), ("VPBank", "vpbank")],
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

def email_pricing_tiers_keyboard(back_target):
    keyboard = [[InlineKeyboardButton(label, callback_data=f"email_price_{val}")] for label, val in EMAIL_PRICING_TIERS]
    keyboard.append([InlineKeyboardButton("Back", callback_data=back_target)])
    return InlineKeyboardMarkup(keyboard)

def email_categories_keyboard(back_target):
    keyboard = [[InlineKeyboardButton(name, callback_data=f"email_cat_{code}")] for name, code in EMAIL_CATEGORIES]
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

# --- CLEAN PAYMENT WALLETS KEYBOARD (BTC, ETH, USDT, LTC + Back) ---
def payment_wallets_keyboard(back_target):
    keyboard = [[InlineKeyboardButton(name, callback_data=f"wallet_pay_{code}")] for name, code in PAYMENT_WALLETS]
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
            text = "Please select a country:"
            await query.message.edit_text(text, reply_markup=countries_keyboard("bank_country", "main_menu"))
        elif cat_type == "email":
            text = "Please select a country:"
            await query.message.edit_text(text, reply_markup=countries_keyboard("email_country", "main_menu"))
        elif cat_type == "crypto":
            text = "Please select the amount of leads you want to purchase:"
            await query.message.edit_text(text, reply_markup=pricing_tiers_keyboard("main_menu"))
        else:
            text = "Please select the amount of leads you want to purchase:"
            await query.message.edit_text(text, reply_markup=pricing_tiers_keyboard("main_menu"))

    # --- EMAIL LEADS FLOW ---
    elif data.startswith("email_country_"):
        country_code = data.split("_")[2]
        context.user_data['selected_email_country'] = country_code

        text = "Please select an email leads category:"
        await query.message.edit_text(text, reply_markup=email_categories_keyboard("category_email"))

    elif data.startswith("email_cat_"):
        cat_code = data.split("_")[2]
        context.user_data['selected_email_category'] = cat_code

        text = "📋 **Updated Packages**\nPlease select a package tier:"
        country = context.user_data.get('selected_email_country', 'uk')
        await query.message.edit_text(text, reply_markup=email_pricing_tiers_keyboard(f"email_country_{country}"), parse_mode="Markdown")

    elif data.startswith("email_price_"):
        tier_code = data.split("_")[1]
        context.user_data['selected_email_tier'] = tier_code

        text = "Please select a payment wallet option:"
        cat_code = context.user_data.get('selected_email_category', 'business')
        await query.message.edit_text(text, reply_markup=payment_wallets_keyboard(f"email_cat_{cat_code}"))

    # --- CRYPTO LEADS FLOW ---
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
        
        text = "Please select a payment wallet option:"
        await query.message.edit_text(text, reply_markup=payment_wallets_keyboard(f"price_{tier}"))

    # --- SMS LEADS FLOW ---
    elif data.startswith("sms_country_"):
        country_code = data.split("_")[2]
        context.user_data['selected_sms_country'] = country_code
        tier = context.user_data.get('selected_tier', 'package')
        
        text = "Please select a payment wallet option:"
        await query.message.edit_text(text, reply_markup=payment_wallets_keyboard(f"price_{tier}"))

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

    elif data.startswith("bank_price_"):
        tier_code = data.split("_")[1]
        context.user_data['selected_bank_tier'] = tier_code
        
        text = "Please select a payment wallet option:"
        bank_name = context.user_data.get('selected_bank_name', 'bank')
        await query.message.edit_text(text, reply_markup=payment_wallets_keyboard(f"bank_name_{bank_name}"))

    # --- CHECKOUT / PAYMENT CONFIRMATION FOR PAYMENT WALLETS (BTC, ETH, USDT, LTC) ---
    elif data.startswith("wallet_pay_"):
        wallet_code = data.split("_")[2]
        context.user_data['selected_payment_wallet'] = wallet_code
        
        wallet_name = wallet_code.upper()
        category = context.user_data.get('selected_category', 'leads')

        if category == "bank":
            country = context.user_data.get('selected_bank_country', 'global')
            bank = context.user_data.get('selected_bank_name', 'bank')
            tier = context.user_data.get('selected_bank_tier', 'package')
            back_target = f"bank_price_{tier}"

            text = (
                f"Order Summary\n\n"
                f"Category: BANK LEADS\n"
                f"Country: {country.upper()}\n"
                f"Bank Institution: {bank.upper()}\n"
                f"Package Tier: {tier.upper()} Leads\n"
                f"Payment Wallet: {wallet_name}\n\n"
                f"Status: Ready for checkout. Please contact administration to complete payment."
            )
        elif category == "email":
            country = context.user_data.get('selected_email_country', 'global')
            email_cat = context.user_data.get('selected_email_category', 'category')
            tier = context.user_data.get('selected_email_tier', 'package')
            back_target = f"email_price_{tier}"

            text = (
                f"Order Summary\n\n"
                f"Category: EMAIL LEADS ({email_cat.upper()})\n"
                f"Country: {country.upper()}\n"
                f"Package Tier: {tier.upper()} Leads\n"
                f"Payment Wallet: {wallet_name}\n\n"
                f"Status: Ready for checkout. Please contact administration to complete payment."
            )
        else:
            tier = context.user_data.get('selected_tier', 'package')
            country = context.user_data.get('selected_country', 'global')
            back_target = f"price_{tier}"

            text = (
                f"Order Summary\n\n"
                f"Category: {category.upper()} LEADS\n"
                f"Package: {tier.upper()} Leads\n"
                f"Country: {country.upper()}\n"
                f"Payment Wallet: {wallet_name}\n\n"
                f"Status: Ready for checkout. Please contact administration to complete payment."
            )

        keyboard = [
            [InlineKeyboardButton("Back", callback_data=back_target)],
            [InlineKeyboardButton("Main Menu", callback_data="main_menu")]
        ]
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

    # --- WALLET & TOP UP FLOW (Using general crypto exchanges list) ---
    elif data == "wallet":
        text = (
            "Current Balance: £0\n\n"
            "Please select a crypto option to top up your balance:"
        )
        await query.message.edit_text(text, reply_markup=crypto_exchanges_keyboard("main_menu"))

    elif data.startswith("crypto_ex_"):
        exchange_code = data.split("_")[2]
        context.user_data['selected_exchange'] = exchange_code
        exchange = exchange_code.capitalize()

        text = (
            f"Top Up Summary\n\n"
            f"Method: {exchange}\n"
            f"Current Balance: £0\n\n"
            f"Status: Ready for top up. Please contact administration to complete payment."
        )
        keyboard = [
            [InlineKeyboardButton("Back", callback_data="wallet")],
            [InlineKeyboardButton("Main Menu", callback_data="main_menu")]
        ]
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

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
