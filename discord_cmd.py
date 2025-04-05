from discord.ext import commands
import paramiko, discord, os
from output import *
from tmux_cmd import *
from util import validate_cmd, ansi_escape, tmux_new, tmux_send, tmux_list, tmux_kill

PRIVATE_RSA_KEY_PATH = os.path.expanduser(os.getenv("PRIVATE_RSA_KEY_PATH"))
SSH_HOST = os.getenv("SSH_HOST")
DISCORD_API_TOKEN = os.getenv("DISCORD_API_TOKEN")

active_sessions = []
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

        # shell = client.invoke_shell()
        session_name = "New session"
        result = tmux_new(session_name=session_name)
        await ctx.send(result.stderr or f"Session '{session_name}' created.")

        active_sessions.append((client, session_name))

        await ctx.send(f"{AUTHENTICATION_SUCCESS} {username}")
    except Exception as e:
        await ctx.send(f"{AUTHENTICATION_FAILED}: {str(e)}")

# @bot.command(name="exec", help="Execute command")
# async def execute(ctx, *, command: str):
#     user_id = ctx.author.id
#     if user_id not in active_sessions:
#         await ctx.send(f"{NO_SESSIONS}")
#         return
    
#     _, shell = active_sessions[user_id]
#     is_valid_cmd, msg = validate_cmd(command)
#     if not is_valid_cmd:
#         await ctx.send(msg)
#         return

#     try:
#         shell.send(command + "\n")
#         await asyncio.sleep(1)

#         output = shell.recv(4096).decode("utf-8")
#         output = ansi_escape(output)
#         chunks = [output[i:i+2000] for i in range(0, len(output), 2000)]

#         for chunk in chunks:
#             await ctx.send(f"```\n{chunk}\n```")
#     except Exception as e:
#         await ctx.send(f"{CMD_EXECUTION_FAILED} {str(e)}")

@bot.command(name="exit", help="Terminate SSH session")
async def exit_ssh(ctx):
    user_id = ctx.author.id

    if user_id in active_sessions:
        client, _ = active_sessions.pop(user_id)
        client.close()
        await ctx.send(f"{TERMINATE_SESSION}")
    else:
        await ctx.send(f"{NO_SESSIONS}")

@bot.command(name="tmux", help="Generate multiple sessions")
async def tmux(ctx, tmux_cmd: str, session_name: str, *, command: str):
    if tmux_cmd == TMUX_NEW:
        result = tmux_new(session_name=session_name)
        await ctx.send(result.stderr or f"Session '{session_name}' created.")
    elif tmux_cmd == TMUX_SEND:
        result = tmux_send(session_name=session_name, command=command)
        await ctx.send(result.stderr or f"Command sent to '{session_name}': {command}")
    elif tmux_cmd == TMUX_LIST:
        is_valid, result = tmux_list()
        if not is_valid:
            await ctx.send(result)
        else:
            await ctx.send(f"Active Sessions:\n```\n{result.stdout}```" if result.stdout else "No active sessions.")
    elif tmux_cmd == TMUX_KILL:
        result = tmux_kill(session_name=session_name)
        await ctx.send(result.stderr or f"Session '{session_name}' terminated.")
    else:
        await ctx.send(f"{INVALID_CMD}: {tmux_cmd}")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(name="Waiting for command."))

if __name__ == '__main__':
    bot.run(DISCORD_API_TOKEN)