#
# Copyright (C) 2024 by TheTeamVivek@Github, < https://github.com/TheTeamVivek >.
#
# This file is part of < https://github.com/TheTeamVivek/YukkiMusic > project,
# and is released under the MIT License.
# Please see < https://github.com/TheTeamVivek/YukkiMusic/blob/master/LICENSE >
#
# All rights reserved
import os
import sys
from typing import List, Dict

import yaml

languages = {}
commands = {}

languages_present = {}


def get_command(value: str, language: str = "en") -> List[str]:
    if value not in commands:
        available_commands = ", ".join(commands.keys())
        raise ValueError(
            f"Command '{value}' does not exist. "
            f"Please ensure the command is defined in the YAML files under './strings/commands/'. "
            f"Available commands are: {available_commands}"
        )
    
    return commands[value].get(language, [])


def command(cmd: str, language: str = "en") -> str:
    cmds = " ".join([f"/{c}" for c in get_command(cmd, language)])
    return cmds



def get_string(lang: str):
    return languages[lang]


for filename in os.listdir(r"./strings/commands"):
    if filename.endswith(".yml"):
        language_code = filename[:-4]
        with open(f"./strings/commands/{filename}", encoding="utf8") as file:
            language_commands = yaml.safe_load(file)
        for command_key, command_list in language_commands.items():
            if command_key not in commands:
                commands[command_key] = {}
            commands[command_key][language_code] = command_list



for filename in os.listdir(r"./strings/langs/"):
    if "en" not in languages:
        languages["en"] = yaml.safe_load(
            open(r"./strings/langs/en.yml", encoding="utf8")
        )
        languages_present["en"] = languages["en"]["name"]
    if filename.endswith(".yml"):
        language_name = filename[:-4]
        if language_name == "en":
            continue
        languages[language_name] = yaml.safe_load(
            open(r"./strings/langs/" + filename, encoding="utf8")
        )
        for item in languages["en"]:
            if item not in languages[language_name]:
                languages[language_name][item] = languages["en"][item]
    try:
        languages_present[language_name] = languages[language_name]["name"]
    except:
        print(
            "There is some issue with the language file inside bot. Please report it to the TheTeamvk at @TheTeamvk on Telegram"
        )
        sys.exit()




