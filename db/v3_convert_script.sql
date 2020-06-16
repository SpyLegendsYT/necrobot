#user converion to new format
INSERT INTO necrobot.Users (user_id, necroins, exp, daily, title, tutorial)
SELECT user_id, necroins::bigint, exp, current_date, title, False 
FROM necrobot_v2.Users

#badge conversion to new format
INSERT INTO necrobot.Badges (user_id, badge, spot)
SELECT user_id, badge, 0
FROM (
    SELECT u.user_id, unnest(string_to_array(u.badges, ','))
    FROM necrobot_v2.Users u
)

#guild conversion to new format
INSERT INTO necrobot.Guilds
SELECT 
    guild_id, mute, automod_channel, welcome_channel, welcome_message, goodbye_message, 
    prefix, broadcast_channel, broadcast_message, broadcast_time, starboard_channel, starboard_limit, 
    auto_role, auto_role_timer, False
FROM necrobot_v2.Guilds

#permission conversion to new format
INSERT INTO necrobot.Permissions
SELECT guild_id, user_id, level
FROM necrobot_v2.Permissions

#disabled conversion to new format
INSERT INTO necrobot.Disabled
SELECT guild_id, command
FROM necrobot_v2.Disabled

#ignore automod conversion to the new format
INSERT INTO necrobot.IgnoreAutomod
SELECT guild_id, id
FROM necrobot_v2.IgnoreAutomod

#ignore command conversion to the new format
INSERT INTO necrobot.IgnoreCommand
SELECT guild_id, id
FROM necrobot_v2.IgnoreCommand

#self roles conversion to new format
INSERT INTO necrobot.SelfRoles
SELECT guild_id, role_id
FROM necrobot_v2.SelfRoles

#starred messages conversion
INSERT INTO necrobot.Starred
SELECT message_id, starred_id, guild_id, user_id
FROM necrobot_v2.Starred

#polls conversion to the new system
INSERT INTO necrobot.Polls
SELECT message_id, 327175434754326539, concat('https://discordapp.com/channels/327175434754326539/504389672945057799/', message_id), 1
FROM necrobot_v2.Polls

#votes conversion to the new system
INSERT INTO necrobot.Votes
SELECT message_id, user_id, reaction
FROM necrobot_v2.Votes

#yt rss conversion to the new system
INSERT INTO necrobot.Youtube
SELECT guild_id, channel_id, youtuber_id, NOW(), filter
FROM necrobot_v2.Youtube

#leaderboard conversion to the new system
INSERT INTO necrobot.Leaderboards
SELECT guild_id, message, symbol
FROM necrobot_v2.Leaderboards

#leaderboard points conversion to the new system
INSERT INTO necrobot.LeaderboardPoints
SELECT user_id, guild_id, points
FROM necrobot_v2.LeaderboardPoints

#tag conversion to the new system
INSERT INTO necrobot.Tags
SELECT guild_id, name, content, owner_id, uses, created_at
FROM necrobot_v2.Tags

INSERT INTO necrobot.Aliases
SELECT name, name, guild_id
FROM necrobot_v2.Tags

#aliases conversion to the new system
INSERT INTO necrobot.Aliases
SELECT alias, original, guild_id
FROM necrobot_v2.Aliases

#warnings conversion to the new system
INSERT INTO necrobot.Warnings
SELECT warn_id, user_id, issuer_id, guild_id, warning_content, to_timestamp(date_issued, 'YYYY-MM-DD HI:MI:SS.US')
FROM necrobot_v2.Warnings

#NOT CONVERTED
#Logs - just start new
#BadgeShop - new in v3
#Reminders - all reminders are cancelled (depending on how many there are at the time of switch)
#Invites - get latest
#MU - not officially implemented yet, no conversion
#MU_Users - not officially implemented yet, no conversion
#Waifu - discountinued feature
#Waifus - discontinued feature
#Gifts - discountinued feature
