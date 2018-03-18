from discord.ext import commands
import discord

def has_perms(perms_level):
    def predicate(ctx): 
        if isinstance(ctx.message.channel, discord.DMChannel):
            return False

        return ctx.bot.user_data[ctx.message.author.id]["perms"][ctx.message.guild.id] >= perms_level

    return commands.check(predicate)

def is_waifu_admin():
    def predicate(ctx):
        return ctx.author.id in [241942232867799040, 203015871378096128]

    return commands.check(predicate)
    