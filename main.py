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

# Intents nécessaires
intents = discord.Intents.default()
intents.voice_states = True
intents.members = True

# Bot simple (pas de commandes => Client suffit)
client = discord.Client(intents=intents)

# ⏱️ cooldown 2h
COOLDOWN_SECONDS = 2 * 60 * 60
derniere_alerte_unique = 0


@client.event
async def on_ready():
    print(f"Connecté en tant que {client.user}")


@client.event
async def on_voice_state_update(member, before, after):
    global derniere_alerte_unique

    # ❌ ignore bots
    if member.bot:
        return

    log_channel = client.get_channel(LOG_CHANNEL_ID)
    if log_channel is None:
        return

    heure = datetime.now().strftime("%d/%m %H:%M")

    # 🟢 JOIN VOCAL
    if (
        (before.channel is None or before.channel.id != VOICE_CHANNEL_ID)
        and (after.channel is not None and after.channel.id == VOICE_CHANNEL_ID)
    ):
        await log_channel.send(
            f"🟢 **{member.display_name}** a rejoint le vocal à **{heure}**"
        )

    # 🔴 LEAVE VOCAL
    if (
        (before.channel is not None and before.channel.id == VOICE_CHANNEL_ID)
        and (after.channel is None or after.channel.id != VOICE_CHANNEL_ID)
    ):
        await log_channel.send(
            f"🔴 **{member.display_name}** a quitté le vocal à **{heure}**"
        )

    voice_channel = client.get_channel(VOICE_CHANNEL_ID)
    if voice_channel is None:
        return

    # 👥 membres humains uniquement
    membres_humains = [m for m in voice_channel.members if not m.bot]

    # ⚠️ UNE SEULE PERSONNE RESTE
    if len(membres_humains) == 1:
        now = time.time()

        if now - derniere_alerte_unique >= COOLDOWN_SECONDS:
            derniere_alerte_unique = now

            dernier = membres_humains[0]

            await log_channel.send(
                f"<@&{ROLE_ID}> ⚠️ Il ne reste plus qu'une seule personne dans le vocal : **{dernier.display_name}**"
            )


client.run(TOKEN)