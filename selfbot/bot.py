import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='n!')

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.event
async def on_message(message):
    if message.author.id == "241942232867799040":
        if message.content.startswith("§"):
            image = open("images/"+message.content[1:])
            await bot.edit_message(message, image)


token = open("data/token.txt", "r").read()
bot.run(token, bot=False)