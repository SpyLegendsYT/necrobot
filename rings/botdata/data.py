#!/usr/bin/python3.6
import ast
import csv
import sys
default_path = sys.argv[3]

class Data():
    def __init__(self, serverData, userData, superDuperIgnoreList):
        self.serverData = serverData
        self.userData = userData
        self.superDuperIgnoreList = superDuperIgnoreList

    serverData = dict()
    userData = dict()

    with open(default_path + "userdata.csv","r") as f:
        reader = csv.reader(f)
        for row in reader:
            permsDict = ast.literal_eval(row[5])
            userData[row[0]] = {"money":int(row[1]),"daily":row[2],"title":row[3],"exp":int(row[4]),"perms":permsDict,"warnings":row[6].split(","),"lastMessage":"","lastMessageTime":0, "locked":""}

    with open(default_path + "setting.csv","r") as f:
        reader = csv.reader(f)
        superDuperIgnoreList = list(sys.argv[4])
        next(reader)
        next(reader)
        for row in reader:
            tagsDict = ast.literal_eval(row[9])
            serverData[row[0]] = {"mute":row[1],"automod":row[2],"welcome-channel":row[3], "selfRoles":row[4].split(","),"ignoreCommand":row[5].split(","),"ignoreAutomod":row[6].split(","),"welcome":row[7],"goodbye":row[8],"tags":tagsDict, "prefix":row[10]}

