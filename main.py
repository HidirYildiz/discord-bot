import os
import time
from datetime import datetime

import discord
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
VOICE_CHANNEL_ID = int(os.getenv("VOICE_CHANNEL_ID"))
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID"))
ROLE_ID = int(os.getenv("ROLE_ID"))

intents = discord.Intents.default()
intents.voice_states = True
intents.members = True

client = discord.Client(intents=intents)

COOLDOWN_SECONDS = 2 * 60 * 60  # 2h

# 🧠 État global propre
last_alert_time = 0
alert_sent = False

log_channel = None
voice_channel = None


@client.event
async def on_ready():
    global log_channel, voice_channel

    print(f"Connecté en tant que {client.user}")

    log_channel = client.get_channel(LOG_CHANNEL_ID)
    voice_channel = client.get_channel(VOICE_CHANNEL_ID)

    if log_channel is None:
        print("❌ Salon log introuvable")
    if voice_channel is None:
        print("❌ Salon vocal introuvable")


@client.event
async def on_voice_state_update(member, before, after):
    global last_alert_time, alert_sent

    if member.bot:
        return

    if log_channel is None or voice_channel is None:
        return

    now_str = datetime.now().strftime("%d/%m %H:%M")

    # 🟢 JOIN
    if (
        before.channel is None or before.channel.id != VOICE_CHANNEL_ID
    ) and (
        after.channel is not None and after.channel.id == VOICE_CHANNEL_ID
    ):
        await log_channel.send(
            f"🟢 **{member.display_name}** a rejoint le vocal à **{now_str}**"
        )

    # 🔴 LEAVE
    if (
        before.channel is not None and before.channel.id == VOICE_CHANNEL_ID
    ) and (
        after.channel is None or after.channel.id != VOICE_CHANNEL_ID
    ):
        await log_channel.send(
            f"🔴 **{member.display_name}** a quitté le vocal à **{now_str}**"
        )

    # 👥 mise à jour membres
    members = [m for m in voice_channel.members if not m.bot]

    # ⚠️ seulement 1 personne
    if len(members) == 1:
        now = time.time()

        if not alert_sent and (now - last_alert_time >= COOLDOWN_SECONDS):
            last_alert_time = now
            alert_sent = True

            last_user = members[0]

            await log_channel.send(
                f"<@&{ROLE_ID}> ⚠️ Il ne reste plus qu'une seule personne dans le vocal : **{last_user.display_name}**"
            )

    # 🔄 reset si le vocal n'est plus dans cet état critique
    elif len(members) > 1:
        alert_sent = False


client.run(TOKEN)