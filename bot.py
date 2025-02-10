from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
import logging
import config

logging.basicConfig(level=logging.INFO)

# Bot Client
bot = TelegramClient("report_bot", config.API_ID, config.API_HASH).start(bot_token=config.BOT_TOKEN)

# User Clients (Mass Reporting Accounts)
session_clients = []
for session in config.SESSION_STRINGS:
    client = TelegramClient(StringSession(session), config.API_ID, config.API_HASH)
    session_clients.append(client)

async def start_sessions():
    for client in session_clients:
        try:
            await client.start()
            logging.info("✅ Started a new session successfully!")
        except Exception as e:
            logging.error(f"❌ Error starting session: {e}")

@bot.on(events.NewMessage(pattern="/start"))
async def start(event):
    await event.reply("👋 **Welcome to Mass Report Bot!**\nUse `/report @username spam` to report.")

@bot.on(events.NewMessage(pattern="/help"))
async def help(event):
    help_text = "**Mass Report Bot Commands:**\n"
    help_text += "/report @username spam – Report a user\n"
    help_text += "/report @channel spam – Report a channel\n"
    help_text += "/addsession – Add a new session"
    await event.reply(help_text)

@bot.on(events.NewMessage(pattern=r"/report\s+(@\w+|\d+)\s+(\w+)"))
async def report(event):
    args = event.text.split()
    if len(args) < 3:
        return await event.reply("⚠️ Usage: `/report @username reason`")
    
    target = args[1]  # Username or ID
    reason_text = args[2].lower()

    # Mapping Report Reasons
    reasons = {
        "spam": "Spam",
        "violence": "Violence",
        "scam": "Scam",
        "child": "Child Abuse",
        "illegal": "Illegal Content",
        "terrorism": "Terrorism",
        "copyright": "Copyright Violation"
    }

    if reason_text not in reasons:
        return await event.reply("⚠️ Invalid reason! Use: spam, violence, scam, child, illegal, terrorism, copyright")

    reason = reasons[reason_text]
    success_count = 0
    failed_count = 0

    # Report using all sessions
    for client in session_clients:
        try:
            entity = await client.get_entity(target)
            await client.report_spam(entity)  # Reporting as spam
            success_count += 1
            logging.info(f"✅ Reported {target} for {reason}")
        except Exception as e:
            failed_count += 1
            logging.error(f"❌ Error reporting {target}: {e}")

    await event.reply(f"✅ {success_count} reports sent, ❌ {failed_count} failed.")

@bot.on(events.NewMessage(pattern="/addsession"))
async def add_session(event):
    await event.reply("📥 Send your **Telethon Session String** to add a new session.")

@bot.on(events.NewMessage())
async def new_session(event):
    if len(event.raw_text) > 20:  # Basic check for session string
        new_session = event.raw_text.strip()
        try:
            client = TelegramClient(StringSession(new_session), config.API_ID, config.API_HASH)
            await client.connect()
            if await client.is_user_authorized():
                session_clients.append(client)
                await event.reply("✅ New session added successfully!")
                logging.info("✅ New session added successfully!")
            else:
                await event.reply("⚠️ Invalid session string. Please try again.")
        except Exception as e:
            await event.reply("❌ Error adding session. Check logs for details.")
            logging.error(f"❌ Error adding session: {e}")

# Start bot and user clients
with bot:
    bot.loop.run_until_complete(start_sessions())
    bot.run_until_disconnected()
