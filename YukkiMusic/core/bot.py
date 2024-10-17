#
# Copyright (C) 2024 by TheTeamVivek@Github, < https://github.com/TheTeamVivek >.
#
# This file is part of < https://github.com/TheTeamVivek/YukkiMusic > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/TheTeamVivek/YukkiMusic/blob/master/LICENSE >
#
# All rights reserved.
#
import uvloop

uvloop.install()


import sys

from pyrogram import Client
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import (
    ChatSendPhotosForbidden,
    ChatWriteForbidden,
    FloodWait,
)
from pyrogram.types import (
    BotCommand,
    BotCommandScopeAllChatAdministrators,
    BotCommandScopeAllGroupChats,
    BotCommandScopeAllPrivateChats,
)

import config

from ..logging import LOGGER


class YukkiBot(Client):
    def __init__(self):
        LOGGER(__name__).info(f"Starting Bot")
        super().__init__(
            "YukkiMusic",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN,
            in_memory=True,
        )

    async def edit_message_text(self, *args, **kwargs):
        try:
            return await super().edit_message_text(*args, **kwargs)
        except FloodWait as e:
            time = int(e.value)
            await asyncio.sleep(time)
            if time < 25:
                return await self.edit_message_text(self, *args, **kwargs)

    async def send_message(self, *args, **kwargs):
        if kwargs.get("send_direct", False):
            kwargs.pop("send_direct", None)
            return await super().send_message(*args, **kwargs)

        try:
            return await super().send_message(*args, **kwargs)
        except FloodWait as e:
            time = int(e.value)
            await asyncio.sleep(time)
            if time < 25:
                return await self.send_message(self, *args, **kwargs)
        except ChatWriteForbidden:
            chat_id = kwargs.get("chat_id") or args[0]
            if chat_id:
                await self.leave_chat(chat_id)
                

    async def send_photo(self, *args, **kwargs):
        try:
            return await super().send_photo(*args, **kwargs)
        except FloodWait as e:
            time = int(e.value)
            await asyncio.sleep(time)
            if time < 25:
                return await self.send_photo(self, *args, **kwargs)
        except ChatSendPhotosForbidden:
            chat_id = kwargs.get("chat_id") or args[0]
            if chat_id:
                await self.send_message(chat_id, "I don't have the right to send photos in this chat, leaving now..")
                await self.leave_chat(chat_id)

    async def start(self):
        await super().start()
        get_me = await self.get_me()
        self.username = get_me.username
        self.id = get_me.id
        self.name = self.me.first_name + " " + (self.me.last_name or "")
        self.mention = self.me.mention

        try:
            await self.send_message(
                config.LOG_GROUP_ID,
                text=f"<u><b>{self.mention} Bot Started :</b><u>\n\nId : <code>{self.id}</code>\nName : {self.name}\nUsername : @{self.username}",
            )
        except:
            LOGGER(__name__).error(
                "Bot has failed to access the log group. Make sure that you have added your bot to your log channel and promoted as admin!"
            )
            # sys.exit()
        if config.SET_CMDS == str(True):
            try:
                await self.set_bot_commands(
                    commands=[
                        BotCommand("start", "Start the bot"),
                        BotCommand("help", "Get the help menu"),
                        BotCommand("ping", "Check if the bot is alive or dead"),
                    ],
                    scope=BotCommandScopeAllPrivateChats(),
                )
                await self.set_bot_commands(
                    commands=[
                        BotCommand("play", "Start playing requested song"),
                    ],
                    scope=BotCommandScopeAllGroupChats(),
                )
                await self.set_bot_commands(
                    commands=[
                        BotCommand("play", "Start playing requested song"),
                        BotCommand("skip", "Move to next track in queue"),
                        BotCommand("pause", "Pause the current playing song"),
                        BotCommand("resume", "Resume the paused song"),
                        BotCommand("end", "Clear the queue and leave voicechat"),
                        BotCommand("shuffle", "Randomly shuffles the queued playlist."),
                        BotCommand(
                            "playmode",
                            "Allows you to change the default playmode for your chat",
                        ),
                        BotCommand(
                            "settings",
                            "Open the settings of the music bot for your chat.",
                        ),
                    ],
                    scope=BotCommandScopeAllChatAdministrators(),
                )
            except:
                pass
        else:
            pass
        try:
            a = await self.get_chat_member(config.LOG_GROUP_ID, self.id)
            if a.status != ChatMemberStatus.ADMINISTRATOR:
                LOGGER(__name__).error("Please promote bot as admin in logger group")
                sys.exit()
        except Exception:
            pass
        if get_me.last_name:
            self.name = get_me.first_name + " " + get_me.last_name
        else:
            self.name = get_me.first_name
        LOGGER(__name__).info(f"MusicBot started as {self.name}")

    async def stop(self):
        await super().stop()



import inspect
import re
from typing import Callable, Union, List, Pattern, Optional

import pyrogram
from pyrogram import enums
from pyrogram.types import Message, CallbackQuery, InlineQuery, PreCheckoutQuery, InlineKeyboardMarkup, ReplyKeyboardMarkup, Update

create = pyrogram.filters.create


def command(commands: Union[str, List[str]], prefixes: Union[str, List[str]] = "/", case_sensitive: bool = False):
    """Filter commands, i.e.: text messages starting with "/" or any other custom prefix.

    Parameters:
        commands (``str`` | ``list``):
            The command or list of commands as string the filter should look for.
            Examples: "start", ["start", "help", "settings"]. When a message text containing
            a command arrives, the command itself and its arguments will be stored in the *command*
            field of the :obj:`~pyrogram.types.Message`.

        prefixes (``str`` | ``list``, *optional*):
            A prefix or a list of prefixes as string the filter should look for.
            Defaults to "/" (slash). Examples: ".", "!", ["/", "!", "."], list(".:!").
            Pass None or "" (empty string) to allow commands with no prefix at all.

        case_sensitive (``bool``, *optional*):
            Pass True if you want your command(s) to be case sensitive. Defaults to False.
            Examples: when True, command="Start" would trigger /Start but not /start.
    """
    command_re = re.compile(r"([\"'])(.*?)(?<!\\)\1|(\S+)")

    async def func(flt, client: pyrogram.Client, message: Message):
        username = client.me.username or ""
        text = message.text or message.caption
        message.command = None

        if not text:
            return False

        for prefix in flt.prefixes:
            if not text.startswith(prefix):
                continue

            without_prefix = text[len(prefix):]

            for cmd in flt.commands:
                if not re.match(rf"^(?:{cmd}(?:@?{username})?)(?:\s|$)", without_prefix,
                                flags=re.IGNORECASE if not flt.case_sensitive else 0):
                    continue

                without_command = re.sub(rf"{cmd}(?:@?{username})?\s?", "", without_prefix, count=1,
                                         flags=re.IGNORECASE if not flt.case_sensitive else 0)

                # match.groups are 1-indexed, group(1) is the quote, group(2) is the text
                # between the quotes, group(3) is unquoted, whitespace-split text

                # Remove the escape character from the arguments
                message.command = [cmd] + [
                    re.sub(r"\\([\"'])", r"\1", m.group(2) or m.group(3) or "")
                    for m in command_re.finditer(without_command)
                ]

                return True

        return False

    commands = commands if isinstance(commands, list) else [commands]
    commands = {c if case_sensitive else c.lower() for c in commands}

    prefixes = [] if prefixes is None else prefixes
    prefixes = prefixes if isinstance(prefixes, list) else [prefixes]
    prefixes = set(prefixes) if prefixes else {""}

    return create(
        func,
        "CommandFilter",
        commands=commands,
        prefixes=prefixes,
        case_sensitive=case_sensitive
    )

