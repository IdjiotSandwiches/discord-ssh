NOT_AUTH = "You need insert username and key. Use /help for more details."
NOT_COMMAND = "Use /help to use the command."
WRONG_KEY = "Wrong key. Hint: Strike Witches."

ACTIVE_SESSIONS = "You already have an active SSH session!"
NO_SESSIONS = "No active SSH session. Use `/ssh` to start one."
TERMINATE_SESSION = "SSH session terminated."

AUTHENTICATION_SUCCESS = "SSH session started as"
AUTHENTICATION_FAILED = "SSH connection failed"

INTERACTIVE_CMD_RESTRICTION = "This command requires interactive input."
ROOT_CMD_RESTRICTION = "This command requires root privilage."

CMD_EXECUTION_FAILED = "Error executing command:"
INVALID_CMD = "Invalid command."

DELETE_RESTRICTION = "This command is for Server only."
DELETE_INVALID = "Failed to delete message"

HELP = """--| List of command |--
- /ssh [username] [key]: connect to SSH connection using username and key
- /tmux new [session_name]: create new session
- /tmux send [session_name] [command]: send & execute command to given session
- /tmux list: show all active session
- /tmux kill [session_name]: end given session
- /help: show list of commands
- /exit: close SSH connection"""