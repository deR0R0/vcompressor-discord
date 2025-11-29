import discord
from discord.ext import commands



DISCORD_INTENTS = discord.Intents.all()
client = commands.Bot(command_prefix="/", intents=DISCORD_INTENTS)