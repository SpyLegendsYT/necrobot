import random
import csv

class HungerGames():
    def _event_parser(self, filename):
        event_list = list()
        with open(filename) as f:
            reader = csv.reader(f)
            for row in reader:
                event_list.append({"tributes" : int(row[0]), "killed" : list(row[1]), "string" : row[2]})
        return event_list

    def __init__(self, tributes_list):
        self.tributes_list = tributes_list
        self.game_start_events = self._event_parser("game_start_data.csv")
        self.day_events = self._event_parser("day_data.csv")
        self.night_events = self._event_parser("night_data.csv")
        self.feast_events = self._event_parser("feast_data.csv")
        self.dead_list = list()

    def _phase_parser(self, event_list):
        idle_tributes = self.tributes_list
        idle_events = event_list
        while len(idle_tributes) > 0 and len(self.tributes_list) > 1:
            tributes = list()
            event = random.choice([event for event in idle_events if event["tributes"] <= len(idle_tributes) and len(event["killed"]) < len(self.tributes_list)])
            tributes = random.sample(idle_tributes, event["tributes"])
            idle_tributes = [x for x in idle_tributes if x not in tributes]
            idle_events.remove(event)
            if len(event["killed"]) > 0:
                for killed in event["killed"]:
                    tribute = tributes[int(killed)-1]
                    self.tributes_list.remove(tribute)
                    self.dead_list.append(tribute)

            format_dict = dict()
            for tribute in tributes:
                format_dict["p"+str(tributes.index(tribute)+1)] = tribute

            print(event["string"].format(**format_dict))

    def main(self):
        print("GAME START")
        self._phase_parser(self.game_start_events)
        input()
        day = 0
        while len(self.tributes_list) > 1:
            if day == 6:
                self._phase_parser(self.feast_events)

            self._phase_parser(self.day_events)
            input()

            print("Dead Tributes: " + ", ".join(self.dead_list))
            self.dead_list = list()
            input()

            self._phase_parser(self.night_events)
            input()

        print(self.tributes_list[0] + " is the Winner!")

hunger = HungerGames(["John", "Lauren", "Tammy", "Danny", "Bruce", "Jeremy", "Dawn", "Richard", "Flora", "Rodney", "Rose", "Leland", "Pablo", "Glenn", "Eloise", "Yvonne", "Celia", "Paula", "Rosa", "Fred", "Lynne", "Paul", "Clyde", "Traci"])
hunger.main()