# NecroBot
NecroBot has two very specific reason to be, it is meant to increase the Discord Moderation abilities tenfold but more importantly it is meant to be the first bot to support mod creators throughout the world. The bot will work hand in hand with modders all across Discord to help them showcase their content on their servers through rich embeds. NecroBot also contains it's own hierarchy system which means that server owners no longer need to give users specific permissions on their servers for them to use the bot, simply set their NecroBot permission level to be as you wish using `n!perms`. Not sure what permission level to use? Just have a look at `n!h` for help. Bot prefix is 'n![command]'.

__Hierachy Ladder:__
* 7: The Bot Smith - Bot Owner & Close Collaborators
* 6: NecroBot Admin - Trusted Members of the NecroBot server
* 5: Server Owner - Given to owners of a server using NecroBot
* 4: Admin - Trusted members of individual servers
* 3: Semi-Admin - "Trainee" admins
* 2: Mods - active, helpful and mature members of individual servers
* 1: Helpers - helpful members of individual servers
* 0: Users - members of servers

__User Pofile__ <br>
**EXP** - Every non-command message generates exp for the user <br>
**Money** - users can claim dailies and check their money

__Planned Features__
* [ ] **Modularity Overhaul** - allow server owners to set their own auto moderation channels, welcome message and others server-specific settings.
* [x] **Overhaul to expand user profile** - server-specific permission, more compact, improved code
* [ ] **Server Roles for Bot Roles** - Give server owners the ability to assign server roles to the bot roles and thereby the ability to grant a bot role by simply granting the equivalent server roles
* [ ] **EXP System** - longer exp cooldown, level up system, random amount of exp
* [ ] **Money System** - actual use of money, transfers between users
* [x] **Help system** - rewamp into something more compact, allows user to add an argument to look up a detailed description of a command.
* [x] **Wikia System** - make a more efficient use of the Wikia API system to allow users to find more out on their favorite wiki

__Commands__
User Commands (Permission level of 0+ (Users))
* `claim` - claim your daily bonus. Once per GMT day.
* `balance [@User]` - check the balance of the given user, if no user is provided it will display your own balance.
* `edain [article]` - search for an article on the Edain Mod Wiki. Content will be displayed if found, else a list of relevant articles will be provided.
* `lotr [article]` - search for an article on the LOTR Wiki. Content will be displayed if found, else a list of relevant articles will be provided.
* `wiki [wiki] [article]` - search for an article on the given wiki. Content will be displayed if found, else a list of relevant articles will be provided.
* `rr [1-6]` - play a game of Russian bullets using the given number of bullets, if no integer is provided it will default to one.
* `tarot` - NecroBot will read your fate in the cards, using the ancient and mystical art of tarology.
* `calc [equation]` - evaluates the given equation. Use `+` to add, `-` to minus, `*` to multiply, `/` to divide, `**` for exponents, `%` for modulo.
* `riddle` - asks the user one of Gollum's riddle, the user then has 30 seconds to type the correct answer or Gollum feeds them to the 'fishies'.
* `dadjoke` - prints a random dad joke from a long list of hilarious and relevant dad jokes (aren't they all hilarious anyways?).
* `info [@User]` - displays the given user's info in a rich embed. If no user is provided it will display your own info.
* `play [url]` - plays either an audio file if given a url finishing with a valid audio file extension or a youtube video if given a youtube url (Award: **NecroBot's buggiest command**)
* `cat` - posts a random cat picture.
* `dog` - posts a random dog pictures.
* `moddb [url]` - will create a rich embed of the mod page given, it must come from the ModDB site and it must be the main page of the mod. (Award: **NecroBot's Crown Jewels**)
* `h [command]` - prints help for the given command, if no command is given then prints the default help.
* `support` - prints an invite to the NecroBot Support server.
* `invite` - prints a link to invite NecroBot to your server

Helper Commands (Permission level of 1+ (Helper))
* `warn add [@User] [message]` - add a warning to the user's warning list to add simply use add and then specify a user and message.

Moderator Commands (Permission level of 2+ (Moderator))
* `setStats [@User]` - sets default NecroBot stats for a user.
* `mute [seconds] [@User(s)]` - mutes all the users mentioned for the amount of seconds provided, if no seconds argument is provided then mutes user(s) indefinitely.
* `unmute [@User(s)]` - unmutes all muted users mentioned.

Semi-Admin Commands (Permission level of 3+ (Semi-Admin))
* `warn del [@User] [position]` - removes a warning from the user's warning list to remove simply use del and then specify a user and the position of the warning to be removed (positions start at 0)

Admin Commands (Permission level of 4+ (Server Admin))
* `perms [@User] [0-6]` - sets permission level which dictates what commands can be used, users can only set a permission level lower than their own.
* `speak [channelID] [message]` - broadcasts a message to the channel provided by proxy of the bot.
* `purge [number]` - purge [number] of messages from the channel it's summoned in.
* `ignore ( add | del ) [ @Users | #channels ]` - add/removes the channels/users from the necrobot ignore list which affects whether or not users can use commands and in which channels they can be used. If no argument or sub-command is provided it will print the list of ignored channels/users.

Server Owner Commands (Permission level of 5+ (Server Owner))
* `automod ( add | del ) [ @Users | #channels ]` - add/removes the channels/users from the necrobot automoderation, this means users/channels will no longer be affected by the spam filter, edition tracking and deletion tracking. If no argument or sub-command is given it will print the list of channels/users ignored by auto moderation. 

NecroBot Admin Commands (Permission level of 6+ (NecroBot Admin))
* `add [@User] [operation]` - does the given equation on the mentioned user's balance. Works similar to calc.
* `setAll` - sets the default stats for all user not already registered on the server.
* `blacklist [@User]` - the latest advancement in banning tech, will ban a user and add them to the list which will ban the user if they try to join any of the servers with NecroBot, high permission level due to power.

NecroBot Owner (Permission level of 7+ (Bot Owner))
* `kill` - saves all the files and sys.exit() the bot (Bot Owner Only)


__Moderation Features__
* **Message Deletion Tracking** - tracks deleted messages and prints deleted messages in a separate channel
* **Message Edition Tracking** - tracks edits made to messages and prints the before and after in a separate channel
* **User Welcome** - welcome new users with a message and assigns them their own username as their server nickname
* **Spam Prevention** - different messages spammed within a 1 second interval or identical message spammed within a 2 second interval will be deleted

Join to see in action: https://discord.gg/sce7jmB <br>
Tell them GitHub sent you!
