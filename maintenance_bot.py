import discord
from discord.ext import commands

from rings.utils.config import token

bot = discord.Client(activity=discord.Game("upgrading to v3, no commands until then"))
bot.run(token)
