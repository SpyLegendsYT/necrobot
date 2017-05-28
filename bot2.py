import discord
import asyncio

import random as rand
import csv

moneyList = {}

with open('data/balances.csv', 'r') as csvfile:
    spamreader = csv.reader(csvfile)
    for row in spamreader:
        moneyList[row[0]] = int(row[1])
print("List of balances: ",moneyList)

client = discord.Client()

@client.event
async def on_ready():
    await client.change_presence(game=discord.Game(name='shipping Necro x Elfu'))
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_message(message):
    if message.content.startswith('n.'):
        print(message.author,"used me")
        print("-------------")
        message.content = message.content.replace("n.","")
        if message.content.startswith("randint"):
            randint = rand.randint(0,100)
            await client.send_message(message.channel, "Here is your random intenger, <@"+message.author.id+">: "+str(randint))
        elif message.content.startswith("balance"):
            await client.send_message(message.channel, ":atm: | **"+message.author.name+"**, you have **"+ str(moneyList[message.author.discriminator]) +"** :euro:")
        elif message.content.startswith("exit"):
            with open("data/balances.csv") as csvfile:
                spamwriter = csv.writer(csvfile)
                for x in moneyList:
                    spamwriter.writerow([x, str(moneyList[x])])
                    await client.send_message(message.channel, "Ready to be shut down")

client.run("MzE3NjE5MjgzMzc3MjU4NDk3.DAnHFw.k6AsGJHruY3BjvjK_g3B_zsAMdg")