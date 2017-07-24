import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

#Help Doc
helpVar=""":information_source: **NecroBot v1.0 Help Menu** :information_source: 
To access the help page pf the command simply us `n!help [command]` and replace [command] with the command you seek to display, such as `n!help edain` will display the help page of the edain command. NecroBot is still WIP so take it easy.

__User Commands__
1. **Economy** - `claim` | `balance`
2. **Wiki** - `edain` | `lotr` | `wiki`
3. **Fun** - `rr` | `tarot` | `calc` | `riddle` | `dadjoke`
4. **Utility** - `info` | `play` | `serverinfo` | `giveme`
5. **Animal** - `cat`| `dog`
6  **Modding** - `moddb`
7. **Support** - `h` | `support` | `invite`

__Moderation Commands__
1. **User Profile** - `add` | `setstats` | `perms` | `setall` | `setroles`
2. **User Moderation** - `mute`  | `unmute` | `warn` | `lock` | `nick`
3. **Feature Enable/Disable** - `automod` | `ignore`
4. **Broadcast** - `speak` | `pm`
5. **Others** - `kill` | `purge` | `blacklist` | `giveme_roles`

```Markdown
>>> The bot usually has a response system so if there is no answer to your command it is either broken, offline or you haven't written the right command
>>> Do not attempt to break the bot if possible
>>> More commands and features will come later...
```"""

#Help Dict
helpDict = {
"claim" : 
"The claim commands allows the user to claim their daily income of money, money which can then later be used to buy various things and participate in various mini games. Daily can be claimed once a day at any time. As soon as the clock hits midnight GMT all cooldowns are refreshed. Use without any arguments:\n\n__Usage__ \n`n!claim`",

"balance":
"Used to check a user's euro balance, if no user is provided it will display your own balance.\n\n__Usage__ \n`n!balance` \n`n!balance [@User]` \n\n__Example__\n`n!balance` - check your own balance \n`n!balance @NecroBot` - check the balance of NecroBot",

"edain":
"Command can be used to look up articles through the Edain Wiki. If the article is found it will return a rich embed version of the article, else it will return a series of world results similar to the search term.\n\n__Usage__\n`n!edain [article]` \n\n__Example__ \n`n!edain Sauron` - search for the article called Sauron\n`n!edain Castellans` - search for an article called Castellans",

"lotr":
"Command can be used to look up articles through the LOTR Wiki. If the article is found it will return a rich embed version of the article, else it will return a series of world results similar to the search term.\n\n__Usage__\n`n!lotr [article]` \n\n__Example__ \n`n!lotr Sauron` - search for the article called Sauron\n`n!lotr Boromir` - search for the article called Boromir",

"wiki":
"Command returns a short summary of the requested article from the requested wiki, else returns a number of different others error messages ranging for plain error messages to a series of articles related to the search result.\n\n__Usage__\n`n!wiki [wiki] [article]` \n\n__Example__\n`n!wiki disney Donald Duck` - search for the article called Donald Duck on the Disney Wiki\n`n!wiki transformers Optimus Prime` - search for the article called Optimus Prime on Transformers",

"rr":
"The rr tag allows users to play a game of russian roulette by loading a number of bullets into a gun. The number can either be picked by adding it after the rr command or will default to 1. \n\n__Usage__\n`n!rr`\n`n!rr [1-6]`\n\n__Example__\n`n!rr 5` - load 5 bullets into the gun\n`n!rr` - load the default amount (1) of bullets into the gun\n`n!rr 3` - load 3 bullets into the gun",

"tarot":
"The tarot command allows user to have their destiny read in tarot cards using our extremely *advanced* card reading system.\n\n__Usage__\n`n!tarot`",

"calc":
"The calc command will evaluate a simple mathematical equation according to its pythonic mathematical symbols and return the result.\n- `+` for additions\n- `-` for subtractions\n- `*` for multiplications \n- `/` for divisions\n- `**` for exponents\n\n__Usage__\n`n!calc [equation]`\n\n__Example__\n`n!calc 4 + 2 / 4` - calculates 2 divided by 4 plus 4\n`n!calc (4+2)*2` - calculates 4 plus 2 times 2\n`n!calc 4**2` - calculates 4 squared",

"h":
"The help tag will either display the help menu for the supplied command name  or will display the default help menu\n\n__Usage__\n`n!help`\n`n!help [command]`\n\n__Example__\n`n!help` - get the default help menu\n`n!help wiki` - get the help info for the wiki command",

"support":
"Provides an invitation to the NecroBot support channel.\n\n__Usage__\n`n!support`",

"invite":
"Provides a link to invite NecroBot to one of your servers.\n\n__Usage__\n`n!invite`",

"giveme":
"Assigns the desired role from the list of self assignable roles to the user. Can also be used to check self assignable roles and remove or add self assignable roles. (Permission level 4+ to remove/add roles (Server Admin))\n\n__Usage__\n`n!giveme info`\n`n!giveme [role]\n\n__Examples__\n`n!giveme Token Role` - assigns user role 'Token Role'\n`n!giveme info` - displays the list of self assignable roles",

"giveme_roles":
"Adds or removes roles from the list of self assignable roles.\n\n__Usage__\n`n!giveme_roles add [role]`\n`n!giveme_roles del [role]`\n\n__Examples__\n`n!giveme add Another Token Role` - adds 'Token Role' to the list of self assignable roles\n`n!giveme del A Third Token Role` - removes 'A Third Token Role' from the list of self assignable roles",

"info":
"The info command will display a user's NecroBot profile allowing users to see their warning history along with other misc data such as id, balance and permission level.\n\n__Usage__\n`n!info`\n`n!info [@User]`\n\n__Example__\n`n!info` - get your own info\n`n!info @NecroBot` - get NecroBot's info",

"serverinfo":
"Like the info commands but will display the profile of the server, with various details related to it.\n\n__Usage__\n`n!serverinfo`",

"add":
"Does the given pythonic operation on the user's current balance (works the same way as `calc`) (Permission level of 6+ (NecroBot Admins))\n\n__Usage__\n`n!add [@User] [operation]`\n\n__Example__\n`n!add @Necro +300` - add 300 to Necro's balance\n`n!add @Necro *2` - multiplies Necro's balance by 2\n`n!add @Necro -200` - substracts 200 from necro's balance.\n`n!add @Necro **3` - cubes Necro's balance",

"setstats":
"Sets the default stats for the user if not on the database already, used when a username gives the bot trouble. (Permission level of 2+ (Mod))\n\n__Usage__\n`n!setStats [@User]`\n\n__Example__\n`n!setStats @NecroBot` - sets the default stats for NecroBot",

"perms":
"Sets the permission level for the user ranging from 0-6, user can only set permission levels that is less than their own. (Permission level of 4+ (Server Admin))\n\n__Hierachy Level__\n7: The Bot Smith - Bot Owners & Collaborators\n6: NecroBot Admin - Trusted Friends\n5: Server Owner - Given to owners of a server using NecroBot\n4: Admin - Trusted members of indivudal servers\n3: Semi-Admin - 'Trainee' admins\n2: Mods - active, helpful and mature members of individual servers\n1: Helpers - helpful members of individual servers\n0: Users - members of servers\n\n__Usage__\n`n!perms [@User] [0-6]`\n\n__Example__\n`n!perms @Necro 7` - set Necro's permission level to 7",

"mute":
"Mutes a user (restrict their ability to type in channels) either permanently or temporarily.(Permission level of 2+ (Mod))\n\n__Usage__\n`n!mute @User`\n`n!mute [@User] [second]`\n\n__Example__\n`n!mute @NecroBot` - mutes NecroBot indefinitely\n`n!mute @NecroBot 15` - mutes NecroBot for 15 seconds",

"unmute":
"Unmutes a user, removing the mute role from their profiles.(Permission level of 2+ (Mod))\n\n__Usage__\n`n!unmute [@User]`\n\n__Example__\n`n!unmute @NecroBot`",

"warn":
"Adds or removes a warning from the user's NecroBot profile.(Permission level of 1+ (Helper) to add warnings and 3+ (Semi Admin) to remove a warnings)\n\n__Usage__\n`n!warn add [@User] [message]`\n`n!warn del [@User] [position]\n\n__Example__\n`n!warn add @Necro this is a test warning` - adds 'this is a test warning' to Necro's list of warnings.\n`n!warn del @Necro 1` - removes the warning in first position of Necro's warning list.",

"speak":
"Sends the message to a specific channels. (Permission level of 4+ (Server Admin))\n\n__Usage__\n`n!speak [channe id] [message]`\n\n__Example__\n`n!speak 31846564420712962 Hello, this is a message` - sends 'Hello, this is a message' to this channel (fake channel)",

"pm":
"Sends a user a message through the bot and awaits for a reply.(Permission level of 6+ (NecroBot Admin))\n\n__Usage__\n`n!pm [user ID] [message]`\n\n__Example__\n`n!pm 97846534420712962 This is another message` - sends 'This is another message' to the user",

"automod":
"Add/removes the channels/users from the necrobot automoderation, this means users/channels will no longer be affected by the spam filter, edition tracking and deletion tracking. (Permission level of 5+ (Server Owner))\n\n__Usage__\n`n!automod` `n!automod add [@Users/#channels]`\n`n!automod del [@Users/#channels]\n\n__Example__\n`n!automod add #necrobot-channel` - adds #necrobot-channel to the automod ignore list\n`n!automod add @NecroBot` - adds @NecroBot to the automod ignore list\n`n!automod del #necrobot-channel` - removes #necrobot-channel from the automod ignore list\n`n!automod del @Necrobot` - removes @NecroBot from the automod ignore list\n`n!automod` - prints the list of ignored channels and users",

"ignore":
"Add/removes the channels/users from the necrobot, this means users/channels will no longer be able to use commands. (Permission level of 5+ (Server Owner))\n\n__Usage__\n`n!ignore` `n!ignore add [@Users/#channels]`\n`n!ignore del [@Users/#channels]\n\n__Example__\n`n!ignore add #necrobot-channel` - adds #necrobot-channel to the command ignore list\n`n!ignore add @NecroBot` - adds @NecroBot to the command ignore list\n`n!ignore del #necrobot-channel` - removes #necrobot-channel from the command ignore list\n`n!ignore del @Necrobot` - removes @NecroBot from the command ignore list\n`n!ignore` - prints the list of ignored channels and users",

"kill":
"Kills the bot and saves all the data.(Permission level of 7+ (Bot Smith))\n\n__Usage__\n`n!kill`",

"purge":
"Looks over the given number of messages and removes all the one that fit the parameters.(Permission level of 5+ (Server Owner))\n\n__Usage__\n`n!purge [number]`\n\n__Example__\n`n!purge 45` - purges the past 45 message",

"blacklist":
"The ultimate moderation tool, the most powerful tool out there in terms of user moderation. This will ban the users in every server NecroBot is on and will keep them out for as long as they are on the NecroBot blacklist. This is especially good for hacking users that can unban themselves from the Discord system.(Permission level of 6+ (NecroBot Admin))\n\n__Usage__\n`n!blacklist [@User]`\n\n__Example__`n!blacklist @Invisible` - bans @Invisible from all the NecroBot servers.",

"cat":
"Post the picture of a random cat. \n\n__Usage__\n`n!cat`",

"dog":
"Post the picture of a random dog. \n\n__Usage__\n`n!dog`",

"riddle":
"Asks the user a riddle, the user must then answer the riddle by typing the solution in the channel the n!riddle command was summoned in.\n\n__Usage__\n`n!riddle`",

"dadjoke":
"Replies with a random dad joke/pun.\n\n__Usage__\n`n!dadjoke`",

"play":
"A command that allows the user to play either an audio file using a link or a youtube video. The audio file link must finish with a valid audio file extension.\n\n__Usage__\n`n!play [audio file url]`\n`n!play [youtube link]`\n\n__Example__\n`n!play https://vignette1.wikia.nocookie.net/edain-mod/images/2/20/Castellan2_select5.ogg` - play the Castellan2_select5.ogg file\n`n!play https://www.youtube.com/watch?v=o6HDfqjlCAs` - play this videos",

"setroles":
"Sets the NecroBot roles for the server and assigns them to users according to their permission level.(Permission level of 5+ (Server Owner))\n\n__Usage__\n`n!setRoles`",

"lock":
"Locks the user in the channel they currently are in.(Permission level of 3+ (Semi-Admin))\n\n__Usage__\n`n!lock`\n`n!lock [@User]`\n\n__Example__\n`n!lock [@User]`\n\n__Example__\n`n!lock @NecroBot` - locks NecroBot in the voice channel it currently is.",

"nick":
"Changes the nickname of the user (Permission level of 3+ (Moderator))\n\n__Usage__\n`n!nick [@User] [nickname]`\n\n__Example__\n`n!nick @NecroBot Lord of all Bots` - changes NecroBot's nick to 'Lord of All Bots'",

"moddb":
"Generates a rich embed from the link given it links to a mod page.\n\n__Usage__\n`n!moddb [url]`\n\n__Examples__\n`n!moddb http://www.moddb.com/mods/edain-mod` - generates a rich embed of the edain mod page\n`n!moddb http://www.moddb.com/mods/rotwk-hd-edition` - generates a rich embed of the ROTWK HD Edition page.",

"setall":
"Sets the stats for all the members on the server (Permission level of 3+ (NecroBot Admin)) \n\n__Usage__`n! setall`"
}

class Support():
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command()
    @commands.cooldown(1, 10, BucketType.server)
    async def support(self):
        await self.bot.say("**Join this server for support**: https://discord.gg/sce7jmB")

    @commands.command()
    @commands.cooldown(1, 10, BucketType.server)
    async def invite(self):
        await self.bot.say("Invite the bot to your server using this link: https://discordapp.com/oauth2/authorize?client_id=317619283377258497&scope=bot&permissions=8")

    # general help command (can be outdated)
    @commands.command()
    @commands.cooldown(3, 5, BucketType.user)
    async def help(self, *arg0 : str):
        if arg0:
            try:
                helpRequest = arg0[0]
                await self.bot.say(":information_source: **The `" + helpRequest + "` command** :information_source:\n\n" + helpDict[helpRequest] + "\n```Markdown \n>>> The bot usually has a response system so if there is no answer to your command it is either broken, offline or you haven't written the right command \n>>> Do not attempt to break the bot if possible \n>>> More commands and features will come later... \n```")
            except KeyError:
                await self.bot.say("This command doesn't exist or Necro forgot to add it.")
        else:
            await self.bot.say(helpVar)

def setup(bot):
    bot.add_cog(Support(bot))