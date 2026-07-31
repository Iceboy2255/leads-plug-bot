import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from datetime import datetime

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load Token from Environment Variable
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# In-memory storage for user join dates (or use a database in production)
USER_JOIN_DATES = {}

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

# --- LEDGER DEVICE LEADS SPECIFIC COUNTRIES (Step 2: 2 per row) ---
LEDGER_COUNTRIES = [
    ("United Kingdom", "uk"),
    ("United States", "usa"),
    ("Canada", "canada"),
    ("Australia", "australia"),
    ("Germany", "germany"),
    ("France", "france"),
    ("Netherlands", "netherlands"),
    ("Sweden", "sweden")
]

# --- HARDWARE WALLET DEVICES (Step 3: 2 per row) ---
HARDWARE_DEVICES = [
    ("Blockstream Jade", "blockstream_jade"),
    ("SafePal S1", "safepal_s1"),
    ("SafePal X1", "safepal_x1"),
    ("Tangem Card", "tangem_card"),
    ("Tangem Ring", "tangem_ring"),
    ("CoolWallet Pro", "coolwallet_pro"),
    ("CoolWallet S", "coolwallet_s"),
    ("OneKey Classic", "onekey_classic"),
    ("Ledger Flex", "ledger_flex"),
    ("Ledger Stax", "ledger_stax"),
    ("Trezor Model One", "trezor_model_one"),
    ("Trezor Safe 3", "trezor_safe_3"),
    ("Trezor Safe 5", "trezor_safe_5"),
    ("ELLIPAL Titan 2.0", "ellipal_titan_2"),
    ("ELLIPAL Titan Mini", "ellipal_titan_mini"),
    ("Keystone 3 Pro", "keystone_3_pro"),
    ("Ledger Nano S Plus", "ledger_nano_s_plus"),
    ("Ledger Nano X", "ledger_nano_x")
]

# --- LEDGER DEVICE LEADS PRICING TIERS (Step 4) ---
LEDGER_DEVICE_PRICING_TIERS = [
    ("1k = £350", "1k_350"),
    ("2k = £600", "2k_600"),
    ("3k = £800", "3k_800"),
    ("4k = £950", "4k_950"),
    ("5k = £1,100", "5k_1100"),
    ("10k = £1,800", "10k_1800"),
    ("15k = £2,400", "15k_2400"),
    ("20k = £2,900", "20k_2900"),
    ("25k = £3,300", "25k_3300")
]

# --- CRYPTO EXCHANGES (Single Column List) for Crypto Leads Only ---
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

# --- PAYMENT WALLETS WITH EXACT ADDRESSES ---
PAYMENT_WALLETS = [
    ("BTC", "btc", "bc1q6cyn934d3vlmgyghr6znnqyl3j4hluk883h70a"),
    ("ETH", "eth", "0x44ceA102871A7270785585909a4eBe13A157D614"),
    ("USDT", "usdt", "TVYa8uBeMZem8MwePaVii5PjEydrK3e8it"),
    ("LTC", "ltc", "LgHLihB2f48nh13F7Byu8yiEAVRhuBMEXL")
]

WALLET_ADDRESSES = {code: addr for _, code, addr in PAYMENT_WALLETS}

# --- CRYPTO LEADS PRICING TIERS ---
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

# --- AGED SMS LEADS PRICING TIERS (FEMALE) ---
SMS_FEMALE_PRICING_TIERS = [
    ("1K - £45", "1k_45"),
    ("2K - £69", "2k_69"),
    ("3K - £87", "3k_87"),
    ("4K - £105", "4k_105"),
    ("5K - £115", "5k_115"),
    ("10K - £175", "10k_175"),
    ("15K - £255", "15k_255"),
    ("20K - £315", "20k_315"),
    ("25k - £375", "25k_375"),
    ("30k - £455", "30k_455"),
    ("35k - £505", "35k_505"),
    ("40k - £535", "40k_535"),
    ("45k - £555", "45k_555"),
    ("50k - £575", "50k_575"),
    ("100k - £715", "100k_715"),
    ("200k - £1015", "200k_1015"),
    ("500k - £1615", "500k_1615"),
    ("1M - £2015", "1m_2015")
]

# --- AGED SMS LEADS PRICING TIERS (MALE) ---
SMS_MALE_PRICING_TIERS = [
    ("1K - £30", "1k_30"),
    ("2K - £54", "2k_54"),
    ("3K - £72", "3k_72"),
    ("4K - £90", "4k_90"),
    ("5K - £100", "5k_100"),
    ("10K - £160", "10k_160"),
    ("15K - £240", "15k_240"),
    ("20K - £300", "20k_300"),
    ("25k - £360", "25k_360"),
    ("30k - £440", "30k_440"),
    ("35k - £490", "35k_490"),
    ("40k - £520", "40k_520"),
    ("45k - £540", "45k_540"),
    ("50k - £560", "50k_560"),
    ("100k - £700", "100k_700"),
    ("200k - £1000", "200k_1000"),
    ("500k - £1600", "500k_1600"),
    ("1M - £2000", "1m_2000")
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

# --- BANK LEADS MAPPING FOR ALL COUNTRIES ---
COUNTRY_BANKS = {
    "australia": [
        ("Commonwealth Bank", "commonwealth_bank"), ("Westpac Bank", "westpac_bank"), ("ANZ Bank", "anz_bank"),
        ("National Australia Bank", "national_australia_bank"), ("Macquarie Bank", "macquarie_bank"), ("Bendigo Bank", "bendigo_bank"),
        ("Suncorp Bank", "suncorp_bank"), ("Bank of Queensland", "bank_of_queensland"), ("ING Australia", "ing_australia"),
        ("HSBC Australia", "hsbc_australia"), ("Citibank Australia", "citibank_australia"), ("AMP Bank", "amp_bank"),
        ("Bankwest", "bankwest"), ("ME Bank", "me_bank"), ("UBank", "ubank"), ("Virgin Money Australia", "virgin_money_australia"),
        ("Judo Bank", "judo_bank"), ("Beyond Bank", "beyond_bank"), ("Heritage Bank", "heritage_bank")
    ],
    "austria": [
        ("Erste Bank", "erste_bank"), ("Raiffeisen Bank", "raiffeisen_bank"), ("Bank Austria", "bank_austria"),
        ("BAWAG Group", "bawag_group"), ("Volksbank Wien", "volksbank_wien"), ("Oberbank", "oberbank"),
        ("Hypo Tirol Bank", "hypo_tirol_bank"), ("Hypo Vorarlberg Bank", "hypo_vorarlberg_bank"), ("Addiko Bank", "addiko_bank"),
        ("DenizBank Austria", "denizbank_austria"), ("BKS Bank", "bks_bank"), ("Volkskreditbank", "volkskreditbank")
    ],
    "belgium": [
        ("KBC Bank", "kbc_bank"), ("BNP Paribas Fortis", "bnp_paribas_fortis"), ("ING Belgium", "ing_belgium"),
        ("Belfius Bank", "belfius_bank"), ("Argenta", "argenta"), ("AXA Bank Belgium", "axa_bank_belgium"),
        ("Crelan", "crelan"), ("Beobank", "beobank"), ("Europabank", "europabank"), ("Nagelmackers Bank", "nagelmackers_bank"),
        ("Keytrade Bank", "keytrade_bank"), ("VDK Bank", "vdk_bank")
    ],
    "brazil": [
        ("Banco do Brasil", "banco_do_brasil"), ("Itaú Unibanco", "itau_unibanco"), ("Bradesco Bank", "bradesco_bank"),
        ("Santander Brasil", "santander_brasil"), ("Caixa Econômica Federal", "caixa_economica_federal"), ("Banco Safra", "banco_safra"),
        ("BTG Pactual", "btg_pactual"), ("Banco Inter", "banco_inter"), ("Nubank", "nubank"), ("Banco Pan", "banco_pan"),
        ("Banco Votorantim", "banco_votorantim"), ("Banco Daycoval", "banco_daycoval"), ("Banco Original", "banco_original")
    ],
    "canada": [
        ("Royal Bank of Canada", "royal_bank_of_canada"), ("TD Canada Trust", "td_canada_trust"), ("Scotiabank", "scotiabank"),
        ("Bank of Montreal", "bank_of_montreal"), ("CIBC", "cibc"), ("National Bank of Canada", "national_bank_of_canada"),
        ("HSBC Canada", "hsbc_canada"), ("Laurentian Bank", "laurentian_bank"), ("EQ Bank", "eq_bank"), ("Alterna Bank", "alterna_bank"),
        ("Canadian Western Bank", "canadian_western_bank"), ("Manulife Bank", "manulife_bank"), ("Tangerine Bank", "tangerine_bank"),
        ("Simplii Financial", "simplii_financial"), ("Motusbank", "motusbank"), ("VersaBank", "versabank"), ("Oaken Financial", "oaken_financial")
    ],
    "cayman_island": [
        ("Cayman National Bank", "cayman_national_bank"), ("Butterfield Bank", "butterfield_bank"), ("Fidelity Bank Cayman", "fidelity_bank_cayman"),
        ("Scotiabank Cayman", "scotiabank_cayman"), ("RBC Cayman", "rbc_cayman"), ("CIBC FirstCaribbean", "cibc_firstcaribbean"), ("HSBC Cayman", "hsbc_cayman")
    ],
    "chile": [
        ("Banco de Chile", "banco_de_chile"), ("Banco Santander Chile", "banco_santander_chile"), ("Banco Estado", "banco_estado"),
        ("Banco BCI", "banco_bci"), ("Scotiabank Chile", "scotiabank_chile"), ("Banco Falabella", "banco_falabella"), ("Banco Ripley", "banco_ripley")
    ],
    "colombia": [
        ("Bancolombia", "bancolombia"), ("Banco de Bogotá", "banco_de_bogota"), ("Davivienda", "davivienda"),
        ("BBVA Colombia", "bbva_colombia"), ("Banco Popular Colombia", "banco_popular_colombia"), ("Scotiabank Colpatria", "scotiabank_colpatria"),
        ("Banco Agrario", "banco_agrario"), ("Banco Caja Social", "banco_caja_social")
    ],
    "croatia": [
        ("Zagrebacka Banka", "zagrebacka_banka"), ("Privredna Banka Zagreb", "privredna_banka_zagreb"), ("Erste Bank Croatia", "erste_bank_croatia"),
        ("Raiffeisen Bank Croatia", "raiffeisen_bank_croatia"), ("OTP Bank Croatia", "otp_bank_croatia"), ("Addiko Bank Croatia", "addiko_bank_croatia"),
        ("Hrvatska Postanska Banka", "hrvatska_postanska_banka")
    ],
    "cyprus": [
        ("Bank of Cyprus", "bank_of_cyprus"), ("Hellenic Bank", "hellenic_bank"), ("Eurobank Cyprus", "eurobank_cyprus"),
        ("Alpha Bank Cyprus", "alpha_bank_cyprus"), ("AstroBank", "astrobank"), ("Ancoria Bank", "ancoria_bank")
    ],
    "czech_republic": [
        ("Ceska Sporitelna", "ceska_sporitelna"), ("CSOB Bank", "csob_bank"), ("Komercni Banka", "komercni_banka"),
        ("Moneta Money Bank", "moneta_money_bank"), ("Air Bank", "air_bank"), ("Fio Banka", "fio_banka")
    ],
    "denmark": [
        ("Danske Bank", "danske_bank"), ("Nordea Denmark", "nordea_denmark"), ("Jyske Bank", "jyske_bank"),
        ("Sydbank", "sydbank"), ("Nykredit Bank", "nykredit_bank"), ("Spar Nord Bank", "spar_nord_bank")
    ],
    "dominican_republic": [
        ("Banco BHD", "bhd"), ("Banco Popular Dominicano", "popular"), ("Banreservas", "banreservas"), ("Banco León", "leon")
    ],
    "ecuador": [
        ("Banco Pichincha", "banco_pichincha"), ("Banco Guayaquil", "banco_guayaquil"), ("Banco del Pacífico", "banco_del_pacifico")
    ],
    "estonia": [
        ("LHV Bank", "lhv_bank"), ("SEB Estonia", "seb_estonia"), ("Swedbank Estonia", "swedbank_estonia")
    ],
    "finland": [
        ("Nordea Finland", "nordea_finland"), ("OP Bank", "op_bank"), ("Danske Bank Finland", "danske_bank_finland")
    ],
    "france": [
        ("BNP Paribas", "bnp_paribas"), ("Société Générale", "societe_generale"), ("Crédit Agricole", "credit_agricole"),
        ("HSBC France", "hsbc_france"), ("La Banque Postale", "la_banque_postale")
    ],
    "germany": [
        ("Deutsche Bank", "deutsche_bank"), ("Commerzbank", "commerzbank"), ("KfW Bank", "kfw_bank"),
        ("ING Germany", "ing_germany"), ("DZ Bank", "dz_bank")
    ],
    "greece": [
        ("National Bank of Greece", "nbg"), ("Piraeus Bank", "piraeus"), ("Alpha Bank", "alpha_gr"), ("Eurobank", "eurobank_gr")
    ],
    "hong_kong": [
        ("HSBC Hong Kong", "hsbc_hong_kong"), ("Hang Seng Bank", "hang_seng_bank"), ("Standard Chartered Hong Kong", "standard_chartered_hong_kong"),
        ("Bank of China Hong Kong", "bank_of_china_hong_kong"), ("DBS Hong Kong", "dbs_hong_kong")
    ],
    "hungary": [
        ("OTP Bank Hungary", "otp_bank_hungary"), ("K&H Bank", "k_h_bank"), ("Erste Bank Hungary", "erste_bank_hungary"), ("UniCredit Hungary", "unicredit_hungary")
    ],
    "iceland": [
        ("Landsbankinn", "landsbankinn"), ("Arion Bank", "arion_bank"), ("Islandsbanki", "islandsbanki")
    ],
    "indonesia": [
        ("Bank Mandiri", "bank_mandiri"), ("Bank Central Asia", "bank_central_asia"), ("Bank Negara Indonesia", "bank_negara_indonesia"),
        ("Bank Rakyat Indonesia", "bank_rakyat_indonesia"), ("CIMB Niaga", "cimb_niaga")
    ],
    "ireland": [
        ("Bank of Ireland", "bank_of_ireland"), ("Allied Irish Banks", "allied_irish_banks"), ("Permanent TSB", "permanent_tsb"), ("Ulster Bank Ireland", "ulster_bank_ireland")
    ],
    "israel": [
        ("Bank Leumi", "bank_leumi"), ("Bank Hapoalim", "bank_hapoalim"), ("Israel Discount Bank", "israel_discount_bank"), ("Mizrahi Tefahot Bank", "mizrahi_tefahot_bank")
    ],
    "italy": [
        ("UniCredit", "unicredit"), ("Intesa Sanpaolo", "intesa_sanpaolo"), ("Banco BPM", "banco_bpm"),
        ("Monte dei Paschi di Siena", "monte_dei_paschi_di_siena"), ("BPER Banca", "bper_banca")
    ],
    "latvia": [
        ("Swedbank Latvia", "swedbank_latvia"), ("SEB Latvia", "seb_latvia"), ("Citadele Bank", "citadele_bank")
    ],
    "lithuania": [
        ("Swedbank Lithuania", "swedbank_lithuania"), ("SEB Lithuania", "seb_lithuania"), ("Siauliu Bankas", "siauliu_bankas")
    ],
    "luxembourg": [
        ("Banque Internationale Luxembourg", "banque_internationale_luxembourg"), ("Spuerkeess", "spuerkeess"), ("BGL BNP Paribas", "bgl_bnp_paribas")
    ],
    "macao": [
        ("Banco Nacional Ultramarino", "banco_nacional_ultramarino")
    ],
    "malaysia": [
        ("Maybank", "maybank"), ("CIMB Bank", "cimb_bank"), ("Public Bank", "public_bank"),
        ("RHB Bank", "rhb_bank"), ("Hong Leong Bank", "hong_leong_bank")
    ],
    "malta": [
        ("Bank of Valletta", "bank_of_valletta"), ("HSBC Malta", "hsbc_malta"), ("APS Bank", "aps_bank")
    ],
    "myanmar": [
        ("KBZ Bank", "kbz_bank"), ("AYA Bank", "aya_bank"), ("CB Bank Myanmar", "cb_bank_myanmar")
    ],
    "nepal": [
        ("NIC Asia Bank", "nic_asia_bank"), ("Global IME Bank", "global_ime_bank"), ("Nabil Bank", "nabil_bank")
    ],
    "netherlands": [
        ("ING Netherlands", "ing_netherlands"), ("ABN AMRO", "abn_amro"), ("Rabobank", "rabobank"), ("De Volksbank", "de_volksbank")
    ],
    "new_zealand": [
        ("ANZ New Zealand", "anz_new_zealand"), ("ASB Bank", "asb_bank"), ("Westpac NZ", "westpac_nz"), ("Kiwibank", "kiwibank")
    ],
    "norway": [
        ("DNB Bank", "dnb_bank"), ("Nordea Norway", "nordea_norway"), ("SpareBank 1", "sparebank_1")
    ],
    "philippines": [
        ("BDO", "bdo"), ("Bank of the Philippine Islands", "bank_of_the_philippine_islands"),
        ("Metrobank Philippines", "metrobank_philippines"), ("Land Bank Philippines", "land_bank_philippines")
    ],
    "poland": [
        ("PKO Bank Polski", "pko_bank_polski"), ("mBank", "mbank"), ("Santander Poland", "santander_poland")
    ],
    "portugal": [
        ("Banco Santander Totta", "banco_santander_totta"), ("Millennium BCP", "millennium_bcp"), ("Novo Banco", "novo_banco")
    ],
    "romania": [
        ("Banca Transilvania", "banca_transilvania"), ("BRD Bank", "brd_bank"), ("Raiffeisen Bank Romania", "raiffeisen_bank_romania")
    ],
    "russia": [
        ("Sberbank", "sberbank"), ("VTB Bank", "vtb_bank"), ("Gazprombank", "gazprombank"), ("Alfa Bank Russia", "alfa_bank_russia")
    ],
    "singapore": [
        ("DBS Bank", "dbs_bank"), ("OCBC Bank", "ocbc_bank"), ("UOB Bank", "uob_bank")
    ],
    "slovakia": [
        ("Slovenská Sporiteľňa", "slovenska_sporitelna"), ("VUB Bank", "vub_bank")
    ],
    "slovenia": [
        ("NLB Bank", "nlb_bank")
    ],
    "south_africa": [
        ("Standard Bank", "standard_bank"), ("FirstRand Bank", "firstrand_bank"), ("Absa Bank", "absa_bank"), ("Nedbank", "nedbank")
    ],
    "spain": [
        ("Santander Spain", "santander_spain"), ("BBVA", "bbva"), ("CaixaBank", "caixabank"), ("Banco Sabadell", "banco_sabadell")
    ],
    "sweden": [
        ("Swedbank", "swedbank"), ("SEB Bank", "seb_bank"), ("Handelsbanken", "handelsbanken"), ("Nordea Sweden", "nordea_sweden")
    ],
    "switzerland": [
        ("UBS", "ubs"), ("Credit Suisse", "credit_suisse"), ("Julius Baer", "julius_baer"), ("Zurich Cantonal Bank", "zurich_cantonal_bank")
    ],
    "thailand": [
        ("Bangkok Bank", "bangkok_bank"), ("Kasikornbank", "kasikornbank"), ("Siam Commercial Bank", "siam_commercial_bank"), ("Krungthai Bank", "krungthai_bank")
    ],
    "uk": [
        ("HSBC", "hsbc"), ("Barclays", "barclays"), ("Lloyds Bank", "lloyds_bank"), ("NatWest", "natwest"),
        ("Santander UK", "santander_uk"), ("TSB Bank", "tsb_bank"), ("Virgin Money UK", "virgin_money_uk"), ("Metro Bank", "metro_bank"),
        ("Starling Bank", "starling_bank"), ("Monzo Bank", "monzo_bank"), ("Co-operative Bank", "co_operative_bank"), ("Aldermore Bank", "aldermore_bank"),
        ("Close Brothers", "close_brothers"), ("Secure Trust Bank", "secure_trust_bank"), ("Shawbrook Bank", "shawbrook_bank"), ("Clydesdale Bank", "clydesdale_bank"),
        ("Yorkshire Bank", "yorkshire_bank"), ("Handelsbanken UK", "handelsbanken_uk"), ("Investec Bank UK", "investec_bank_uk"), ("Citibank UK", "citibank_uk")
    ],
    "ukraine": [
        ("PrivatBank", "privatbank"), ("Oschadbank", "oschadbank"), ("Ukreximbank", "ukreximbank"), ("Raiffeisen Bank Ukraine", "raiffeisen_bank_ukraine")
    ],
    "usa": [
        ("JPMorgan Chase", "jpmorgan_chase"), ("Bank of America", "bank_of_america"), ("Wells Fargo", "wells_fargo"),
        ("Citibank", "citibank"), ("Goldman Sachs Bank", "goldman_sachs_bank"), ("Morgan Stanley Bank", "morgan_stanley_bank"),
        ("U.S. Bank", "u_s_bank"), ("PNC Bank", "pnc_bank"), ("Truist Bank", "truist_bank"), ("Capital One", "capital_one"),
        ("TD Bank USA", "td_bank_usa"), ("Fifth Third Bank", "fifth_third_bank"), ("KeyBank", "keybank"), ("Regions Bank", "regions_bank"),
        ("Huntington Bank", "huntington_bank"), ("Ally Bank", "ally_bank"), ("Discover Bank", "discover_bank"), ("Charles Schwab Bank", "charles_schwab_bank"),
        ("BMO Harris Bank", "bmo_harris_bank"), ("First Republic Bank", "first_republic_bank")
    ],
    "vietnam": [
        ("Vietcombank", "vietcombank"), ("BIDV", "bidv"), ("VietinBank", "vietinbank"), ("Techcombank", "techcombank"), ("ACB Vietnam", "acb_vietnam")
    ],
    "default": [
        ("National Bank", "national_bank"), ("Commercial Bank", "commercial_bank"), ("Retail Bank", "retail_bank"), ("Digital Bank", "digital_bank")
    ]
}

# --- KEYBOARD BUILDERS ---

def main_menu_keyboard():
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

# --- HANDLERS ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user and user.id not in USER_JOIN_DATES:
        USER_JOIN_DATES[user.id] = datetime.now().strftime("%m-%d-%Y")

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

    user = update.effective_user
    if user and user.id not in USER_JOIN_DATES:
        USER_JOIN_DATES[user.id] = datetime.now().strftime("%m-%d-%Y")

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
            text = "Please select an option:"
            await query.message.edit_text(text, reply_markup=crypto_leads_home_keyboard("main_menu"))
        elif cat_type == "sms":
            text = "Please select a country:"
            await query.message.edit_text(text, reply_markup=countries_keyboard("sms_country", "main_menu"))
        else:
            text = "Please select an option:"
            await query.message.edit_text(text, reply_markup=main_menu_keyboard())

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

    elif data.startswith("ledger_price_"):
        tier_code = data.split("_")[2]
        context.user_data['selected_ledger_tier'] = tier_code
        device_code = context.user_data.get('selected_ledger_device', 'ledger_nano_x')
        back_target = f"ledger_device_{device_code}"

        text = (
            "==============================\n"
            "💳 **Select Payment Wallet**\n"
            "==============================\n\n"
            "Please choose your preferred cryptocurrency to complete the payment.\n\n"
            "<i>Minimum deposit: £50</i>"
        )
        await query.message.edit_text(text, reply_markup=wallet_page_keyboard(back_target), parse_mode="HTML")

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

        cat_code = context.user_data.get('selected_email_category', 'business')
        back_target = f"email_cat_{cat_code}"

        text = (
            "==============================\n"
            "💳 **Select Payment Wallet**\n"
            "==============================\n\n"
            "Please choose your preferred cryptocurrency to complete the payment.\n\n"
            "<i>Minimum deposit: £50</i>"
        )
        await query.message.edit_text(text, reply_markup=wallet_page_keyboard(back_target), parse_mode="HTML")

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

    elif data.startswith("price_"):
        tier_code = data.split("_")[1]
        context.user_data['selected_tier'] = tier_code

        country = context.user_data.get('selected_crypto_country', 'uk')
        back_target = f"crypto_country_{country}"

        text = (
            "==============================\n"
            "💳 **Select Payment Wallet**\n"
            "==============================\n\n"
            "Please choose your preferred cryptocurrency to complete the payment.\n\n"
            "<i>Minimum deposit: £50</i>"
        )
        await query.message.edit_text(text, reply_markup=wallet_page_keyboard(back_target), parse_mode="HTML")

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

    elif data.startswith("sms_price_"):
        parts = data.split("_")
        gender = parts[2]
        tier_code = parts[3]
        context.user_data['selected_sms_tier'] = tier_code

        back_target = f"sms_gender_{gender}"

        text = (
            "==============================\n"
            "💳 **Select Payment Wallet**\n"
            "==============================\n\n"
            "Please choose your preferred cryptocurrency to complete the payment.\n\n"
            "<i>Minimum deposit: £50</i>"
        )
        await query.message.edit_text(text, reply_markup=wallet_page_keyboard(back_target), parse_mode="HTML")

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
        
        bank_name = context.user_data.get('selected_bank_name', 'bank')
        back_target = f"bank_name_{bank_name}"

        text = (
            "==============================\n"
            "💳 **Select Payment Wallet**\n"
            "==============================\n\n"
            "Please choose your preferred cryptocurrency to complete the payment.\n\n"
            "<i>Minimum deposit: £50</i>"
        )
        await query.message.edit_text(text, reply_markup=wallet_page_keyboard(back_target), parse_mode="HTML")

    # --- WALLET & TOP UP FLOW ---
    elif data == "wallet":
        user_id = query.from_user.id
        join_date = USER_JOIN_DATES.get(user_id, datetime.now().strftime("%m-%d-%Y"))
        text = (
            "==================================\n"
            f"🪪 ID: {user_id}\n"
            f"💰 Balance: £0.00\n"
            f"🗓 Join Date: {join_date}\n"
            "==================================\n\n"
            "Select a top-up amount below:\n"
            "<i>Minimum top-up: £50</i>"
        )
        await query.message.edit_text(text, reply_markup=topup_keyboard("main_menu"), parse_mode="HTML")

    elif data.startswith("topup_"):
        amount = data.split("_")[1]
        if amount == "custom":
            text = "Please enter your custom top-up amount:"
            await query.message.edit_text(text, reply_markup=wallet_page_keyboard("wallet"))
        else:
            wallet_addr = WALLET_ADDRESSES.get("btc", "bc1q6cyn934d3vlmgyghr6znnqyl3j4hluk883h70a")
            text = (
                f"Top-up Amount: £{amount}\n\n"
                f"BTC Wallet Address:\n`{wallet_addr}`\n\n"
                f"<i>Minimum top-up: £50</i>"
            )
            await query.message.edit_text(text, reply_markup=wallet_page_keyboard("wallet"), parse_mode="HTML")

    elif data.startswith("pay_"):
        coin = data.split("_")[1].upper()
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
