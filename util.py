from output import INTERACTIVE_CMD_RESTRICTION, ROOT_CMD_RESTRICTION
import re, subprocess, time

def validate_cmd(command: str):
    restricted_interactive_cmd = ["nano", "vim", "vi", "emacs", "less", "more", "man"]
    restricted_root_cmd = ["sudo", "rm"]
    allowed_cmd = []

    if any(command.strip().startswith(cmd) for cmd in restricted_interactive_cmd):
        return False, INTERACTIVE_CMD_RESTRICTION
    elif any(command.strip().startswith(cmd) for cmd in restricted_root_cmd):
        return False, ROOT_CMD_RESTRICTION
    else:
        return True, ""
    
def chunk_output(output: str):
    ansi_escape_pattern = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    output = ansi_escape_pattern.sub('', output)

    pattern = r"\b[\w.-]+@[\w.-]+:[^\n]*\$"
    matches = list(re.finditer(pattern, output))

    if matches:
        start_index = matches[-2].start()
        output = output[start_index:]

    return [output[i:i+2000] for i in range(0, len(output), 2000)]

def tmux_new(session_name: str):
    return subprocess.run(['tmux', 'new-session', '-d', '-s', session_name], capture_output=True, text=True)

def tmux_send(session_name: str, command: str):
    is_valid, msg = validate_cmd(command=command)
    if not is_valid:
        return chunk_output(msg)

    subprocess.run(['tmux', 'send-keys', '-t', session_name, command, 'C-m'], capture_output=True, text=True)
    time.sleep(1)

    output = subprocess.run(['tmux', 'capture-pane', '-pt', session_name], capture_output=True, text=True)
    output = output.stdout
    output = chunk_output(output)

    return output

def tmux_list():
    return subprocess.run(['tmux', 'ls'], capture_output=True, text=True)

def tmux_kill(session_name: str):
    return subprocess.run(['tmux', 'kill-session', '-t', session_name], capture_output=True, text=True)

def show_help():
    cmd_help = """--| List of command |--
- /ssh [username] [key]: connect to SSH connection using username and key
- /tmux new [session_name]: create new session
- /tmux send [session_name] [command]: send & execute command to given session
- /tmux list: show all active session
- /tmux kill [session_name]: end given session
- /help: show list of commands
- /exit: close SSH connection"""
    return cmd_help