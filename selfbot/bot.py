import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='$', self_bot=True)

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.command(pass_context = True)
@checks.is_owner()
async def e(cont, arg0 : str):
    image = open("images/"+arg0+".png")
    await bot.send_file(cont.message.channel, image)
    await bot.delete_message(cont.message)


token = open("data/token.txt", "r").read()
bot.run(token, bot=False)