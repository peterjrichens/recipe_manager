from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from telegram import ReplyKeyboardMarkup
import logging
import os
from recipe_manager import RecipeManager


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

TOKEN = os.environ.get('TELEGRAM_TOKEN', None)

SELECTED_CATEGORY, SELECTED_RECIPE, EXIT_BROWSE = range(3)

# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    """Send a message when the command /start is issued."""
    update.message.reply_text("""Hi! Holly here, your friendly culinary
                              assistant\nsend /help to see what I can do!
                             """)


def help(bot, update):
    """Send a message when the command /help is issued."""
    update.message.reply_text("""1. Search for anything and I'll show matching
                              recipes\n2. Send /browse to look through all my recipes
                             """)

def show_recipes(bot, update):
    "Return recipes matching message"
    m = RecipeManager()
    recipes = m.lookupRecipe(update.message.text.lower())
    for name, method in recipes:
        update.message.reply_text(name+'\n\n'+method)
    if len(recipes)==0:
        update.message.reply_text("Sorry, I don't know any recipes for %s" %
                                  update.message.text)
    return EXIT_BROWSE

def list_categories(bot, update):
    "List recipe categories"
    m = RecipeManager()
    reply_keyboard = [m.listRecipeCategories()]
    update.message.reply_text(
        'Which would you like to see?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard,resize_keyboard=True,
                                         one_time_keyboard=True))
    return SELECTED_CATEGORY

def list_recipes(bot, update):
    "List recipes in category"
    category = update.message.text
    m = RecipeManager()
    reply_keyboard = [m.listRecipes(category)]
    update.message.reply_text(
        'Here are the recipes have I under %s' % category,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard,resize_keyboard=True,
                                         one_time_keyboard=True))
    return SELECTED_RECIPE

def end_conversation(bot, update):
    logger.info("%s\n Ending the conversation.", update)
    return ConversationHandler.END

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

    # on noncommand i.e message - echo the message on Telegram

    browse_handler = ConversationHandler(
        entry_points=[CommandHandler('browse', list_categories)],

        states={
            SELECTED_CATEGORY: [MessageHandler(Filters.text, list_recipes)],

            SELECTED_RECIPE: [MessageHandler(Filters.text, show_recipes)],

            EXIT_BROWSE: [MessageHandler(Filters.text, end_conversation)]
        },

        fallbacks=[CommandHandler('cancel', end_conversation)]
    )

    dp.add_handler(browse_handler)

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
