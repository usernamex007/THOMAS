from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.account import ReportPeerRequest
from telethon.tl.types import InputReportReasonSpam
import logging
import config

logging.basicConfig(level=logging.INFO)

bot = TelegramClient("report_bot", config.API_ID, config.API_HASH).start(bot_token=config.BOT_TOKEN)

session_clients = []
for session in config.SESSION_STRINGS:
    client = TelegramClient(StringSession(session), config.API_ID, config.API_HASH)
    session_clients.append(client)

active_reports = {}

async def start_sessions():
    for client in session_clients:
        try:
            await client.start()
            logging.info("✅ Started a new session successfully!")
        except Exception as e:
            logging.error(f"❌ Error starting session: {e}")

@bot.on(events.NewMessage(pattern="/csession"))
async def check_sessions(event):
    active_sessions = sum(1 for client in session_clients if await client.is_user_authorized())
    total_sessions = len(session_clients)
    await event.reply(f"📌 **Total Sessions:** {total_sessions}\n✅ **Active Sessions:** {active_sessions}")

@bot.on(events.NewMessage(pattern="/start"))
async def start(event):
    await event.reply("👋 **Welcome to Mass Report Bot!**\nUse /reportuser @username spam or /reportchannel @channel spam to report.")

@bot.on(events.NewMessage(pattern="/help"))
async def help(event):
    help_text = "**Mass Report Bot Commands:**\n"
    help_text += "/reportuser @username spam – Report a user\n"
    help_text += "/reportchannel @channel spam – Report a channel\n"
    help_text += "/addsession – Add a new session\n"
    help_text += "/csession – Check active sessions"
    await event.reply(help_text)

@bot.on(events.NewMessage(pattern=r"/report(user|channel)\s+(@\w+|\d+)"))
async def report(event):
    args = event.text.split()
    if len(args) < 2:
        return await event.reply("⚠️ Usage: `/reportuser @username spam` or `/reportchannel @channel spam`")

    report_type = args[0]  
    target = args[1]  

    await event.reply("📌 How many reports do you want to send? (1-100) Please enter a number.")
    active_reports[event.sender_id] = (report_type, target)

@bot.on(events.NewMessage())
async def handle_report_count(event):
    if event.sender_id in active_reports:
        try:
            report_type, target = active_reports[event.sender_id]
            report_count = int(event.raw_text.strip())

            if report_count < 1 or report_count > 100:
                return await event.reply("⚠️ Please enter a number between 1 and 100.")

            reasons = {"spam": InputReportReasonSpam()}
            reason = reasons["spam"]

            success_count, failed_count = 0, 0

            for client in session_clients:
                try:
                    entity = await client.get_entity(target)

                    if report_type == "/reportchannel":
                        try:
                            await client(JoinChannelRequest(entity))
                            logging.info(f"✅ Joined {target} before reporting")
                        except Exception:
                            pass

                    for _ in range(report_count):
                        await client(ReportPeerRequest(peer=entity, reason=reason, message="Reported for spam"))
                        success_count += 1
                        logging.info(f"✅ Reported {target}")

                except Exception as e:
                    failed_count += 1
                    logging.error(f"❌ Error reporting {target}: {e}")

            await event.reply(f"✅ {success_count} reports sent, ❌ {failed_count} failed.")
            del active_reports[event.sender_id]

        except ValueError:
            await event.reply("⚠️ Please enter a valid number.")

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

with bot:
    bot.loop.run_until_complete(start_sessions())
    bot.run_until_disconnected()
