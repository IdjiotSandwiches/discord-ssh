from output import INTERACTIVE_CMD_RESTRICTION, ROOT_CMD_RESTRICTION

def check_cmd(command):
    restricted_interactive_cmd = ["nano", "vim", "vi", "emacs", "less", "more", "man"]
    restricted_root_cmd = ["sudo", "rm"]
    allowed_cmd = []

    if any(command.strip().startswith(cmd) for cmd in restricted_interactive_cmd):
        return False
    elif any(command.strip().startswith(cmd) for cmd in restricted_root_cmd):
        return False