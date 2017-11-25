from discord.ext.commands.cooldowns import BucketType

def _medium_cooldown():
    return 3, 3, BucketType.user