import discord
import os
import re
import asyncio

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

client = discord.Client(intents=intents)

# =========================
# 🔧 UTILITAIRE CLEAN NOM
# =========================
def clean_name(name: str):
    name = name.lower()
    name = re.sub(r"[^a-z0-9\-]", "", name)
    return name[:20]  # limite de sécurité


# =========================
# 🎫 VIEW - OUVRIR TICKET
# =========================
class TicketOpenView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="📥 Ouvrir", style=discord.ButtonStyle.green)
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):

        guild = interaction.guild
        user = interaction.user

        mod_role = discord.utils.get(guild.roles, name="🔆Modérateur")

        category_name = "tickets"
        category = discord.utils.get(guild.categories, name=category_name)
        if category is None:
            category = await guild.create_category(category_name)

        channel_name = f"ticket-{clean_name(user.name)}"

        # créer salon ticket
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            mod_role: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            guild.me: discord.PermissionOverwrite(view_channel=True)
        }

        channel = await guild.create_text_channel(
            name=channel_name,
            category=category,
            overwrites=overwrites
        )

        # message dans salon ticket
        await channel.send(
            f"{user.mention} {mod_role.mention if mod_role else ''}\n\n"
            f"**Ticket ouvert par** {user.mention}\n\n"
            f"Raison : **Contacter le staff**\n\n"
            f"Merci d'avoir contacté le support.\n"
            f"Décrivez votre problème puis attendez de recevoir une réponse."
            ,
            view=TicketCloseView()
        )

        # message dans salon panel
        panel = discord.utils.get(guild.text_channels, name="📩・ticket")
        if panel:
            await panel.send(f"🎫 Ticket créé → {channel.mention}")

        await interaction.response.send_message(
            f"🎫 Ticket créé : {channel.mention}",
            ephemeral=True
        )


# =========================
# 🔒 VIEW - FERMER TICKET
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
    async def confirm_yes(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.send_message("🔒 Fermeture du ticket... (5s)", ephemeral=False)
        await asyncio.sleep(5)
        await interaction.channel.delete()

    @discord.ui.button(label="❌ Non", style=discord.ButtonStyle.red)
    async def confirm_no(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.message.delete()
        await interaction.response.send_message("❌ Annulé", ephemeral=True)


# =========================
# 📩 PANEL TICKETS
# =========================
async def send_ticket_panel():
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
# 🤖 BOT READY
# =========================
@client.event
async def on_ready():
    print(f"Connecté en tant que {client.user}")
    client.loop.create_task(send_ticket_panel())


# =========================
# 🔧 TOKEN
# =========================
client.run(os.getenv("TOKEN"))
