# NecroBot
The soon to be ultimate moderation bot for all discord server, providing a wide array of tools to keep the peace. Expanding the moderation tools given by Discord tenfold. In addition, has a couple fun commands that can always be used to keep yourself entertained. Necrobot aims to give the server moderators not only additional commands (mute, warn, ect...) but also expand upon the commands already present to help fight against hackers and annoying users such as the new `!blacklist` command.

__Hierachy Ladder:__
* 7: The Bot Smith - Bot Owners & Collaborators
* 6: NecroBot Admin - Trusted Friends
* 5: Server Owner - Given to owners of a server using NecroBot
* 4: Admin - Trusted members of indivudal servers
* 3: Semi-Admin - "Trainee" admins
* 2: Mods - active, helpful and mature members of individual servers
* 1: Helpers - helpful members of indidual servers
* 0: Users - members of servers

__User Pofile__ <br>
**EXP** - Every non-command message generates exp for the user <br>
**Money** - users can claim dailies and check their money

__Planned Features__
* [ ] **Modulability Overhaul** - allow server owners to set their own channels, welcome message and others server-specifc settings.
* [x] **Overhaul to expand user profile** - server-specific permission, more compact, imporved code
* [ ] **Server Roles for Bot Roles** - Give server owners the ability to assign server roles to the bot roles and thereby the ability to grant a bot role by simply granting the equivalent server roles
* [ ] **EXP System** - longer exp cooldown, level up system, random amount of exp
* [ ] **Money System** - actual use of money, transfers between users
* [x] **Help system** - rewamp into something more compact, allows user to add an argument to look up a detailed description of a command.
* [x] **Wikia System** - make a more efficient use of the Wikia API system to allow users to find more out on their favorite wiki

__Command List (may not always be up to date)__
* `!claim` - claim your daily bonus. (Any)
* `!balance [@User]` - check your balance (if no argument is provided) or the balance of another user. (Any)
* `!calc [equation]` - evaluates equation us `+` to add, `-` to minus, `*` to multiply, `/` to divide, `**` for exponents, `%` for modulo. (Any)
* `!h ` - for this help bar. (Any)
* `!edain [article]` - search for an article on the Edain wiki. Content will be displayed if found, else a list of relevant articles will be provided. (Any)
* `!lotrfact` - prints one of sixty lotr facts at random. (Any)
* `!rr [int]` - a good old game of russian roulette. Provide an int between 1 and 6. If none are provided will default to 5. (Any)
* `!lotr [article]` - search for an article on the LOTR wiki. Content will be displayed if found, else a list of relevant articles will be provided. (Any)
* `!info [@User]` - check your info (if no argument is provided) or the info of another user (Any)
* `!tarot` - reads your fate in the cards using the art of tarology (Any)


__Moderations Commands__
* `!kill` - saves all the files and sys.exit() the bot (Bot Owner Only)
* `!add [operator] [intenger] [@User]` - adds [operator][intenger] to the balance of [@User] (Permission level of 6+ (NecroBot Admins))
* `!setStats [@User]` - sets default stats for @User (Permission level of 2+ (Mod))
* `!perms [@User] [0-6]` - sets permission level which dictates what commands can be used, can only set a permission level lower then itself. (Permission level of 4+ for basic access (Server Admin))
* `!setAll` - sets the default stats for all user not already registered on the server (Permission leve of 6+ (NecroBot Admin))
* `!ignored` - prints the list of Users/Channels ignored by the automoderation system and the list of Users/Channels ignored by the bot (Any)
* `!mute [seconds] [@User(s)]` - mutes all the users mentionned for the amount of seconds provided, if no seconds argument is provided, indefinitely. (Permission level of 2+ (Mod))
* `!unmute [@User(s)]` - unmutes all muted users mentionned. (Permission level of 2+ (Mod))
* `!speak [channelID] [message]` - broadcasts a message to the channel provided by proxy of the bot (Permission level of 4+ (Server Admin))
* `!warn (add | del) [@User] [message | position]` - add or remove a warning from the user's warning list to add simply use add and then specify a user and message to remove simply us del and then specify a user and the position of the warning to be removed (positions start at 0) (Permission level of 1+ (Helper) to add warnings and 3+ (Semi Admin) to remove a warnings)
* `!purge [number]` - purge [number] of messages from the channel it's summoned in (Permission level of 4+ (Server Admin))
* `!automod ( add | del ) [ @Users | #channels ]` - add/removes the channels/users from the necrobot automoderation, this means users/channels will no longer be affected by the spam filter, editition tracking and deletion tracking. (Permission leve of 5+ (Server Owner))
* `!ignore ( add | del ) [ @Users | #channels ]` - add/removes the channels/users from the necrobot ignore list which affects whether or not users can use commands and necrobot can be summoned in channels. (Permission leve of 4+ (Server Admin))
* `!blacklist [@User]` - the latest advancement in banning tech, will ban a user and add them to the list which will ban the user if they try to join any of the servers with necrobot, high permission level due to power. (Permission level of 6+ (NecroBot Admin))


__Moderation Features__
* **Message Deletion Tracking** - tracks deleted messages and prints deleted messages in a separate channel
* **Message Edition Tracking** - tracks edits made to message and prints the before and after in a separate channel
* **User Welcome** - welcome new users with a message and assigns them their own username as their server nickname
* **Spam Prevention** - different messages spammed within a 2 second interval or identical message spammed within a 4 second interval will be deleted

Join to see in action: https://discord.gg/sce7jmB <br>
Tell them GitHub sent you!
