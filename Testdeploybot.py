from telethon import TelegramClient
from telethon.tl.functions.account import ReportPeerRequest
from telethon.tl.types import (
    InputReportReasonSpam,
    InputReportReasonFake,
    InputReportReasonViolence,
    InputReportReasonPornography,
    InputReportReasonChildAbuse,
    InputReportReasonCopyright,
    InputReportReasonIllegalDrugs,
    InputReportReasonPersonalDetails,
    InputReportReasonOther
)
import time
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext
import logging

# Set up logging to capture errors
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the conversation states
SELECT_MODE, REPORT_TYPE, REPORT_REASON, POST_LINK, NUM_REPORTS, ENTITY_USERNAME = range(6)

# API credentials (should be hardcoded or retrieved from environment variables for security)
api_id = 'YOUR_API_ID'
api_hash = 'YOUR_API_HASH'

# Telegram bot token (replace with your bot's token)
bot_token = 'YOUR_BOT_TOKEN'

# Report reasons
report_reasons = {
    1: ("I don't like it", InputReportReasonOther()),
    2: ("Child abuse", InputReportReasonChildAbuse()),
    3: ("Violence", InputReportReasonViolence()),
    4: ("Illegal goods", InputReportReasonIllegalDrugs()),
    5: ("Illegal adult content", InputReportReasonPornography()),
    6: ("Personal data", InputReportReasonPersonalDetails()),
    7: ("Terrorism", InputReportReasonViolence()),
    8: ("Scam or spam", InputReportReasonSpam()),
    9: ("Copyright", InputReportReasonCopyright()),
    10: ("Other", InputReportReasonOther())
}

# Start command - bot will respond with instructions
def start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Welcome! This bot allows you to report accounts, channels, groups, and posts.\n"
                              "Type /report to start reporting.")
    return ConversationHandler.END

# Function to handle reporting options
def report(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Choose what you want to report:\n"
                              "1: Account\n2: Channel\n3: Group\n4: Bot\n5: Post Link\n"
                              "Please enter a number from 1 to 5.")
    return REPORT_TYPE

# Handle the report type selection
def report_type(update: Update, context: CallbackContext) -> int:
    report_type = update.message.text
    if report_type == "1":
        context.user_data['report_type'] = "account"
    elif report_type == "2":
        context.user_data['report_type'] = "channel"
    elif report_type == "3":
        context.user_data['report_type'] = "group"
    elif report_type == "4":
        context.user_data['report_type'] = "bot"
    elif report_type == "5":
        context.user_data['report_type'] = "post"
    else:
        update.message.reply_text("Invalid input. Please enter a number between 1 and 5.")
        return REPORT_TYPE

    update.message.reply_text("Please choose the reason for the report:\n"
                              "1: I don't like it\n2: Child abuse\n3: Violence\n4: Illegal goods\n"
                              "5: Illegal adult content\n6: Personal data\n7: Terrorism\n8: Scam or spam\n"
                              "9: Copyright\n10: Other\nPlease enter a number from 1 to 10.")
    return REPORT_REASON

# Handle the reason selection
def report_reason(update: Update, context: CallbackContext) -> int:
    reason_choice = int(update.message.text)
    if reason_choice not in report_reasons:
        update.message.reply_text("Invalid reason. Please choose a number from 1 to 10.")
        return REPORT_REASON

    context.user_data['reason'] = report_reasons[reason_choice][1]
    context.user_data['reason_text'] = report_reasons[reason_choice][0]

    if context.user_data['report_type'] == "post":
        update.message.reply_text("Please provide the full post link (e.g., https://t.me/channel/12345).")
        return POST_LINK
    else:
        update.message.reply_text("Please provide the username or ID of the entity (e.g., @username).")
        return ENTITY_USERNAME

# Handle the post link
def post_link(update: Update, context: CallbackContext) -> int:
    post_link = update.message.text
    context.user_data['post_link'] = post_link
    update.message.reply_text("How many reports would you like to submit?")
    return NUM_REPORTS

# Handle the number of reports
def num_reports(update: Update, context: CallbackContext) -> int:
    try:
        num_reports = int(update.message.text)
        context.user_data['num_reports'] = num_reports
    except ValueError:
        update.message.reply_text("Invalid number. Please enter a valid integer.")
        return NUM_REPORTS

    update.message.reply_text("Proceeding with the report(s)...")
    # Initiate report submission in Telethon
    context.job_queue.run_once(submit_report, 0, context=context)
    return ConversationHandler.END

# Handle the entity username (for non-post reports)
def entity_username(update: Update, context: CallbackContext) -> int:
    entity_username = update.message.text
    context.user_data['entity_username'] = entity_username
    update.message.reply_text("How many reports would you like to submit?")
    return NUM_REPORTS

# Function to submit the report(s)
async def submit_report(context: CallbackContext) -> None:
    try:
        # Fetch client and session
        session_str = 'YOUR_SESSION_STRING'  # Replace with a valid string session
        client = TelegramClient('report_session', api_id, api_hash, string_session=session_str)
        await client.start()

        if context.user_data['report_type'] == "post":
            post_link = context.user_data['post_link']
            parts = post_link.replace("https://t.me/", "").split("/")
            channel_username = parts[0]
            message_id = int(parts[1])
            channel = await client.get_entity(channel_username)

            for i in range(context.user_data['num_reports']):
                await client(ReportPeerRequest(
                    peer=channel,
                    reason=context.user_data['reason'],
                    message=f"Reported post ID {message_id} for {context.user_data['reason_text']}"
                ))
                time.sleep(2)  # To avoid rate limiting
            update.message.reply_text(f"{context.user_data['num_reports']} reports submitted for the post.")

        else:
            entity_username = context.user_data['entity_username']
            entity = await client.get_entity(entity_username)

            for i in range(context.user_data['num_reports']):
                await client(ReportPeerRequest(
                    peer=entity,
                    reason=context.user_data['reason'],
                    message=f"Reported for {context.user_data['reason_text']}"
                ))
                time.sleep(2)
            update.message.reply_text(f"{context.user_data['num_reports']} reports submitted for the entity.")
        
        await client.disconnect()

    except Exception as e:
        update.message.reply_text(f"Error occurred while reporting: {str(e)}")

# Set up the conversation handler
conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start), CommandHandler('report', report)],
    states={
        REPORT_TYPE: [MessageHandler(Filters.text & ~Filters.command, report_type)],
        REPORT_REASON: [MessageHandler(Filters.text & ~Filters.command, report_reason)],
        POST_LINK: [MessageHandler(Filters.text & ~Filters.command, post_link)],
        NUM_REPORTS: [MessageHandler(Filters.text & ~Filters.command, num_reports)],
        ENTITY_USERNAME: [MessageHandler(Filters.text & ~Filters.command, entity_username)],
    },
    fallbacks=[]
)

# Main function to run the bot
def main():
    updater = Updater(bot_token, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
