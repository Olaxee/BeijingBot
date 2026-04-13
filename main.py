import discord
import os
import re
import asyncio

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

client = discord.Client(intents=intents)


# =========================
# 🧼 CLEAN NOM SALON
# =========================
def clean_name(name: str):
    name = name.lower()
    name = re.sub(r"[^a-z0-9]", "", name)
    return name[:20]


# =========================
# 🎨 CONVERT COULEUR
# =========================
def parse_color(value: str):
    if value == "<->":
        return discord.Color.blue()

    value = value.lower()

    colors = {
        "red": discord.Color.red(),
        "blue": discord.Color.blue(),
        "green": discord.Color.green(),
        "orange": discord.Color.orange(),
        "purple": discord.Color.purple(),
        "yellow": discord.Color.gold(),
        "grey": discord.Color.dark_grey(),
    }

    if value in colors:
        return colors[value]

    # hex support (#ff0000)
    if value.startswith("#"):
        try:
            return discord.Color(int(value.replace("#", ""), 16))
        except:
            return discord.Color.blue()

    return discord.Color.blue()


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
            return await interaction.response.send_message(
                "❌ Catégorie introuvable",
                ephemeral=True
            )

        channel = await guild.create_text_channel(
            name=f"ticket-{clean_name(user.name)}",
            category=category,
            overwrites={
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
                role: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
                guild.me: discord.PermissionOverwrite(view_channel=True)
            }
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


# =========================
# 🔒 FERMER TICKET
# =========================
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
            title="❌ Annulé",
            description="La fermeture du ticket a été annulée.",
            color=discord.Color.red()
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)


# =========================
# 💬 +EMBED COMMAND (ULTRA PRO)
# =========================
@client.event
async def on_message(message):

    if message.author.bot:
        return

    guild = message.guild
    role = discord.utils.get(guild.roles, name="🔆Modérateur")

    # =========================
    # +EMBED
    # =========================
    if message.content.startswith("+embed"):

        if role not in message.author.roles:
            return await message.channel.send(
                embed=discord.Embed(
                    title="❌ Permission refusée",
                    description="Tu n’as pas la permission d’utiliser cette commande.",
                    color=discord.Color.red()
                )
            )

        parts = message.content.split(" ")

        # usage:
        # +embed <texte> <couleur> <titre> <footer> <image>

        if len(parts) < 2:
            return await message.channel.send(
                embed=discord.Embed(
                    title="ℹ Utilisation",
                    description="Utilisation : +embed <texte> <couleur> <en-tête> <footer> <image>\n"
                                "*si vous ne voulez pas mettre un champ → '<->'*",
                    color=discord.Color.orange()
                )
            )

        text = parts[1] if len(parts) > 1 else "<->"
        color = parts[2] if len(parts) > 2 else "<->"
        header = parts[3] if len(parts) > 3 else "<->"
        footer = parts[4] if len(parts) > 4 else "<->"
        image = parts[5] if len(parts) > 5 else "<->"

        embed = discord.Embed(
            description=None if text == "<->" else text,
            color=parse_color(color)
        )

        # HEADER (vrai titre)
        if header != "<->":
            embed.title = header

        # FOOTER
        if footer != "<->":
            embed.set_footer(text=footer)

        # IMAGE
        if image != "<->":
            embed.set_image(url=image)

        await message.channel.send(embed=embed)


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
