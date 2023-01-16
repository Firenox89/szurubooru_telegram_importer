import logging
import pydere
import re
import szuru_importer
import traceback
import os

from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, ContextTypes, CommandHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

token = os.environ['TELEGRAM_BOT_TOKEN']


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please give me links!")


async def handle_img(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        file_id = update.message.document.file_id
        new_file = await context.bot.get_file(file_id)
        path = await new_file.download_to_drive()
        szuru_importer.create_szuru_post_from_file(path)
        os.remove(path)
    except:
        response = traceback.format_exc()
        logging.info(response)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response)

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        url = re.search(r"(?P<url>https?://\S+)", update.message.text).group("url")

        board = re.search("https?://(?P<board>[^/]+)", url).group("board")
        id = re.search("https?://[a-z./]+(?P<id>[0-9]+)", url).group("id")
        board_tag = board + "_" + id

        if not szuru_importer.szuruHasTag(board_tag):
            if board == "www.pixiv.net":
                response = "Pixiv is not supported!"
                logging.info(response)
                await context.bot.send_message(chat_id=update.effective_chat.id, text=response)
                return
                #post = pydere.Pixiv(url, id)
            elif board == "danbooru.donmai.us":
                post = pydere.DanPost(id)
            else:
                post = pydere.Post(board, id)

            tagsAdded = szuru_importer.addTags(board, post.tags)

            szuru_importer.createSzuruPost(post.file, post.tags.split(), post.rating, post.source, board_tag)

            response = "Created Post and " + str(tagsAdded) + " tags!"
            logging.info(response)
            await context.bot.send_message(chat_id=update.effective_chat.id, text=response)
    except:
        response = traceback.format_exc()
        logging.info(response)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response)


if __name__ == '__main__':
    application = ApplicationBuilder().token(token).build()


    start_handler = CommandHandler('start', start)
    link_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), handle_link)
    img_handler = MessageHandler(filters.Document.ALL, handle_img)

    application.add_handler(start_handler)
    application.add_handler(link_handler)
    application.add_handler(img_handler)

    application.run_polling()
