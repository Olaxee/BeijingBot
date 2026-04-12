import discord
import os

intents = discord.Intents.default()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"Connecté en tant que {client.user}")

@client.event
async def on_message(message):
    if message.author.bot:
        return

    if message.content.lower() == "+ping":
        embed = discord.Embed(
            title="🏓 Pong !",
            description="**Ping reçu avec succès !**",
            color=discord.Color.blue()
        )
        embed.add_field(name="📡 Statut", value="Bot opérationnel", inline=False)
        embed.set_footer(text="Commande +ping")

        await message.channel.send(embed=embed)

client.run(os.getenv("TOKEN"))
