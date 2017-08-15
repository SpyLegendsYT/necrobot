#!/usr/bin/python3.6
import ast
import csv
import json

class Data():
    def __init__(self, serverData, userData, superDuperIgnoreList):
        self.serverData = serverData
        self.userData = userData
        self.superDuperIgnoreList = superDuperIgnoreList

    serverData = dict()
    userData = dict()

    with open("C:\\Users\\Clement\\Desktop\\necrobot\\rings\\botdata\\userdata.csv","r") as f:
        reader = csv.reader(f)
        for row in reader:
            permsDict = ast.literal_eval(row[5])
            userData[row[0]] = {"money":int(row[1]),"daily":row[2],"title":row[3],"exp":int(row[4]),"perms":permsDict,"warnings":row[6].split(","),"lastMessage":"","lastMessageTime":0, "locked":""}

    with open("C:\\Users\\Clement\\Desktop\\necrobot\\rings\\botdata\\setting.csv","r") as f:
        reader = csv.reader(f)
        superDuperIgnoreList = list(next(reader))
        next(reader)
        for row in reader:
            tagsDict = ast.literal_eval(row[10])
            serverData[row[1]] = {"mute":row[2],"automod":row[3],"welcome-channel":row[4], "selfRoles":row[5].split(","),"ignoreCommand":row[6].split(","),"ignoreAutomod":row[7].split(","),"welcome":row[8],"goodbye":row[9],"tags":tagsDict}

