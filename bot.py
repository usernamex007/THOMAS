from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.account import ReportPeerRequest
from telethon.tl.types import InputReportReasonSpam
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

@bot.on(events.NewMessage(pattern="/csession"))
async def check_sessions(event):
    active_sessions = 0
    for client in session_clients:
        if await client.is_user_authorized():
            active_sessions += 1

    total_sessions = len(session_clients)
    await event.reply(f"📌 **Total Sessions:** {total_sessions}\n✅ **Active Sessions:** {active_sessions}")

@bot.on(events.NewMessage(pattern="/start"))
async def start(event):
    await event.reply("👋 **Welcome to Mass Report Bot!**\nUse `/reportuser @username spam` or `/reportchannel @channel spam` to report.")

@bot.on(events.NewMessage(pattern="/help"))
async def help(event):
    help_text = "**Mass Report Bot Commands:**\n"
    help_text += "/reportuser @username spam – Report a user\n"
    help_text += "/reportchannel @channel spam – Report a channel\n"
    help_text += "/addsession – Add a new session\n"
    help_text += "/csession – Check active sessions"
    await event.reply(help_text)

@bot.on(events.NewMessage(pattern=r"/report(user|channel)\s+(@\w+|\d+)\s+(\w+)"))
async def report(event):
    args = event.text.split()
    if len(args) < 3:
        return await event.reply("⚠️ Usage: `/reportuser @username spam` or `/reportchannel @channel spam`")
    
    report_type = args[0]  # /reportuser या /reportchannel
    target = args[1]  # Username, Channel, या ID
    reason_text = args[2].lower()

    reasons = {
        "spam": InputReportReasonSpam(),
        "scam": InputReportReasonSpam(),
        "violence": InputReportReasonSpam(),
        "child": InputReportReasonSpam(),
        "illegal": InputReportReasonSpam(),
        "terrorism": InputReportReasonSpam(),
        "copyright": InputReportReasonSpam()
    }

    if reason_text not in reasons:
        return await event.reply("⚠️ Invalid reason! Use: spam, violence, scam, child, illegal, terrorism, copyright")

    reason = reasons[reason_text]

    await event.reply("📌 कितनी रिपोर्ट मारनी हैं? (1-100) कृपया संख्या भेजें।")

    count_msg = await bot.wait_for(events.NewMessage(from_users=event.sender_id), timeout=30)
    try:
        report_count = int(count_msg.text)
        if report_count < 1 or report_count > 100:
            return await event.reply("⚠️ कृपया 1 से 100 के बीच कोई संख्या दर्ज करें।")
    except ValueError:
        return await event.reply("⚠️ कृपया सही संख्या भेजें।")

    success_count, failed_count = 0, 0

    for client in session_clients:
        try:
            entity = await client.get_entity(target)

            if report_type == "/reportchannel":
                try:
                    await client(JoinChannelRequest(entity))
                    logging.info(f"✅ Joined {target} before reporting")
                except Exception as e:
                    logging.warning(f"⚠️ Unable to join {target}: {e}")

            for _ in range(report_count):
                await client(ReportPeerRequest(peer=entity, reason=reason, message=f"Reported for {reason_text}"))
                success_count += 1
                logging.info(f"✅ Reported {target} for {reason_text}")

        except Exception as e:
            failed_count += 1
            logging.error(f"❌ Error reporting {target}: {e}")

    await event.reply(f"✅ {success_count} reports sent, ❌ {failed_count} failed.")

@bot.on(events.NewMessage(pattern="/addsession"))
async def add_session(event):
    await event.reply("📥 Send your **Telethon Session String** to add a new session.")

@bot.on(events.NewMessage())
async def new_session(event):
    if len(event.raw_text) > 20:
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
