# NecroBot
The soon to be ultimate moderation bot for all discord server, providing a wide array of tools to keep the peace. Expanding the moderation tools given by Discord tenfold. In addition, has a couple fun commands that can always be used to keep yourself entertained.

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
* `!add [operator] [intenger] [@User]` - adds [operator][intenger] to the balance of [@User] (Permission level of 3+)
* `!setStats [@User]` - sets default stats for @User (Permission level of 2+)
* `!perms [@User] [Title]` - sets title, which is also responsible for permission level (Permission level of 4+)
* `!setAll` - sets the default stats for all user not already registered on the server (Bot Owner Only)
* `!ignore` - prints the list of Users ignored by the bot's automoderation system and the list of channels ignored by the bot (Any)
* `!mute [seconds] [@User(s)]` - mutes all the users mentionned for the amount of seconds provided, if no seconds argument is provided, indefinitely. (Permission level of 2+)
* `!unmute [@User(s)]` - unmutes all muted users mentionned. (Permission level of 2+)
* `!ignore ([@User] | [#channel])` - ignores/unignores channels/user (Permission level of 3+)
* `!speak [channelID] [message]` - broadcasts a message to the channel provided by proxy of the bot (Permission level of 4+)
* `!warn (add | del) [@User] [message | position]` - add or remove a warning from the user's warning list to add simply use add and then specify a user and message to remove simply us del and then specify a user and the position of the warning to be removed (positions start at 0)
* `!purge [number]` - purge [number] of messages


__Moderation Features__
* **Message Deletion Tracking** - tracks deleted messages and prints deleted messages in a separate channel
* **Message Edition Tracking** - tracks edits made to message and prints the before and after in a separate channel
* **User Welcome** - welcome new users with a message
* **Spam Prevention** - different messages spammed within a 2 second interval or identical message spammed within a 4 second interval will be deleted

Join to see in action: https://discord.gg/sce7jmB

Tell them GitHub sent you.
