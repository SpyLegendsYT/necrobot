#!/usr/bin/python3.6
import ast
import csv
import sys
default_path = sys.argv[3]

class Data():
    def __init__(self, serverData, userData, superDuperIgnoreList, starboard_messages):
        self.serverData = serverData
        self.userData = userData
        self.superDuperIgnoreList = superDuperIgnoreList
        self.starboard_messages = starboard_messages

    serverData = dict()
    userData = dict()
    superDuperIgnoreList = list()
    starboard_messages = dict()

    with open(default_path + "userdata.csv","r") as f:
        reader = csv.reader(f)
        for row in reader:
            permsDict = ast.literal_eval(row[5])
            userData[row[0]] = {"money":int(row[1]),"daily":row[2],"title":row[3],"exp":int(row[4]),"perms":permsDict,"warnings":row[6].split(","),"lastMessage":"","lastMessageTime":0, "locked":""}

    with open(default_path + "setting.csv","r") as f:
        reader = csv.reader(f)
        superDuperIgnoreList= (sys.argv[4])
        starboard_messages = ast.literal_eval(next(reader)[0])
        for row in reader:
            tagsDict = ast.literal_eval(row[9])
            serverData[row[0]] = {"mute":row[1],"automod":row[2],"welcome-channel":row[3], "selfRoles":row[4].split(","),"ignoreCommand":row[5].split(","),"ignoreAutomod":row[6].split(","),"welcome":row[7],"goodbye":row[8],"tags":tagsDict, "prefix":row[10], "broadcast": row[11] , "broadcast-channel": row[12], "starboard": row[13], "starboard-count": row[14]}

