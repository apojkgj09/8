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
import re
from typing import Union, List, Dict
from pyrogram import Client, filters
from pyrogram.types import Message
from YukkiMusic.utils.database import get_lang

import yaml

languages = {}
commands = {}

languages_present = {}


def get_command(value: str, language: str = "en", include_english: bool = True) -> List[str]:
    if value not in commands:
        available_commands = ", ".join(commands.keys())
        raise KeyError(
            f"Command '{value}' does not exist. "
            f"Please ensure the command is defined in the YAML files under './strings/cmds/'. "
            f"Available commands are: {available_commands}"
        )
    command_list = commands[value].get(language, [])
    if include_english and language != "en":
        command_list += commands[value].get("en", [])
    return command_list


def command(cmd: str) -> str:
    if value not in commands:
        available_commands = ", ".join(commands.keys())
        raise KeyError(
            f"Command '{value}' does not exist. "
            f"Please ensure the command is defined in the YAML files under './strings/cmds/'. "
            f"Available commands are: {available_commands}"
        )
    command_list = commands[cmd].get("en", [])



def get_string(lang: str):
    return languages[lang]


for filename in os.listdir(r"./strings/cmds"):
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

def cmd(commands_key: Union[str, List[str]], prefixes: Union[str, List[str]] = "/", case_sensitive: bool = False):
    command_re = re.compile(r"([\"'])(.*?)(?<!\\)\1|(\S+)")

    async def func(flt, client: Client, message: Message):
        username = client.me.username or ""
        text = message.text or message.caption
        message.command = None

        if not text:
            return False

        lang_key = await get_lang(message.chat.id)

        if isinstance(commands_key, str):
            keys = [commands_key]
        else:
            keys = commands_key

        command_list = []
        for key in keys:
            try:
                command_list += get_command(key, lang_key, include_english=True)
            except KeyError:
                command_list += get_command(key, "en", include_english=False)

        prefixes_to_use = list(flt.prefixes)
        if lang_key != "en" and "" not in prefixes_to_use:
            prefixes_to_use.append("")

        for prefix in prefixes_to_use:
            if not text.startswith(prefix):
                continue

            without_prefix = text[len(prefix):]

            for cmd in command_list:
                if not re.match(rf"^(?:{cmd}(?:@?{username})?)(?:\s|$)", without_prefix,
                                flags=re.IGNORECASE if not flt.case_sensitive else 0):
                    continue

                without_command = re.sub(rf"{cmd}(?:@?{username})?\s?", "", without_prefix, count=1,
                                         flags=re.IGNORECASE if not flt.case_sensitive else 0)

                message.command = [cmd] + [
                    re.sub(r"\\([\"'])", r"\1", m.group(2) or m.group(3) or "")
                    for m in command_re.finditer(without_command)
                ]
                return True

        return False

    prefixes = [] if prefixes is None else prefixes
    prefixes = prefixes if isinstance(prefixes, list) else [prefixes]
    prefixes = set(prefixes) if prefixes else {""}

    return filters.create(
        func,
        "CustomCommandFilter",
        prefixes=prefixes,
        commands_key=commands_key,
        case_sensitive=case_sensitive
    )
filters.cmd = cmd