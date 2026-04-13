import discord
import os
import re
import asyncio
import shlex
from datetime import datetime
import pytz

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

client = discord.Client(intents=intents)


# =========================
# 🧼 CLEAN NOM SALON
# =========================
def clean_name(name: str):
    name = name.lower()
    name = re.sub(r"[^a-z0-9]", "", name)
    return name[:20]


# =========================
# 🎫 TICKETS (inchangé)
# =========================
class TicketOpenView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="📥 Ouvrir", style=discord.ButtonStyle.green)
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):

        guild = interaction.guild
        user = interaction.user

        role = discord.utils.get(guild.roles, name="🔆Modérateur")

        category = discord.utils.get(guild.categories, name="📩  //  Ticket")
        if category is None:
            return await interaction.response.send_message("❌ Catégorie introuvable", ephemeral=True)

        channel_name = f"ticket-{clean_name(user.name)}"

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            role: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            guild.me: discord.PermissionOverwrite(view_channel=True)
        }

        channel = await guild.create_text_channel(
            name=channel_name,
            category=category,
            overwrites=overwrites
        )

        embed = discord.Embed(
            description=
f"""**Ticket ouvert par** {user.mention}

Raison : **Contacter le staff**

Merci d'avoir contacté le support.
Décrivez votre problème puis attendez de recevoir une réponse.
""",
            color=discord.Color.green()
        )

        await channel.send(
            content=f"{user.mention} {(role.mention if role else '')}",
            embed=embed,
            view=TicketCloseView()
        )

        await interaction.response.send_message(
            f"🎫 Ticket créé : {channel.mention}",
            ephemeral=True
        )


class TicketCloseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 Fermer", style=discord.ButtonStyle.red)
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.send_message(
            "❓ Êtes-vous sûr de vouloir fermer ce ticket ?",
            view=ConfirmCloseView(),
            ephemeral=False
        )


class ConfirmCloseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=30)

    @discord.ui.button(label="✔ Oui", style=discord.ButtonStyle.green)
    async def yes(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.send_message("🔒 Fermeture du ticket... (5s)", ephemeral=False)
        await asyncio.sleep(5)
        await interaction.channel.delete()

    @discord.ui.button(label="❌ Non", style=discord.ButtonStyle.red)
    async def no(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.message.delete()

        embed = discord.Embed(
            description="❌ Annulé : fermeture du ticket annulée.",
            color=discord.Color.red()
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)


# =========================
# 💬 +EMBED
# =========================
@client.event
async def on_message(message):

    if message.author.bot:
        return

    guild = message.guild
    role = discord.utils.get(guild.roles, name="🔆Modérateur")

    bot_user = guild.me if guild else client.user

    def help_embed():
        return discord.Embed(
            title="ℹ Utilisation +embed",
            description='Syntaxe :\n**+embed "texte" "couleur" "en-tête" "footer" "image"**',
            color=discord.Color.orange()
        )

    # ❌ no role
    if message.content.startswith("+embed") and role not in message.author.roles:
        return await message.channel.send(
            embed=discord.Embed(
                description="❌ Tu n’as pas la permission d’utiliser cette commande.",
                color=discord.Color.red()
            )
        )

    if message.content.startswith("+embed"):

        content = message.content.replace("+embed", "").strip()

        if content == "":
            return await message.channel.send(embed=help_embed())

        try:
            args = shlex.split(content)
        except:
            return await message.channel.send(embed=help_embed())

        if len(args) < 1:
            return await message.channel.send(embed=help_embed())

        text = args[0] if len(args) > 0 else "<->"
        color = args[1] if len(args) > 1 else "<->"
        header = args[2] if len(args) > 2 else "<->"
        footer = args[3] if len(args) > 3 else "<->"
        image = args[4] if len(args) > 4 else "<->"

        embed = discord.Embed()

        if text != "<->":
            embed.description = text.replace("\\n", "\n")

        try:
            embed.color = int(color.replace("#", ""), 16) if color != "<->" else discord.Color.blue()
        except:
            embed.color = discord.Color.blue()

        if footer != "<->":
            embed.set_footer(text=footer)

        if image != "<->":
            embed.set_thumbnail(url=image)

        embed.set_author(
            name=header if header != "<->" else "Embed",
            icon_url=bot_user.display_avatar.url
        )

        await message.channel.send(embed=embed)


# =========================
# 👋 WELCOME SYSTEM (JOIN)
# =========================
@client.event
async def on_member_join(member):

    guild = member.guild

    channel = discord.utils.get(guild.text_channels, name="🖼️・join")
    if channel is None:
        return

    # 👥 compteur membres
    member_count = guild.member_count

    # ⏰ heure Paris
    tz = pytz.timezone("Europe/Paris")
    now = datetime.now(tz)
    time_now = now.strftime("%H:%M")

    embed = discord.Embed(
        description=(
            f"Bienvenue {member.mention} sur **Beijing 🏯🏮**. "
            f"Nous sommes {member_count} membres."
        ),
        color=0xFF1D8D
    )

    embed.set_author(
        name="Bienvenue.",
        icon_url=member.display_avatar.url
    )

    embed.set_footer(
        text=f"Nouveau membre #{member_count} • Aujourd’hui à {time_now}"
    )

    embed.set_thumbnail(url=member.display_avatar.url)

    await channel.send(embed=embed)


# =========================
# 📩 PANEL TICKETS
# =========================
async def send_panel():
    await client.wait_until_ready()

    for guild in client.guilds:
        channel = discord.utils.get(guild.text_channels, name="📩・ticket")

        if channel:
            embed = discord.Embed(
                title="🎫 Support & Tickets",
                description=(
                    "Avez vous besoin d'aide ?\n"
                    "Avez vous besoin de contacter le staff ?\n"
                    "Avez vous besoin d'info ?\n\n"
                    "Ouvrez un ticket ci-dessous"
                ),
                color=discord.Color.green()
            )

            await channel.send(embed=embed, view=TicketOpenView())


# =========================
# 🤖 READY
# =========================
@client.event
async def on_ready():
    print(f"Connecté en tant que {client.user}")
    client.loop.create_task(send_panel())


# =========================
# 🔐 TOKEN
# =========================
client.run(os.getenv("TOKEN"))
