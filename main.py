import discord
import os
import re
import asyncio
import shlex
import secrets
import string
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

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
# 🕒 DATE INTELLIGENTE
# =========================
def get_date_string():
    now = datetime.now(ZoneInfo("Europe/Paris"))
    today = now.date()
    yesterday = today - timedelta(days=1)

    if now.date() == today:
        date_str = "Aujourd’hui"
    elif now.date() == yesterday:
        date_str = "Hier"
    else:
        date_str = now.strftime("%d/%m/%Y")

    time_str = now.strftime("%H:%M")

    return f"{date_str} à {time_str}"


# =========================
# 🎫 TICKETS
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
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            role: discord.PermissionOverwrite(view_channel=True) if role else None,
            guild.me: discord.PermissionOverwrite(view_channel=True)
        }

        channel = await guild.create_text_channel(
            name=channel_name,
            category=category,
            overwrites=overwrites
        )

        embed = discord.Embed(
            description=f"""**Ticket ouvert par** {user.mention}

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
            view=ConfirmCloseView()
        )


class ConfirmCloseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=30)

    @discord.ui.button(label="✔ Oui", style=discord.ButtonStyle.green)
    async def yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🔒 Fermeture du ticket... (5s)")
        await asyncio.sleep(5)
        await interaction.channel.delete()

    @discord.ui.button(label="❌ Non", style=discord.ButtonStyle.red)
    async def no(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.message.delete()


# =========================
# 💬 COMMANDES
# =========================
@client.event
async def on_message(message):

    if message.author.bot:
        return

    guild = message.guild
    role = discord.utils.get(guild.roles, name="🔆Modérateur")

    bot_user = guild.me if guild else client.user

    # =========================
    # 🎫 +setticket
    # =========================
    if message.content.lower() == "+setticket":

        if role not in message.author.roles:
            return await message.channel.send(
                embed=discord.Embed(
                    description="❌ Tu n’as pas la permission.",
                    color=discord.Color.red()
                )
            )

        # Vérif si déjà un panel existe
        for channel in guild.text_channels:
            async for msg in channel.history(limit=50):
                if msg.author == client.user and msg.components:
                    return await message.channel.send(
                        embed=discord.Embed(
                            description="❌ Un panel ticket existe déjà.",
                            color=discord.Color.red()
                        )
                    )

        perms = message.channel.permissions_for(guild.me)

        if not perms.send_messages:
            return await message.channel.send(
                embed=discord.Embed(
                    description="❌ Impossible d'envoyer le panel (permissions).",
                    color=discord.Color.red()
                )
            )

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

        await message.channel.send(embed=embed, view=TicketOpenView())

    # =========================
    # 🔐 +gencode
    # =========================
    if message.content.lower() == "+gencode":

        alphabet = string.ascii_letters + string.digits
        length = secrets.randbelow(9) + 16

        code = ''.join(secrets.choice(alphabet) for _ in range(length))

        embed = discord.Embed(
            title="🔐 Code généré",
            description=f"`{code}`",
            color=discord.Color.green()
        )

        embed.set_footer(text="Longueur aléatoire • Génération sécurisée")

        return await message.channel.send(embed=embed)

    # =========================
    # ℹ HELP EMBED
    # =========================
    def help_embed():
        return discord.Embed(
            title="ℹ +embed",
            description="**+embed \"texte\" \"couleur\" \"titre\" \"footer\" \"image\"**\n👉 Utilise `<->` pour ignorer une option",
            color=discord.Color.orange()
        )

    if message.content.startswith("+embed") and role not in message.author.roles:
        return await message.channel.send(embed=discord.Embed(description="❌ Tu n’as pas la permission.", color=discord.Color.red()))

    if message.content.startswith("+embed"):

        content = message.content.replace("+embed", "").strip()

        if content == "":
            return await message.channel.send(embed=help_embed())

        try:
            args = shlex.split(content)
        except:
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

        if header != "<->":
            embed.set_author(name=header, icon_url=bot_user.display_avatar.url)

        await message.channel.send(embed=embed)


# =========================
# 👋 JOIN SYSTEM
# =========================
@client.event
async def on_member_join(member):

    channel = discord.utils.get(member.guild.text_channels, name="🖼️・join")
    if not channel:
        return

    guild = member.guild
    count = guild.member_count

    now = datetime.now(ZoneInfo("Europe/Paris"))
    today = now.date()
    yesterday = today - timedelta(days=1)

    if now.date() == today:
        date_str = "Aujourd’hui"
    elif now.date() == yesterday:
        date_str = "Hier"
    else:
        date_str = now.strftime("%d/%m/%Y")

    time_str = now.strftime("%H:%M")

    embed = discord.Embed(
        description=f"Bienvenue {member.mention} sur **Beijing 🏯🏮**. Nous sommes {count} membres.",
        color=0xFF1D8D
    )

    embed.set_author(name="Bienvenue.", icon_url=member.display_avatar.url)
    embed.set_footer(text=f"Nouveau membre #{count} • {date_str} à {time_str}")
    embed.set_thumbnail(url=member.display_avatar.url)

    await channel.send(embed=embed)


# =========================
# 🤖 READY
# =========================
@client.event
async def on_ready():
    print(f"Connecté en tant que {client.user}")


# =========================
# 🔐 TOKEN
# =========================
client.run(os.getenv("TOKEN"))
