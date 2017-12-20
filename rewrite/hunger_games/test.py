import csv
import random

counter = 0
event_list = list()

with open("game_start_data.csv") as f:
    reader = csv.reader(f)
    for row in reader:
        event_list.append({"tributes" : int(row[0]), "killed" : list(row[1]), "string" : row[2]})

tributes_list = ["bob", "john", "smith", "sam", "robert", "gerald", "percy", "anabeth", "the thing"]

def phase_parser():
    idle_tributes = tributes_list
    idle_events = event_list
    while len(idle_tributes) > 1:
        tributes = list()
        event = random.choice([event for event in idle_events if event["tributes"] < len(idle_tributes)])
        tributes = random.sample(idle_tributes, event["tributes"])
        idle_tributes = [x for x in idle_tributes if x not in tributes]
        idle_events.remove(event)
        if len(event["killed"]) > 0:
            for killed in event["killed"]:
                tribute = tributes[int(killed)-1]
                tributes_list.remove(tribute)
                dead_list.append(tribute)

        format_dict = dict()
        for tribute in tributes:
            format_dict["p"+str(tributes.index(tribute)+1)] = tribute

        print(event["string"].format(**format_dict))

while len(tributes_list) > 1:
    dead_list = list()
    phase_parser()
    print("Living " + str(tributes_list))
    print("Dead " + str(dead_list))

print(tributes_list[0] + " is the winner!")




