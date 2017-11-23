
def default_stats(member, server):
    if member.id not in userData:
        userData[member.id] = {'money': 200, 'daily': '', 'title': '', 'exp': 0, 'perms': {}, 'warnings': [], 'lastMessage': '', 'lastMessageTime': 0, 'locked': ''}

    if server.id not in userData[member.id]["perms"]:
        if any(userData[member.id]["perms"][x] == 7 for x in userData[member.id]["perms"]):
            userData[member.id]["perms"][server.id] = 7
        elif any(userData[member.id]["perms"][x] == 6 for x in userData[member.id]["perms"]):
            userData[member.id]["perms"][server.id] = 6
        elif member.id == server.owner.id:
            userData[member.id]["perms"][server.id] = 5
        elif member.server_permissions.administrator:
            userData[member.id]["perms"][server.id] = 4
        else:
            userData[member.id]["perms"][server.id] = 0
            
def all_mentions(cont, msg):
    mention_list = []
    mentions = msg.split(" ")
    for x in mentions:
        ID = re.sub('[<>!#@]', '', x)
        if not bot.get_channel(ID) is None:
            channel = bot.get_channel(ID)
            mention_list.append(channel)
        elif not cont.message.server.get_member(ID) is None:
            member = cont.message.server.get_member(ID)
            mention_list.append(member)
    return mention_list

def has_perms(perms_level):
    def predicate(cont): 
        if cont.message.channel.is_private:
            return False
        return userData[cont.message.author.id]["perms"][cont.message.server.id] >= perms_level
    return commands.check(predicate)

def is_necro():
    def predicate(cont):
        return cont.message.author.id == "241942232867799040"
    return commands.check(predicate)