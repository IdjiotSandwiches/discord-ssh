from discord.ext import commands
import paramiko, discord, os
from output import *
from tmux_cmd import *
from util import tmux_new, tmux_send, tmux_list, tmux_kill, show_help, delete_user_message
from dotenv import load_dotenv

load_dotenv()

PRIVATE_RSA_KEY_PATH = os.path.expanduser(os.getenv("PRIVATE_RSA_KEY_PATH"))
SSH_HOST = os.getenv("SSH_HOST")
DISCORD_API_TOKEN = os.getenv("DISCORD_API_TOKEN")
KEY = os.getenv("KEY")

active_sessions = {}
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="/", intents=intents)
bot.remove_command("help")

@bot.command(name="ssh", help="Initialize SSH session")
async def ssh(ctx, username: str = None, key: str = None):
    await delete_user_message(ctx)

    if not username or not key:
        await ctx.send(f"```\n{NOT_AUTH}```")
        return
    
    user_id = ctx.author.id
    if user_id in active_sessions:
        await ctx.send(f"```\n{ACTIVE_SESSIONS}```")
        return

    try:
        if key != KEY:
            raise ValueError(WRONG_KEY)
        
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        private_key = paramiko.RSAKey.from_private_key_file(PRIVATE_RSA_KEY_PATH)
        client.connect(hostname=SSH_HOST, username=username, pkey=private_key)
        active_sessions[user_id] = client

        await ctx.send(f"```\n{AUTHENTICATION_SUCCESS} {username}```")
    except Exception as e:
        await ctx.send(f"```\n{AUTHENTICATION_FAILED}: {str(e)}```")

@bot.command(name="exit", help="Terminate SSH session")
async def exit_ssh(ctx):
    await delete_user_message(ctx)

    user_id = ctx.author.id
    if user_id in active_sessions:
        client = active_sessions.pop(user_id)
        client.close()
        await ctx.send(f"```\n{TERMINATE_SESSION}```")
    else:
        await ctx.send(f"```\n{NO_SESSIONS}```")

@bot.command(name="tmux", help="Generate multiple sessions")
async def tmux(ctx, tmux_cmd: str = None, session_name: str = None, *, command: str = None):
    await delete_user_message(ctx)

    if not tmux_cmd or not session_name or not command:
        await ctx.send(f"```\n{NOT_COMMAND}```")
        return

    user_id = ctx.author.id
    if user_id not in active_sessions:
        await ctx.send(f"```\n{NO_SESSIONS}```")
    else:
        try:
            if tmux_cmd == TMUX_NEW:
                result = tmux_new(session_name=session_name)
                await ctx.send(result.stderr or f"```Session '{session_name}' created.```")
            elif tmux_cmd == TMUX_SEND:
                result = tmux_send(session_name=session_name, command=command)
                for chunk in result:
                    await ctx.send(f"```\n{chunk}```")
            elif tmux_cmd == TMUX_LIST:
                result = tmux_list()
                await ctx.send(f"Active Sessions:\n```\n{result.stdout}```" if result.stdout else "```\nNo active sessions.```")
            elif tmux_cmd == TMUX_KILL:
                result = tmux_kill(session_name=session_name)
                await ctx.send(result.stderr or f"```\nSession '{session_name}' terminated.```")
            else:
                await ctx.send(f"```\n{INVALID_CMD}: {tmux_cmd}```")
        except Exception as e:
            await ctx.send(f"```\n{CMD_EXECUTION_FAILED} {str(e)}```")

@bot.command(name="help", help="Command guide")
async def help(ctx):
    await delete_user_message(ctx)
    await ctx.send(f"```\n{show_help()}```")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(name="TuGil on your command."))

if __name__ == '__main__':
    bot.run(DISCORD_API_TOKEN)