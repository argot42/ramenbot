import re, os

__version__ = "1.0"

symbol_map = {ord('@'): None, ord('!'): None, ord('%'): None, ord('~'): None, ord('&'): None, ord('+'): None}

class fm:
    un = '\033[4m'
    b = '\033[1m'
    end = '\033[0m'

def usage():
    print("ramenbot - Love-filled, handcrafted, bad-coded, python irc bot ❤\n")
    print("%sUsage:%s" % (fm.un, fm.end))
    print("ramenbot [options]\n")
    print("%sOptions:%s" % (fm.un, fm.end))
    print("%s -h, --help%s\t\t\t\tThis help." % (fm.b, fm.end))
    print("%s -v, --version%s\t\t\t\tDisplays bot version." % (fm.b, fm.end))
    print("%s -f path, --config=path%s\t\t\tConfig file location. (default ~/.ramenbot/ramenrc)" % (fm.b, fm.end))
    print("%s -H address, --host=address%s\t\tAddress of the irc server" % (fm.b, fm.end))
    print("%s -p port, --port=port%s\t\t\tPort number of the irc server" % (fm.b, fm.end))
    print("%s -n nickname, --nick=nickname%s\t\tramenbot nickname" % (fm.b, fm.end))
    print("%s -r realname, --realname=realname%s\tramenbot realname (default nickname)" % (fm.b, fm.end))
    print("%s -c channel, --channel=channel%s\t\tChannel ramenbot will join" % (fm.b, fm.end))
    print("%s -s, --ssl%s\t\t\t\tramenbot will use a secure connection" % (fm.b, fm.end))
    print("%s -t path, --tellfile=path%s\t\tSQLite db from where .tell command will pull and write\n\t\t\t\t\tthe user msgs" % (fm.b, fm.end))


def check_host(data):
    if type(data) != str:
        return False

    matched = re.match(r'^(?:[\w,-]+\.)+\w+$', data)
    if matched:
        return True
    else:
        return False


def check_nick(data):
    if type(data) != str:
        return False

    matched = re.match(r'^[\w,-]+$', data)
    if matched:
        return True
    else:
        return False


def check_port(data):
    try:
        int(data)
    except ValueError:
        return False
    else:
        return True


def check_path(data):
    return os.path.exists(data)   


def check_chan(data):
    if type(data) != str:
        return False

    matched = re.match(r'^#[\w,-]+$', data)
    if matched:
        return True
    else:
        return False


def check(data, indentifier):
    if indentifier == 'host':
        return check_host(data)
    elif indentifier == 'port':
        return check_port(data)
    elif indentifier in ['nick', 'realname']:
        return check_nick(data)
    elif indentifier == 'channel':
        return check_chan(data)
    elif indentifier == 'tellfile':
        return check_path(data)


def complete_missing(configuration_list):
    while not configuration_list['host'][1]:
        tmp = input("host: ")

        if check(tmp, 'host'):
            configuration_list['host'][0] = tmp
            configuration_list['host'][1] = True


    while not configuration_list['port'][1]:
        tmp = input("port: ")

        if check(tmp, 'port'):
            configuration_list['port'][0] = int(tmp)
            configuration_list['port'][1] = True


    while not configuration_list['nick'][1]:
        tmp = input("nick: ")

        if check(tmp, 'nick'):
            configuration_list['nick'][0] = tmp
            configuration_list['nick'][1] = True


    if not configuration_list['realname'][1]:
        configuration_list['realname'][0] = configuration_list['nick'][0]
        configuration_list['realname'][1] = True


    while not configuration_list['channel'][1]:
        tmp = input("channel: ")

        if check(tmp, 'channel'):
            configuration_list['channel'][0] = tmp
            configuration_list['channel'][1] = True


    # Configuration not mandatory
    configuration_list['tellfile'][1] = True
    configuration_list['ssl'][1] = True
