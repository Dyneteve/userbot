# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.b (the "License");
# you may not use this file except in compliance with the License.
#

""" Userbot module for executing code and terminal commands from Telegram. """

import asyncio
import subprocess
from getpass import getuser

# from userbot import *

from userbot import HELPER, LOGGER, LOGGER_GROUP
from userbot.events import register


@register(outgoing=True, pattern="^.eval")
async def evaluate(query):
    """ For .eval command, evaluates the given Python expression. """
    if not query.text[0].isalpha() and query.text[0] not in ("/", "#", "@", "!"):
        if query.is_channel and not query.is_group:
            await query.edit("`Eval isn't permitted on channels`")
            return
        evaluation = eval(query.text[6:])
        if evaluation:
            if isinstance(evaluation) == "str":
                if len(evaluation) > 4096:
                    file = open("output.txt", "w+")
                    file.write(evaluation)
                    file.close()
                await query.client.send_file(
                    query.chat_id,
                    "output.txt",
                    reply_to=query.id,
                    caption="`Output too large, sending as file`",
                )
                subprocess.run(["rm", "sender.txt"], stdout=subprocess.PIPE)
        await query.edit(
            "**Query: **\n`"
            + query.text[6:]
            + "`\n**Result: **\n`"
            + str(evaluation)
            + "`"
        )
    else:
        await query.edit(
            "**Query: **\n`"
            + query.text[6:]
            + "`\n**Result: **\n`No Result Returned/False`"
        )
    if LOGGER:
        await query.client.send_message(
            LOGGER_GROUP, "Eval query " +
            query.text[6:] + " was executed successfully"
        )


@register(outgoing=True, pattern=r"^.exec (.*)")
async def run(run_q):
    """ For .exec command, which executes the dynamically created program """
    if not run_q.text[0].isalpha() and run_q.text[0] not in ("/", "#", "@", "!"):
        if run_q.is_channel and not run_q.is_group:
            await run_q.edit("`Exec isn't permitted on channels`")
            return
        code = run_q.raw_text[5:]
        exec(f"async def __ex(e): " + ""
             .join(f"\n {l}" for l in code.split("\n")))
        result = await locals()["__ex"](run_q)
        if result:
            if len(result) > 4096:
                file = open("output.txt", "w+")
                file.write(result)
                file.close()
                await run_q.client.send_file(
                    run_q.chat_id,
                    "output.txt",
                    reply_to=run_q.id,
                    caption="`Output too large, sending as file`",
                )
                subprocess.run(["rm", "output.txt"], stdout=subprocess.PIPE)

            await run_q.edit(
                "**Query: **\n`"
                + run_q.text[5:]
                + "`\n**Result: **\n`"
                + str(result) + "`"
            )
        else:
            await run_q.edit(
                "**Query: **\n`"
                + run_q.text[5:]
                + "`\n**Result: **\n`"
                + "No Result Returned/False"
                + "`"
            )

        if LOGGER:
            await run_q.client.send_message(
                LOGGER_GROUP,
                "Exec query " + run_q.text[5:] + " was executed successfully"
            )


@register(outgoing=True, pattern="^.term(?: |$)(.*)")
async def terminal_runner(term):
    """ For .term command, runs bash commands and scripts on your server. """
    if not term.text[0].isalpha() and term.text[0] not in ("/", "#", "@", "!"):
        curruser = getuser()
        command = term.pattern_match.group(1)

        if term.is_channel and not term.is_group:
            await term.edit("`Term commands aren't permitted on channels!`")
            return

        if not command:
            await term.edit("``` Give a command or use .help term for \
                an example.```")
            return

        if command in ("userbot.session", "config.env"):
            await term.edit("`That's a dangerous operation! Not Permitted!`")
            return

        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        result = str(stdout.decode().strip()) \
            + str(stderr.decode().strip())

        if len(result) > 4096:
            output = open("output.txt", "w+")
            output.write(result)
            output.close()
            await term.client.send_file(
                term.chat_id,
                "output.txt",
                reply_to=term.id,
                caption="`Output too large, sending as file`",
            )
            subprocess.run(["rm", "output.txt"], stdout=subprocess.PIPE)
            return
        await term.edit(
            "`"
            f"{curruser}:~# {command}"
            f"\n{result}"
            "`"
        )

        if LOGGER:
            await term.client.send_message(
                LOGGER_GROUP,
                "Terminal Command " + command + " was executed sucessfully",
            )

HELPER.update({
    "eval": ".eval 2 + 3\nUsage: Evalute mini-expressions."
})
HELPER.update({
    "exec": ".exec print('hello')\nUsage: Execute small python scripts."
})
HELPER.update({
    "term": "Run bash commands and scripts on your server. Usage: \n .term ls"
})
