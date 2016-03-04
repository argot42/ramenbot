import sys
import getopt
from os.path import expanduser

from bowl import Bowl
from rutils import usage, check, complete_missing, __version__

try:
    opts, args = getopt.getopt(sys.argv[1:], "hvf:H:p:n:r:c:t:", ["help", "version", "config=", "host=", "port=", "nick=", "realname=", "channel=", "tellfile="])

except getopt.GetoptError as err:
    usage()
    print(err)
    sys.argv(2)

# where configuration will be located
config_file_path = '~/.ramenbot/ramenrc'
# bot configuration dictionary <config_name>: [<value>, <command_line_flag>]
bot_configuration = \
    {'host': [str(), False],
        'port': [int(), False],
        'nick': [b'', False],
        'realname': [b'', False],
        'channel': [b'', False],
        'tellfile': ['~/.ramenbot/tellfile.db', False]
    }

for option, argument in opts:
    if option in ("-h", "--help"):
        usage()
        sys.exit()

    elif option in ("-v", "--version"):
        print("sushibot", __version__)
        sys.exit()
    
    elif option in ("-f", "--config"):
        config_file_path = argument

    elif option in ("-H", "--host"):
        if check(bot_configuration["host"], "host"):
            bot_configuration["host"][0] = argument
            bot_configuration["host"][1] = True

    elif option in ("-p", "--port"):
        if check(bot_configuration["port"], "port"):
            bot_configuration["port"][0] = int(argument)
            bot_configuration["port"][1] = True

    elif option in ("-n", "--nick"):
        if check(bot_configuration["nick"], "nick"):
            bot_configuration["nick"][0] = str.encode(argument, 'utf-8')
            bot_configuration["nick"][1] = True

    elif option in ("-r", "--realname"):
        if check(bot_configuration["realname"], "realname"):
            bot_configuration["realname"][0] = str.encode(argument, 'utf-8')
            bot_configuration["realname"][1] = True

    elif option in ("-c", "--channel"):
        if check(bot_configuration["channel"], "channel"):
            bot_configuration["channel"][0] = str.encode(argument, 'utf-8')
            bot_configuration["channel"][1] = True

    elif option in ("-t", "--tellfile"):
        if check(bot_configuration["tellfile"], "tellfile"):
            bot_configuration["tellfile"][0] = argument + '/tellfile.db'
            bot_configuration["tellfile"][1] = True

    
# reading config file
try:
    fd = open(expanduser(config_file_path), 'r')

except FileNotFoundError as err:
    print("Configuration file not found")

else:
    for line in fd:
        parts = str.strip(line).split(': ')
        
        if parts[0] == 'nick':
            if not bot_configuration["nick"][1] and check(parts[1], "nick"): 
                bot_configuration["nick"][0] = str.encode(parts[1], 'utf-8')
                bot_configuration["nick"][1] = True

        elif parts[0] == 'realname':
            if not bot_configuration["realname"][1] and check(parts[1], "realname"): 
                bot_configuration["realname"][0] = str.encode(parts[1], 'utf-8')
                bot_configuration["realname"][1] = True

        elif parts[0] == 'host':
            if not bot_configuration["host"][1] and check(parts[1], "host"):
                bot_configuration["host"][0] = parts[1]
                bot_configuration["host"][1] = True

        elif parts[0] == 'port':
            if not bot_configuration["port"][1] and check(parts[1], "port"): 
                bot_configuration["port"][0] = int(parts[1])
                bot_configuration["port"][1] = True

        elif parts[0] == 'channel':
            if not bot_configuration["channel"][1] and check(parts[1], "channel"): 
                bot_configuration["channel"][0] = str.encode(parts[1], 'utf-8')
                bot_configuration["channel"][1] = True

        elif parts[0] == 'tellfile':
            if not bot_configuration["tellfile"][1] and check(parts[1], "tellfile"): 
                bot_configuration["tellfile"][0] = parts[1] + '/tellfile.db'
                bot_configuration["tellfile"][1] = True


# Complete mandatory config info
complete_missing(bot_configuration)
print(bot_configuration)

bowl = Bowl(bot_configuration["host"][0], bot_configuration["port"][0], bot_configuration["nick"][0],\
        bot_configuration["realname"][0], bot_configuration["channel"][0], bot_configuration["tellfile"][0])

try:
    bowl.connect()

except:
    raise
