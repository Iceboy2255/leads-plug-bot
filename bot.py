import os
import random
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

LEADS = 3459000
FULLZ = 456

# Clean UK Base Lists grouped by price (quantities and duplicates cleaned)
UK_30_BASES = [
    377935, 379103, 379921, 401704, 402483, 406068, 409758, 412983,
    412985, 415141, 416549, 421363, 421808, 423063, 423608, 425125,
    425854, 426150, 428331, 430589, 430742, 431911, 434256, 436767
]

UK_20_BASES = [
    341263, 341278, 374681, 377384, 377386, 377389, 402396, 412983,
    416549, 432265, 433668, 437709, 443446, 446204, 446238, 446259
]

UK_10_BASES = [
    535522, 535666, 537317, 537370, 557483, 416598, 425125, 427977, 
    440043, 446223, 446238, 446259, 446263, 446271, 446272, 446278, 446291
]

UK_5_BASES = [
    341268, 341269, 341270, 371783, 371784, 374681,
    412984, 416549, 436982, 446238, 446259
]

# Clean and evenly distributed AU Base Lists based on provided data
AU_30_BASES = [
    251729, 401714, 401795, 402993, 404137, 405497, 423953, 423954, 426557, 431313, 434956, 434968
]

AU_20_BASES = [
    439239, 441115, 450606, 450949, 455701, 456430, 456468, 456475, 462239, 464554, 473256, 474838
]

AU_10_BASES = [
    493130, 494052, 515683, 516310, 516323, 516361, 516366, 518863, 518868, 521729, 526901, 527172
]

AU_5_BASES = [
    528013, 529918, 532655, 535316, 535318, 538653, 540403, 544647, 550586, 554758
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        f"+ニニ Stock ニニニ+\n"
        f"• Leads: {LEADS}\n"
        f"| Fullz: {FULLZ}\n"
        f"=== Stock ==+\n\n"
        f"Choose an option below:"
    )

    keyboard = [
        [
            InlineKeyboardButton("Leads", callback_data="leads"),
            InlineKeyboardButton("Fullz", callback_data="fullz"),
        ],
        [
            InlineKeyboardButton("Wallet", callback_data="wallet"),
            InlineKeyboardButton("Help", callback_data="help"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(text, reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    # Handle individual base click with credit check and popup alerts for UK/AU
    if query.data.startswith("base_buy_") or query.data.startswith("au_buy_"):
        parts = query.data.split("_")
        price = int(parts[2])
        
        user_credits = context.user_data.get("credits", 0)

        if user_credits < price:
            await query.answer("❌ NOT ENOUGH CREDITS ❌", show_alert=True)
            return
        else:
            await query.answer("Access granted", show_alert=True)
            await query.edit_message_text("Access granted")
            return

    await query.answer()

    if query.data == "leads":
        await query.edit_message_text("You selected **Leads**.\n\n(Add your leads info / price here)")

    elif query.data == "fullz":
        text = "📦 **Fullz Lists**\n\nChoose a country:"
        keyboard = [
            [InlineKeyboardButton("UK List", callback_data="fullz_uk")],
            [InlineKeyboardButton("AU List", callback_data="fullz_au")],
            [InlineKeyboardButton("US List", callback_data="fullz_us")],
            [InlineKeyboardButton("« Back", callback_data="back_to_start")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")

    elif query.data == "fullz_uk":
        text = "🇬🇧 **UK List**\n\nChoose a base option:"
        keyboard = [
            [InlineKeyboardButton("£5 Base", callback_data="base_uk_5_0")],
            [InlineKeyboardButton("£10 Base", callback_data="base_uk_10_0")],
            [InlineKeyboardButton("£20 Base", callback_data="base_uk_20_0")],
            [InlineKeyboardButton("£30 Base", callback_data="base_uk_30_0")],
            [InlineKeyboardButton("« Back", callback_data="fullz")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")

    elif query.data == "fullz_au":
        text = "🇦🇺 **AU List**\n\nChoose a base option:"
        keyboard = [
            [InlineKeyboardButton("£5 Base", callback_data="base_au_5_0")],
            [InlineKeyboardButton("£10 Base", callback_data="base_au_10_0")],
            [InlineKeyboardButton("£20 Base", callback_data="base_au_20_0")],
            [InlineKeyboardButton("£30 Base", callback_data="base_au_30_0")],
            [InlineKeyboardButton("« Back", callback_data="fullz")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")

    elif query.data == "fullz_us":
        text = "🇺🇸 **US List**\n\nChoose a package:"
        keyboard = [
            [InlineKeyboardButton("£5 Base", callback_data="us_5")],
            [InlineKeyboardButton("£10 Base", callback_data="us_10")],
            [InlineKeyboardButton("£20 Base", callback_data="us_20")],
            [InlineKeyboardButton("£30 Base", callback_data="us_30")],
            [InlineKeyboardButton("« Back", callback_data="fullz")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")

    # Handling Clean UK Base Lists with Pagination System and navigation buttons
    elif query.data.startswith("base_uk_"):
        parts = query.data.split("_")
        price = int(parts[2])
        page = int(parts[3])
        
        bases_map = {30: UK_30_BASES, 20: UK_20_BASES, 10: UK_10_BASES, 5: UK_5_BASES}
        bases_list = bases_map.get(price, [])
        
        items_per_page = 10
        total_pages = max(1, (len(bases_list) + items_per_page - 1) // items_per_page)
        
        if page >= total_pages:
            page = 0
        
        start_idx = page * items_per_page
        end_idx = start_idx + items_per_page
        current_slice = bases_list[start_idx:end_idx]
        
        text = (
            f"🇬🇧 **UK £{price} Base** (Page {page + 1}/{total_pages})\n\n"
            f"Tap an item to select:"
        )
        
        keyboard = []
        for bin_num in current_slice:
            keyboard.append([InlineKeyboardButton(str(bin_num), callback_data=f"base_buy_{price}_{bin_num}")])
            
        nav_row = []
        nav_row.append(InlineKeyboardButton("🔄 Refresh", callback_data=f"base_uk_{price}_{page}"))
        
        if page < total_pages - 1:
            nav_row.append(InlineKeyboardButton("➡️ Next", callback_data=f"base_uk_{price}_{page + 1}"))
            
        if page > 0:
            nav_row.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"base_uk_{price}_{page - 1}"))
            
        if nav_row:
            keyboard.append(nav_row)
            
        keyboard.append([
            InlineKeyboardButton("◀ Previous Menu", callback_data="fullz_uk"),
            InlineKeyboardButton("🌍 Main Menu", callback_data="back_to_start")
        ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")

    # Handling Clean AU Base Lists with Pagination System and navigation buttons (matching UK layout exactly)
    elif query.data.startswith("base_au_"):
        parts = query.data.split("_")
        price = int(parts[2])
        page = int(parts[3])
        
        bases_map = {30: AU_30_BASES, 20: AU_20_BASES, 10: AU_10_BASES, 5: AU_5_BASES}
        bases_list = bases_map.get(price, [])
        
        items_per_page = 10
        total_pages = max(1, (len(bases_list) + items_per_page - 1) // items_per_page)
        
        if page >= total_pages:
            page = 0
        
        start_idx = page * items_per_page
        end_idx = start_idx + items_per_page
        current_slice = bases_list[start_idx:end_idx]
        
        text = (
            f"🇦🇺 **AU £{price} Base** (Page {page + 1}/{total_pages})\n\n"
            f"Tap an item to select:"
        )
        
        keyboard = []
        for bin_num in current_slice:
            keyboard.append([InlineKeyboardButton(str(bin_num), callback_data=f"au_buy_{price}_{bin_num}")])
            
        nav_row = []
        nav_row.append(InlineKeyboardButton("🔄 Refresh", callback_data=f"base_au_{price}_{page}"))
        
        if page < total_pages - 1:
            nav_row.append(InlineKeyboardButton("➡️ Next", callback_data=f"base_au_{price}_{page + 1}"))
            
        if page > 0:
            nav_row.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"base_au_{price}_{page - 1}"))
            
        if nav_row:
            keyboard.append(nav_row)
            
        keyboard.append([
            InlineKeyboardButton("◀ Previous Menu", callback_data="fullz_au"),
            InlineKeyboardButton("🌍 Main Menu", callback_data="back_to_start")
        ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")

    elif query.data in ["us_5", "us_10", "us_20", "us_30"]:
        await query.edit_message_text(
            f"You selected: **{query.data.upper().replace('_', ' ')}**\n\n"
            "(I will put the real content here when you send it)",
            parse_mode="Markdown"
        )

    elif query.data == "wallet":
        await query.edit_message_text("Wallet info:\n\n(Add your payment addresses here)")

    elif query.data == "help":
        await query.edit_message_text("Help:\n\n• /start – show stock again\n• Contact admin for support")

    elif query.data == "back_to_start":
        text = (
            f"+ニニ Stock ニニニ+\n"
            f"• Leads: {LEADS}\n"
            f"| Fullz: {FULLZ}\n"
            f"=== Stock ==+\n\n"
            f"Choose an option below:"
        )
        keyboard = [
            [
                InlineKeyboardButton("Leads", callback_data="leads"),
                InlineKeyboardButton("Fullz", callback_data="fullz"),
            ],
            [
                InlineKeyboardButton("Wallet", callback_data="wallet"),
                InlineKeyboardButton("Help", callback_data="help"),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup)

def main():
    if not TOKEN:
        raise ValueError("BOT_TOKEN is missing from your environment or .env file.")
        
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()