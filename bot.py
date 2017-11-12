from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
import logging
import os
import numpy as np
from recipe_manager import RecipeManager


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

TOKEN = os.environ.get('TELEGRAM_TOKEN', None)

def start(bot, update):
    """Send a message when the command /start is issued."""
    update.message.reply_text("""Hi! Holly here, your friendly culinary assistant. Send /help to see what I can do!
                             """)

def help(bot, update):
    """Send a message when the command /help is issued."""
    update.message.reply_text("""1. Search for anything and I'll show matching recipes\n2. Send /browse to look through all my recipes""")

def show_recipes(bot, update):
    "Return recipes matching message"
    m = RecipeManager()
    recipes = m.lookupRecipe(update.message.text.lower())
    for name, method in recipes:
        update.message.reply_text(name+'\n\n'+method)
    if len(recipes)==0:
        update.message.reply_text("Sorry, I don't know any recipes for %s" %
                                  update.message.text)

def list_categories(bot, update):
    "List recipe categories"
    m = RecipeManager()

    keyboard = [[InlineKeyboardButton('%s\n'%category, callback_data=category)] for
                 category in m.listRecipeCategories()]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Choose a category:', reply_markup=reply_markup)


def manage_callback(bot, update):
    cb_data = update.callback_query.data
    m = RecipeManager()
    if update.callback_query.message.text == 'Choose a category:':
        "List recipes in category"
        category = cb_data
        keyboard = [InlineKeyboardButton(recipe, callback_data=recipe) for
                     recipe in m.listRecipes(category)]
        if len(keyboard) % 2 == 0:
            keyboard = np.reshape(keyboard, (len(keyboard) / 2,2))
        else:
            keyboard = [[key] for key in keyboard]
        reply_markup = InlineKeyboardMarkup(keyboard)

        bot.edit_message_text(text='Choose a recipe:',
                          reply_markup=reply_markup,
                          chat_id=update.callback_query.message.chat_id,
                          message_id=update.callback_query.message.message_id)
    elif update.callback_query.message.text == 'Choose a recipe:':
        "Show selected recipe"
        recipe = cb_data
        name, method = m.lookupRecipe(recipe, exact_match=True)
        bot.edit_message_text(text=name+'\n\n'+method,
                              chat_id=update.callback_query.message.chat_id,
                              message_id=update.callback_query.message.message_id)

def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    """Start the bot."""
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    dp.add_handler(CommandHandler('browse', list_categories))
    dp.add_handler(CallbackQueryHandler(manage_callback))

    dp.add_handler(MessageHandler(Filters.text, show_recipes))
    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
