#!/usr/bin/python3.6
import ast
import csv
import sys

class Data():
    def __init__(self):
        self.server_data = dict()
        self.user_data = dict()

    path = "rings/utils/data/"
    with open(path + "user_data.csv","r") as f:
        reader = csv.reader(f)
        for row in reader:
            permsDict = ast.literal_eval(row[5])
            self.user_data[int(row[0])] = {"money":int(row[1]),"daily":row[2],"title":row[3],"exp":int(row[4]),"perms":permsDict,"warnings":row[6].split(","),"lastMessage":"","lastMessageTime":0, "locked":""}

    with open(path + "server_settings.csv","r") as f:
        reader = csv.reader(f)
        for row in reader:
            tagsDict = ast.literal_eval(row[9])
            self.server_data[int(row[0])] = {"mute":row[1],"automod":row[2],"welcome-channel":row[3], "selfRoles":row[4].split(","),"ignoreCommand":row[5].split(","),"ignoreAutomod":row[6].split(","),"welcome":row[7],"goodbye":row[8],"tags":tagsDict, "prefix":row[10], "broadcast": row[11] , "broadcast-channel": row[12], "starboard": row[13], "starboard-count": row[14]}

