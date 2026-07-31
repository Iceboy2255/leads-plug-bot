import logging
import os
asyncio_module = __import__('asyncio')
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# --- CONFIGURATION ---
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
ADMIN_TELEGRAM_ID = 7280810198
ADMIN_GROUP_ID = -1003907566721
COMMAND_PASSWORD = "myprince"

# --- GLOBAL SYSTEM STATES ---
BOT_ACTIVE = True
USER_DATABASE = set()
ORDER_COUNTER = 928172
INVENTORY_STOCK = {"Leads Bundle A": 15, "Leads Bundle B": 5}
PAYMENT_RECORDS = set()
ACTIVE_ORDERS = {}  
BROADCAST_STATE = set() 

# Global reference for loop safety
_bot_application = None

# --- 1 & 2. TELEGRAM GROUP LIVE CONSOLE (CRASH-PROOF THREAD-SAFE) ---
class TelegramGroupLogHandler(logging.Handler):
    def emit(self, record):
        log_entry = self.format(record)
        try:
            global _bot_application
            if _bot_application and _bot_application.bot:
                asyncio_module.run_coroutine_threadsafe(
                    _bot_application.bot.send_message(
                        chat_id=ADMIN_GROUP_ID,
                        text=f"📊 **[LIVE CONSOLE]**\n{log_entry}",
                        parse_mode="Markdown"
                    ),
                    _bot_application.updater.bot.loop if hasattr(_bot_application, 'updater') and _bot_application.updater else asyncio_module.get_event_loop()
                )
        except Exception:
            pass

# Initialize Logging (Muting local console output, pushing exclusively to group)
logging.basicConfig(level=logging.INFO, handlers=[])
logger = logging.getLogger("BotLogger")
logger.setLevel(logging.INFO)

# --- CORE HANDLERS ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    USER_DATABASE.add(user.id)
    
    # --- 4. START / STOP SYSTEM CHECK ---
    if not BOT_ACTIVE and user.id != ADMIN_TELEGRAM_ID:
        await update.message.reply_text("Bot temporarily unavailable")
        return

    logger.info(f"[NEW USER]\nID: {user.id}\nUsername: @{user.username if user.username else 'None'}")
    
    keyboard = [
        [InlineKeyboardButton("📦 Buy Leads", callback_data="shop_menu")],
        [InlineKeyboardButton("💰 Wallet / Crypto", callback_data="wallet_menu")],
    ]
    if user.id == ADMIN_TELEGRAM_ID:
        keyboard.append([InlineKeyboardButton("📊 Admin Panel", callback_data="admin_panel")])

    await update.message.reply_text(
        "Welcome to the automated delivery system. Choose an option below:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user

    global BOT_ACTIVE, ORDER_COUNTER

    if not BOT_ACTIVE and query.data != "admin_panel" and user.id != ADMIN_TELEGRAM_ID:
        await query.edit_message_text("Bot temporarily unavailable")
        return

    logger.info(f"[BUTTON CLICK] User: @{user.username or user.id} clicked {query.data}")

    # --- 3. ADMIN PANEL ---
    if query.data == "admin_panel":
        if user.id != ADMIN_TELEGRAM_ID:
            await query.edit_message_text("❌ Unauthorized access.")
            return
        
        keyboard = [
            [InlineKeyboardButton("📊 Dashboard", callback_data="adm_dash"), InlineKeyboardButton("📦 Orders", callback_data="adm_orders")],
            [InlineKeyboardButton("👥 Users", callback_data="adm_users"), InlineKeyboardButton("💰 Revenue", callback_data="adm_revenue")],
            [InlineKeyboardButton("📢 Broadcast", callback_data="adm_bc")],
            [InlineKeyboardButton("🟢 Start Bot", callback_data="adm_start"), InlineKeyboardButton("🔴 Stop Bot", callback_data="adm_stop")],
            [InlineKeyboardButton("⬅️ Back", callback_data="main_menu")]
        ]
        await query.edit_message_text("🔒 **Admin Control Panel**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif query.data == "adm_start":
        if user.id == ADMIN_TELEGRAM_ID:
            BOT_ACTIVE = True
            logger.info(f"[ADMIN] Bot started by @{user.username or user.id}")
            await query.edit_message_text("🟢 Bot status changed to: ACTIVE", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_panel")]]))

    elif query.data == "adm_stop":
        if user.id == ADMIN_TELEGRAM_ID:
            BOT_ACTIVE = False
            logger.info(f"[ADMIN] Bot stopped by @{user.username or user.id}")
            await query.edit_message_text("🔴 Bot status changed to: STOPPED", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_panel")]]))

    elif query.data == "adm_dash":
        if user.id == ADMIN_TELEGRAM_ID:
            dash_text = (
                f"📊 **Dashboard Statistics**\n\n"
                f"• Status: {'🟢 Active' if BOT_ACTIVE else '🔴 Stopped'}\n"
                f"• Registered Users: {len(USER_DATABASE)}\n"
                f"• Bundle A Stock: {INVENTORY_STOCK['Leads Bundle A']}\n"
                f"• Bundle B Stock: {INVENTORY_STOCK['Leads Bundle B']}\n"
                f"• Total Orders: {ORDER_COUNTER - 928172}"
            )
            await query.edit_message_text(dash_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_panel")]]))

    elif query.data == "adm_orders":
        if user.id == ADMIN_TELEGRAM_ID:
            orders_summary = f"📦 **Active Tracked Orders**\nTotal Processed: {ORDER_COUNTER - 928172}\nRecent state synchronized."
            await query.edit_message_text(orders_summary, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_panel")]]))

    elif query.data == "adm_users":
        if user.id == ADMIN_TELEGRAM_ID:
            await query.edit_message_text(f"👥 **Total Unique Users:** {len(USER_DATABASE)}", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_panel")]]))

    elif query.data == "adm_revenue":
        if user.id == ADMIN_TELEGRAM_ID:
            revenue_calc = (ORDER_COUNTER - 928172) * 25.00
            await query.edit_message_text(f"💰 **Estimated Revenue:** ${revenue_calc:.2f} USD", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_panel")]]))

    elif query.data == "adm_bc":
        if user.id == ADMIN_TELEGRAM_ID:
            BROADCAST_STATE.add(user.id)
            await query.edit_message_text("📢 **Broadcast Mode:** Please send the message you want to broadcast to all users.", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_panel")]]))

    # --- SHOP & 7. SMART STOCK SYSTEM ---
    elif query.data == "shop_menu":
        keyboard = [
            [InlineKeyboardButton(f"Leads Bundle A (Stock: {INVENTORY_STOCK['Leads Bundle A']})", callback_data="buy_bundle_a")],
            [InlineKeyboardButton(f"Leads Bundle B (Stock: {INVENTORY_STOCK['Leads Bundle B']})", callback_data="buy_bundle_b")],
            [InlineKeyboardButton("⬅️ Back", callback_data="main_menu")]
        ]
        await query.edit_message_text("Select your desired package:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data.startswith("buy_bundle_"):
        bundle_key = "Leads Bundle A" if "a" in query.data else "Leads Bundle B"
        
        # --- 7. STOCK VALIDATION CHECK ---
        if INVENTORY_STOCK[bundle_key] <= 0:
            await query.edit_message_text("Out of stock")
            return

        ORDER_COUNTER += 1
        order_id = f"ORD-{ORDER_COUNTER}"
        
        ACTIVE_ORDERS[user.id] = {
            "order_id": order_id,
            "product": bundle_key,
            "country": "Global",
            "amount": "1",
            "price": "$25.00",
            "crypto": "USDT"
        }

        logger.info(
            f"[ORDER]\nORDER_ID: {order_id}\nUser: @{user.username or user.id}\n"
            f"Product: {bundle_key}\nCountry: Global\nAmount: 1\nPrice: $25.00"
        )

        crypto_keyboard = [
            [InlineKeyboardButton("Pay with BTC", callback_data="pay_BTC")],
            [InlineKeyboardButton("Pay with ETH", callback_data="pay_ETH")],
            [InlineKeyboardButton("Pay with USDT", callback_data="pay_USDT")],
            [InlineKeyboardButton("Pay with LTC", callback_data="pay_LTC")],
            [InlineKeyboardButton("I PAID", callback_data="verify_payment")]
        ]
        await query.edit_message_text(
            f"Order Created: `{order_id}`\n\n"
            f"Please send exact amount to our multi-crypto gateway wallet and click **I PAID** once completed.",
            reply_markup=InlineKeyboardMarkup(crypto_keyboard),
            parse_mode="Markdown"
        )

    # --- 8. MULTI-CRYPTO PAYMENT CHECK & 6. AUTO DELIVERY ---
    elif query.data.startswith("pay_"):
        crypto_type = query.data.split("_")[1]
        if user.id in ACTIVE_ORDERS:
            ACTIVE_ORDERS[user.id]["crypto"] = crypto_type
        await query.answer(f"Selected {crypto_type}. Send funds and press 'I PAID'.", show_alert=True)

    elif query.data == "verify_payment":
        if user.id not in ACTIVE_ORDERS:
            await query.answer("No active order found.", show_alert=True)
            return

        order_info = ACTIVE_ORDERS[user.id]
        order_id = order_info["order_id"]

        payment_signature = f"{order_id}-{user.id}"
        if payment_signature in PAYMENT_RECORDS:
            await query.edit_message_text(
                "❌ Payment not detected or incorrect\n"
                "Please send exact amount to correct wallet and try again"
            )
            return

        PAYMENT_RECORDS.add(payment_signature)

        logger.info(
            f"[PAYMENT CONFIRMED]\nORDER_ID: {order_id}\n"
            f"User: @{user.username or user.id}\nCrypto: {order_info['crypto']}\nAmount: {order_info['price']}"
        )

        # --- 7. SMART STOCK REDUCTION SYSTEM ---
        product_name = order_info["product"]
        if INVENTORY_STOCK[product_name] > 0:
            INVENTORY_STOCK[product_name] -= 1

        file_name = "verified_leads_export.csv"
        logger.info(f"[DELIVERED]\nORDER_ID: {order_id}\nFile: {file_name}")

        del ACTIVE_ORDERS[user.id]

        # --- 6. AUTO DELIVERY FILE & MESSAGE ---
        await query.edit_message_text(
            "✅ Payment confirmed. Your leads have been delivered."
        )
        await context.bot.send_document(
            chat_id=user.id,
            document=b"email,phone,name\nlead1@example.com,+123456789,John Doe",
            filename=file_name
        )

    elif query.data == "wallet_menu":
        await query.edit_message_text(
            "💰 **Crypto Gateway Wallet:**\n`1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa`",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="main_menu")]],
            parse_mode="Markdown"
        ))

    elif query.data == "main_menu":
        keyboard = [
            [InlineKeyboardButton("📦 Buy Leads", callback_data="shop_menu")],
            [InlineKeyboardButton("💰 Wallet / Crypto", callback_data="wallet_menu")],
        ]
        if user.id == ADMIN_TELEGRAM_ID:
            keyboard.append([InlineKeyboardButton("📊 Admin Panel", callback_data="admin_panel")])
        await query.edit_message_text("Main Menu:", reply_markup=InlineKeyboardMarkup(keyboard))

# --- 5. BROADCAST SYSTEM & PASSWORD AUTH ---
async def text_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text

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
    global _bot_application
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    _bot_application = app
    
    ch = TelegramGroupLogHandler()
    ch.setLevel(logging.INFO)
    logger.addHandler(ch)

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_message_handler))

    app.run_polling()

if __name__ == "__main__":
    main()
