import json

@commands.command
async def get_roles(self, ctx):
    self_roles = []
    query = """INSERT INTO necrobot.SelfRoles VALUES ({},{});"""
    for guild in self.server_data:
        guild_obj = self.bot.get_guild(guild)
        for role in self.server_data[guild]["selfRoles"]:
            self_roles.append(query.format(guild, discord.utils.get(guild_obj.roles, name=role)))

    with open("self_roles.json", "w") as out:
        json.dump(self_roles, out)

