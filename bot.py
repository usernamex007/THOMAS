from telethon import TelegramClient, events, Button
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
        await client.start()
        logging.info(f"Started session: {client.session.filename}")

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

    # Report using all sessions
    for client in session_clients:
        try:
            entity = await client.get_entity(target)
            await client.report(entity, reason=reason)
            logging.info(f"Reported {target} for {reason}")
        except Exception as e:
            logging.error(f"Error reporting {target}: {e}")

    await event.reply(f"✅ Successfully reported {target} for {reason}!")

@bot.on(events.NewMessage(pattern="/addsession"))
async def add_session(event):
    await event.reply("📥 Send your **Telethon Session String** to add a new session.")

@bot.on(events.NewMessage())
async def new_session(event):
    if "1" in event.raw_text:  # Placeholder to filter session strings
        new_session = event.raw_text.strip()
        session_clients.append(TelegramClient(StringSession(new_session), config.API_ID, config.API_HASH))
        await event.reply("✅ New session added successfully!")

# Start bot and user clients
with bot:
    bot.loop.run_until_complete(start_sessions())
    bot.run_until_disconnected()
