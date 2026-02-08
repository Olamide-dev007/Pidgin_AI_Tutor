"""
Telegram Bot for Pidgin AI Tutor
Allows users to learn via Telegram messaging app
"""

import os
import logging
import json
from datetime import datetime

# Check if telegram library is available
try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import (
        Application,
        CommandHandler,
        MessageHandler,
        CallbackQueryHandler,
        ContextTypes,
        filters
    )
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    print("⚠️  python-telegram-bot not installed!")
    print("To use Telegram bot, install: pip install python-telegram-bot")

from chatbot import PidginChatbot, RuleBasedFallback

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize chatbot
try:
    chatbot = PidginChatbot("models/fine_tuned_pidgin")
    MODEL_LOADED = True
    logger.info("AI model loaded successfully")
except Exception as e:
    logger.warning(f"Could not load AI model: {e}. Using rule-based responses.")
    MODEL_LOADED = False

# Store user data
user_data = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message"""
    user = update.effective_user
    user_id = user.id
    
    # Initialize user data
    if user_id not in user_data:
        user_data[user_id] = {
            'name': user.first_name,
            'messages': [],
            'topic': 'general',
            'started': datetime.now().isoformat()
        }
    
    welcome_message = f"""
🎓 *Welcome to Pidgin AI Tutor!* 🎓

Hello {user.first_name}! 👋

I be AI wey dey teach Mathematics and Coding for Nigerian Pidgin English.

*Wetin I fit do for you:*
📐 Mathematics (Addition, Algebra, Fractions, etc.)
💻 Coding (Python basics, Variables, Loops, etc.)
💬 Answer your questions in Pidgin

*How to use me:*
Just send me your question for Pidgin or English!

*Example Questions:*
• "Wetin be algebra?"
• "How I go add 15 + 28?"
• "Teach me Python"
• "Wetin be variable?"

Type /help to see all commands.
Let's learn together! 📚
    """
    
    keyboard = [
        [
            InlineKeyboardButton("📐 Learn Math", callback_data='topic_math'),
            InlineKeyboardButton("💻 Learn Coding", callback_data='topic_coding')
        ],
        [InlineKeyboardButton("❓ Help", callback_data='help')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        welcome_message,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send help message"""
    help_text = """
*📚 Pidgin AI Tutor - Help*

*Commands:*
/start - Start the bot
/help - Show this help
/topic - Change topic
/stats - View your stats
/clear - Clear chat history
/feedback - Send feedback

*Topics:*
📐 Mathematics
💻 Coding (Python)

*How to Ask:*
Just type your question naturally!

Examples:
• "Wetin be Python?"
• "Calculate 5 × 8"
• "How I go write if statement?"

I dey here to help! 🎓
    """
    
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def topic_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Change topic"""
    keyboard = [
        [
            InlineKeyboardButton("📐 Mathematics", callback_data='topic_math'),
            InlineKeyboardButton("💻 Coding", callback_data='topic_coding')
        ],
        [InlineKeyboardButton("💬 General Chat", callback_data='topic_general')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Wetin you wan learn? Choose your topic:",
        reply_markup=reply_markup
    )


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user statistics"""
    user_id = update.effective_user.id
    
    if user_id not in user_data:
        await update.message.reply_text("Use /start first!")
        return
    
    data = user_data[user_id]
    message_count = len(data.get('messages', []))
    topic = data.get('topic', 'general')
    started = data.get('started', 'Unknown')
    
    stats_text = f"""
📊 *Your Learning Stats* 📊

👤 Name: {data.get('name', 'User')}
📅 Started: {started[:10]}
💬 Messages: {message_count}
📚 Topic: {topic.capitalize()}

Keep learning! 🌟
    """
    
    await update.message.reply_text(stats_text, parse_mode='Markdown')


async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Clear conversation"""
    user_id = update.effective_user.id
    
    if user_id in user_data:
        user_data[user_id]['messages'] = []
    
    await update.message.reply_text("✅ Chat cleared! Make we start fresh. 🆕")


async def feedback_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Request feedback"""
    keyboard = [
        [
            InlineKeyboardButton("⭐", callback_data='feedback_1'),
            InlineKeyboardButton("⭐⭐", callback_data='feedback_2'),
            InlineKeyboardButton("⭐⭐⭐", callback_data='feedback_3'),
        ],
        [
            InlineKeyboardButton("⭐⭐⭐⭐", callback_data='feedback_4'),
            InlineKeyboardButton("⭐⭐⭐⭐⭐", callback_data='feedback_5'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "💬 *Rate your experience:*\n\nHow many stars you go give me?",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user messages"""
    user = update.effective_user
    user_id = user.id
    user_message = update.message.text
    
    # Initialize user
    if user_id not in user_data:
        user_data[user_id] = {
            'name': user.first_name,
            'messages': [],
            'topic': 'general',
            'started': datetime.now().isoformat()
        }
    
    # Log message
    user_data[user_id]['messages'].append({
        'user': user_message,
        'timestamp': datetime.now().isoformat()
    })
    
    # Typing indicator
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action='typing'
    )
    
    # Generate response
    try:
        if MODEL_LOADED:
            response = chatbot.generate_response(user_message)
        else:
            fallback = RuleBasedFallback.get_response(user_message)
            response = fallback if fallback else "I dey learn to answer that. Try ask me about Math or Python!"
        
        user_data[user_id]['messages'][-1]['bot'] = response
        
        await update.message.reply_text(response)
        
        # Ask for feedback occasionally
        if len(user_data[user_id]['messages']) % 5 == 0:
            keyboard = [[
                InlineKeyboardButton("👍 Good", callback_data='quick_good'),
                InlineKeyboardButton("👎 Bad", callback_data='quick_bad')
            ]]
            await update.message.reply_text(
                "Was this helpful?",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text("Sorry, I get small problem. Try again! 🔧")


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button clicks"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    if user_id not in user_data:
        user_data[user_id] = {
            'name': query.from_user.first_name,
            'messages': [],
            'topic': 'general',
            'started': datetime.now().isoformat()
        }
    
    # Topic selection
    if data.startswith('topic_'):
        topic = data.replace('topic_', '')
        user_data[user_id]['topic'] = topic
        
        messages = {
            'math': "📐 Great! Let's learn Math! Ask me anything.",
            'coding': "💻 Awesome! Let's learn Coding!",
            'general': "💬 Okay! How I fit help you?"
        }
        
        await query.edit_message_text(messages.get(topic, "Topic selected!"))
    
    # Help
    elif data == 'help':
        await help_command(update, context)
    
    # Feedback
    elif data.startswith('feedback_'):
        rating = data.replace('feedback_', '')
        save_telegram_feedback(user_id, rating)
        await query.edit_message_text(f"Thank you! You gave {rating} stars! ⭐")
    
    elif data.startswith('quick_'):
        sentiment = data.replace('quick_', '')
        save_telegram_feedback(user_id, sentiment)
        await query.edit_message_text("Thanks for feedback! 🙏")


def save_telegram_feedback(user_id, rating):
    """Save feedback"""
    os.makedirs("data", exist_ok=True)
    
    feedback = {
        'user_id': user_id,
        'name': user_data.get(user_id, {}).get('name', 'Unknown'),
        'rating': rating,
        'timestamp': datetime.now().isoformat()
    }
    
    try:
        with open('data/telegram_feedback.json', 'r') as f:
            all_feedback = json.load(f)
    except FileNotFoundError:
        all_feedback = []
    
    all_feedback.append(feedback)
    
    with open('data/telegram_feedback.json', 'w') as f:
        json.dump(all_feedback, f, indent=2)


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors"""
    logger.error(f"Update {update} caused error {context.error}")


def main():
    """Start the bot"""
    if not TELEGRAM_AVAILABLE:
        print("❌ Cannot start bot: python-telegram-bot not installed")
        print("Install with: pip install python-telegram-bot")
        return
    
    TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN not set!")
        print("\nSteps:")
        print("1. Message @BotFather on Telegram")
        print("2. Send /newbot")
        print("3. Get your token")
        print("4. Set it: export TELEGRAM_BOT_TOKEN='your-token'")
        return
    
    # Create application
    application = Application.builder().token(TOKEN).build()
    
    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("topic", topic_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("clear", clear_command))
    application.add_handler(CommandHandler("feedback", feedback_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)
    
    print("🤖 Pidgin AI Tutor Bot is starting...")
    print(f"📱 Model loaded: {MODEL_LOADED}")
    print("✅ Bot running! Press Ctrl+C to stop.\n")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()