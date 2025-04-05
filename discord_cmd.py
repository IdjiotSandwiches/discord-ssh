from discord.ext import commands
import paramiko
import discord
import re
import os
import asyncio
from output import *

PRIVATE_RSA_KEY_PATH = os.path.expanduser(os.getenv("PRIVATE_RSA_KEY_PATH"))
SSH_HOST = os.getenv("SSH_HOST")
DISCORD_API_TOKEN = os.getenv("DISCORD_API_TOKEN")

active_sessions = {}
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)

@bot.command(name="ssh", help="Initialize SSH session")
async def ssh(ctx, username: str):
    if not username:
        await ctx.send(NOT_USERNAME)
        return

    user_id = ctx.author.id
    if user_id in active_sessions:
        await ctx.send(ACTIVE_SESSIONS)
        return

    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        private_key = paramiko.RSAKey.from_private_key_file(PRIVATE_RSA_KEY_PATH)
        client.connect(hostname=SSH_HOST, username=username, pkey=private_key)

        shell = client.invoke_shell()
        active_sessions[user_id] = (client, shell)

        await ctx.send(f"{AUTHENTICATION_SUCCESS} {username}")
    except Exception as e:
        await ctx.send(f"{AUTHENTICATION_FAILED} {str(e)}")

@bot.command(name="exec", help="Execute command")
async def execute(ctx, *, command: str):
    user_id = ctx.author.id
    if user_id not in active_sessions:
        await ctx.send(f"{NO_SESSIONS}")
        return
    
    _, shell = active_sessions[user_id]
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

    blocked_commands = ["nano", "vim", "vi", "emacs", "less", "more", "man"]

    if any(command.strip().startswith(cmd) for cmd in blocked_commands):
        await ctx.send(f"{INTERACTIVE_CMD_RESTRICTION}")
        return

    try:
        shell.send(command + "\n")
        await asyncio.sleep(1)

        output = shell.recv(4096).decode("utf-8")
        output = ansi_escape.sub('', output)
        chunks = [output[i:i+2000] for i in range(0, len(output), 2000)]

        for chunk in chunks:
            await ctx.send(f"```\n{chunk}\n```")
    except Exception as e:
        await ctx.send(f"{CMD_EXECUTION_FAILED} {str(e)}")

@bot.command(name="exit", help="Terminate SSH session")
async def exit_ssh(ctx):
    user_id = ctx.author.id

    if user_id in active_sessions:
        client, _ = active_sessions.pop(user_id)
        client.close()
        await ctx.send(f"{TERMINATE_SESSION}")
    else:
        await ctx.send(f"{NO_SESSIONS}")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(name="Waiting for command."))

bot.run(DISCORD_API_TOKEN)