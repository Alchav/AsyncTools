"""This file was originally made as a quick & dirty helper tool, not meant for public eyes.
If you like good code, avert your eyes."""

import csv
import string
import yaml
import itertools
import sys


with open(sys.argv[1], 'r') as f:
    mystery = yaml.unsafe_load(f.read())

shuffles = {"bigkey_shuffle": "b", "compass_shuffle": "c", "map_shuffle": "m"}
ignored = {"open_pyramid"}
always = {"game", "accessibility", "progression_balancing"}

rows = []
players = list(mystery["name"].values())
START = 1
for START, player in enumerate(players, 1):
    if player.startswith("Player") and all(c in string.digits for c in player.lstrip("Player")):
        print("First generic player:", player, START)
        break
    print(player)
END = len(players) + 1
print(START, END)

print("unnamed players follow")
for p in range(START, END):
    row = {"keysanity": ""}
    for key, value in [(k, v) for k, v in mystery.items() if isinstance(v, dict)]:
        if not key in ignored:
            if p not in value:
                row[key] = None
                continue
            pvalue = value[p]
            try:
                pkey = getattr(pvalue, "current_key", pvalue)
            except:
                pass
            if key == "smallkey_shuffle":
                if pkey == "universal":
                    row["keysanity"] += "u"
                elif pkey != "original_dungeon":
                    row["keysanity"] += "s"
            elif key in shuffles:
                if pkey != "original_dungeon":
                    row["keysanity"] += shuffles[key]
            else:
                row[key] = pvalue
    row["keysanity"] = "".join(sorted(row["keysanity"]))
    rows.append(row)


def get_option_name(option):
    getter = getattr(option, "get_current_option_name", None)
    if getter:
        return getter()
    else:
        return option


def get_option_header(option, key):
    getter = getattr(option, "displayname", None)
    if getter:
        return getter
    else:
        return key


# filter identical options out
games = set(row["game"] for row in rows)
print("Games", games)
for game in games:
    remove = set()
    game_rows = [row for row in rows if row["game"] == game]
    for key, value in next(iter(game_rows)).items():
        if all(row[key] == value for row in game_rows):
            remove.add(key)
    remove -= {"game"}
    for key in remove:
        for row in game_rows:
            del row[key]

with open('mystery_result.csv', 'w') as mysterycsv:
    rows = [{get_option_header(data, key): get_option_name(data) for key, data in row.items()} for row in rows]
    fieldnames = set(itertools.chain.from_iterable(((key for key, value in dictionary.items() if value is not None)
                                                    for dictionary in rows)))
    writer = csv.DictWriter(mysterycsv, fieldnames=fieldnames, lineterminator='\n')

    writer.writeheader()

    for row in rows:
        writer.writerow({key: value for key, value in row.items() if key in fieldnames})

with open("mystery_players.csv", 'w') as mysterycsv:
    writer = csv.DictWriter(mysterycsv, fieldnames=["Slot", "Name"], lineterminator='\n')
    writer.writeheader()
    for i, name in enumerate(players, 1):
        writer.writerow({"Slot": i, "Name": name})

print("Done")
