def usage():
    print("Usage")

def check(data, indentifier):
    return True

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
            configuration_list['nick'][0] = str.encode(tmp, 'utf-8')
            configuration_list['nick'][1] = True


    if not configuration_list['realname'][1]:
        configuration_list['realname'][0] = configuration_list['nick'][0]
        configuration_list['realname'][1] = True


    while not configuration_list['channel'][1]:
        tmp = input("channel: ")

        if check(tmp, 'channel'):
            configuration_list['channel'][0] = str.encode(tmp, 'utf-8')
            configuration_list['channel'][1] = True


    configuration_list['tellfile'][1] = True
