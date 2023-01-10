import json
import logging
import pydere
import re
import requests
import szuru_importer
import traceback
import os

from requests.auth import HTTPDigestAuth
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, ContextTypes, CommandHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

token = os.environ['TELEGRAM_BOT_TOKEN']

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please give me links!")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        url = re.search("(?P<url>https?://[^\s]+)", update.message.text).group("url")
        response = "Try to get '" + url + "'"
        logging.info(response)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response)

        board = re.search("https?://(?P<board>[^/]+)", url).group("board")
        id = re.search("https?://[a-z./]+(?P<id>[0-9]+)", url).group("id")
        board_tag = board+"_"+id

        response = "add post " + id + " from " + board
        logging.info(response)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response)

        if not szuru_importer.szuruHasTag(board_tag):
            post = pydere.Post(board, id)

            tagsAdded = szuru_importer.addTags(board, post.tags)

            response = "create Szuru post"
            logging.info(response)
            await context.bot.send_message(chat_id=update.effective_chat.id, text=response)
            szuru_importer.createSzuruPost(post.file, post.tags.split(), post.rating, post.source, board_tag)

            response = "Success!"
            logging.info(response)
            await context.bot.send_message(chat_id=update.effective_chat.id, text=response)
    except:
        response = traceback.format_exc()
        logging.info(response)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response)


if __name__ == '__main__':
    application = ApplicationBuilder().token(token).build()

    start_handler = CommandHandler('start', start)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)

    application.add_handler(start_handler)
    application.add_handler(echo_handler)

    application.run_polling()
