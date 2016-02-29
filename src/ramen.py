import re

__version__ = "0.1"

class Ramen:
    def parse(msg_content, parser_info):
        print(msg_content)

        # bot pings server
        matched = re.match(r'PING (?P<ping_id>:\w+)', msg_content)
        if matched:
            return Ramen.pong(matched.group('ping_id'))

        # bot joins channel
        matched = re.match(r'^:%s' % parser_info['nick'], msg_content)
        if matched:
            return Ramen.join(parser_info['channel'])

        # bot reads msgs
        matched = re.match(r'^:(?P<sender_nick>\w+)!\S+ (?P<irc_command>\w+)(?: (?P<receiver>#\w+|\w+))* :(?P<msg_body>.+)$', msg_content)
        if matched:
            if matched.group('irc_command') == 'JOIN':
                print('%s -> JOINED -> %s' % (matched.group('sender_nick'), matched.group('msg_body')))

            elif matched.group('irc_command') == 'PRIVMSG':
                return Ramen.resolv_com(parser_info, matched.group('sender_nick'), matched.group('receiver'), matched.group('msg_body'))


        # list of users in the channel
        matched = re.match(r'.+ = %s :%s((?: (?:\w+))*)' % (parser_info['channel'], parser_info['nick']), msg_content)
        if matched:
            Ramen.log_join(matched.group(1)[1:].split(' ')) 


    def pong(pong_string):
        return [b'PONG %b\r\n' % (str.encode(pong_string, 'utf-8'))]


    def join(channel):
        return [b'JOIN %b\r\n' % (str.encode(channel, 'utf-8'))]


    def resolv_com(info, nick, receiver, com):
        # obtain command name
        print("COM->",com)
        matched = re.match(r'\.(?P<com_id>\w+)(?P<args>(?: (?:\S+))*)', com)
        if not matched:
            return None

        comid = matched.group('com_id')
        args = matched.group('args')[1:].split(' ')

        # check command and respond adequately
        if comid == 'help':
            return Ramen.help(info, nick, receiver, args)

        elif comid == 'tell':
            return Ramen.tell(info, nick, receiver, args)

        elif comid == 'lastseen':
            return Ramen.lastseen(info, nick, receiver, args)

        elif comid == 'source':
            return Ramen.source(info, nick, receiver)
       
        else:
            return None


    def help(info, nick, receiver, args):
        if not args[0]:
            return [b'PRIVMSG %b :List of Commands:\r\n' % (str.encode(receiver, 'utf-8')),\
                    b'PRIVMSG %b :- help\r\n' % (str.encode(receiver, 'utf-8')),\
                    b'PRIVMSG %b :- lastseen\r\n' % (str.encode(receiver, 'utf-8')),\
                    b'PRIVMSG %b :- tell\r\n' % (str.encode(receiver, 'utf-8')),\
                    b'PRIVMSG %b :- source\r\n' % (str.encode(receiver, 'utf-8')),\
                    b'PRIVMSG %b :Try .help <command_name> to check command\'s syntax\r\n' % (str.encode(receiver, 'utf-8'))]

        elif args[0] == 'help':
            return [b'PRIVMSG %b :.help [command]: shows command sintax or, without arguments, the list of commands\r\n' % (str.encode(receiver, 'utf-8'))]

        elif args[0] == 'lastseen':
            return [b'PRIVMSG %b :.lastseen <user>: shows timestamp of a user\'s last connection\r\n' % (str.encode(receiver, 'utf-8'))]

        elif args[0] == 'tell':
            return [b'PRIVMSG %b :.tell <user>: leave a message for a disconnected user. he\'ll receive it when he writes again on the channel\r\n' % (str.encode(receiver, 'utf-8'))]

        elif args[0] == 'source':
            return [b'PRIVMSG %b :.source: ramenbot is libre baby\r\n' % (str.encode(receiver, 'utf-8'))]


    def source(info, nick, receiver):
        return [b'PRIVMSG %b :ramenbot v%b [https://github.com/argot42/ramenbot.git]\r\n' % (str.encode(receiver, 'utf-8'), str.encode(__version__, 'utf-8'))]


    def tell(info, nick, receiver, args):
        return None


    def lastseen(info, nick, receiver, args):
        return None


    def log_join(info):
        print('USERS ->', info)
