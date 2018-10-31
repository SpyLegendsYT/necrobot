import psycopg2
from config import dbpass

def db_gen():
    server_data = {}
    user_data = {}
    conn = psycopg2.connect(dbname="postgres", user="postgres", password=dbpass)
    cur = conn.cursor()

    #create server cache
    cur.execute("SELECT * FROM necrobot.Guilds;")
    for g in cur.fetchall():
        server_data[g[0]] = {
            "mute": g[1] if g[1] != 0 else "", 
            "automod":g[2] if g[2] != 0 else "", 
            "welcome-channel":g[3] if g[3] != 0 else "", 
            "welcome":g[4], 
            "goodbye":g[5], 
            "prefix":g[6],
            "broadcast-channel":g[7] if g[7] != 0 else "",
            "broadcast":g[8],
            "broadcast-time":g[9],
            "starboard-channel":g[10] if g[10] != 0 else "",
            "starboard-limit":g[11],
            "auto-role":g[12] if g[12] != 0 else "",
            "auto-role-timer":g[13] if g[13] is not None else 0,
            "self-roles":[],
            "ignore-command":[],
            "ignore-automod":[],
            "tags":{},
            "disabled":[],
            "aliases":{}
        }

    cur.execute("SELECT * FROM necrobot.SelfRoles;")
    for g in cur.fetchall():
        server_data[g[0]]["self-roles"].append(g[1])

    cur.execute("SELECT * FROM necrobot.Disabled;")
    for g in cur.fetchall():
        server_data[g[0]]["disabled"].append(g[1])

    cur.execute("SELECT * FROM necrobot.IgnoreAutomod;")
    for g in cur.fetchall():
        server_data[g[0]]["ignore-automod"].append(g[1])

    cur.execute("SELECT * FROM necrobot.IgnoreCommand;")
    for g in cur.fetchall():
        server_data[g[0]]["ignore-command"].append(g[1])

    cur.execute("SELECT * FROM necrobot.Tags;")
    for g in cur.fetchall():
        server_data[g[0]]["tags"][g[1]] = {
            "content":g[2], 
            "owner":g[3], 
            "counter":g[4], 
            "created":g[5]
        }

    #create user cache
    cur.execute("SELECT * FROM necrobot.Users;")
    for u in cur.fetchall():
        user_data[u[0]] = {
            "money": u[1],
            "exp": u[2],
            "daily": u[3],
            "badges": u[4].split(",") if u[4] != "" else [],
            "title":u[5],
            "tutorial": u[6] == 'True',
            "perms":{},
            "waifu":{},
            "places":{},
            "warnings":{}
        }

    cur.execute("SELECT * FROM necrobot.Permissions;")
    for u in cur.fetchall():
        user_data[u[1]]["perms"][u[0]] = u[2]
        user_data[u[1]]["warnings"][u[0]] = []

    cur.execute("SELECT * FROM necrobot.Warnings;")
    for u in cur.fetchall():
        user_data[u[1]]["warnings"][u[3]].append(u[4])

    cur.execute("SELECT * FROM necrobot.Badges;")
    for u in cur.fetchall():
        user_data[u[0]]["places"][u[1]] = u[2]

    cur.execute("SELECT * FROM necrobot.Waifu;")
    for u in cur.fetchall():
        user_data[u[0]]["waifu"][u[1]] = {
            "waifu-value":u[2],
            "waifu-claimer": u[3] if u[3] != 0 else "",
            "affinity": u[4] if u[4] != 0 else "",
            "heart-changes":u[5],
            "divorces":u[6],
            "flowers":u[7],
            "waifus":[],
            "gifts":{}
        }

    cur.execute("SELECT * FROM necrobot.Waifus;")
    for u in cur.fetchall():
        user_data[u[0]]["waifu"][u[1]]["waifus"].append(u[2])

    cur.execute("SELECT * FROM necrobot.Gifts;")
    for u in cur.fetchall():
        user_data[u[0]]["waifu"][u[1]]["gifts"][u[2]] = u[3]

    cur.execute("SELECT * FROM necrobot.Starred;")
    starred = [x[0] for x in cur.fetchall()]

    cur.execute("SELECT * FROM necrobot.Aliases;")
    for t in cur.fetchall():
        server_data[t[2]]["aliases"][t[0]] = t[1]

    return user_data, server_data, starred
