from output import INTERACTIVE_CMD_RESTRICTION, ROOT_CMD_RESTRICTION
import re, subprocess

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
    
def ansi_escape(output: str):
    ansi_escape_pattern = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape_pattern.sub('', output)

def tmux_new(session_name: str):
    return subprocess.run(['tmux', 'new-session', '-d', '-s', session_name], capture_output=True, text=True)

def tmux_send(session_name: str, command: str):
    is_valid, msg = validate_cmd(command=command)
    if not is_valid:
        return is_valid, msg
    
    return is_valid, subprocess.run(['tmux', 'send-keys', '-t', session_name, command, 'C-m'], capture_output=True, text=True)

def tmux_list():
    return subprocess.run(['tmux', 'ls'], capture_output=True, text=True)

def tmux_kill(session_name: str):
    return subprocess.run(['tmux', 'kill-session', '-t', session_name], capture_output=True, text=True)