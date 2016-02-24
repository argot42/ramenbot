import re

__version__ = "0.1"

class Ramen:
    def parse(msg_content, parser_info):
        msg_content = str.rstrip(msg_content)
        msg_splited = str.split(msg_content) 

        if not msg_splited:
            return None

        if msg_splited[0] == "PING":
            return Ramen.pong(msg_splited[1])

        elif msg_splited[0] == (":%s" % parser_info['nick']):
            return Ramen.join(parser_info['channel'])

        elif len(msg_splited) > 3:
            # obtain sender nickname
            matched = re.match(':(?P<sender_nick>\w+)!', msg_splited[0])
            if not matched:
                return None
            parser_info['sender_nick'] = matched.group('sender_nick')

            # receiver be user or channel
            parser_info['receiver'] = msg_splited[2]

            # check msg type
            if msg_splited[1] == "JOIN":
                Ramen.log_join(info)
                return None

            elif msg_splited[1] == "PRIVMSG":
                # check if msg is a command or not
                if msg_splited[3][0:2] == ':.':
                    return Ramen.resolv_com(parser_info, msg_splited[3:])
                else:
                    return None
                    #Ramen.tell_check(info)


    def pong(pong_string):
        return [b'PONG %b\r\n' % (str.encode(pong_string, 'utf-8'))]


    def join(channel):
        return [b'JOIN %b\r\n' % (str.encode(channel, 'utf-8'))]


    def resolv_com(info, com):
        # obtain command name
        matched = re.match(r':\.(?P<com_id>\w+)', com[0])
        if not matched:
            return None
        comid = matched.group('com_id')

        # check command and respond adequately
        if comid == 'help':
            return Ramen.help(info, com[1:])

        elif comid == 'tell':
            return Ramen.tell(info, com[1:])

        elif comid == 'lastseen':
            return Ramen.lastseen(info, com[1:])

        elif comid == 'source':
            return Ramen.source(info)

        else:
            return None


    def help(info, args):
        if not args:
            return [b'PRIVMSG %b List of Commands:\r\n' % (str.encode(info['channel'], 'utf-8')),\
                    b'PRIVMSG %b - help\r\n' % (str.encode(info['channel'], 'utf-8')),\
                    b'PRIVMSG %b - lastseen\r\n' % (str.encode(info['channel'], 'utf-8')),\
                    b'PRIVMSG %b - tell\r\n' % (str.encode(info['channel'], 'utf-8')),\
                    b'PRIVMSG %b - source\r\n' % (str.encode(info['channel'], 'utf-8')),\
                    b'PRIVMSG %b Try .help <command_name> to check command\'s syntax\r\n' % (str.encode(info['channel'], 'utf-8'))]

        elif args[0] == 'help':
            return [b'PRIVMSG %b .help [command]: shows command sintax or, without arguments, the list of commands\r\n' % (str.encode(info['channel'], 'utf-8'))]

        elif args[0] == 'lastseen':
            return [b'PRIVMSG %b .lastseen <user>: shows timestamp of a user\'s last connection\r\n' % (str.encode(info['channel'], 'utf-8'))]

        elif args[0] == 'tell':
            return [b'PRIVMSG %b .tell <user>: leave a message for a disconnected user. he\'ll receive it when he writes again on the channel\r\n' % (str.encode(info['channel'], 'utf-8'))]

        elif args[0] == 'source':
            return [b'PRIVMSG %b .source: ramenbot is libre baby\r\n' % (str.encode(info['channel'], 'utf-8'))]


    def source(info):
        return [b'PRIVMSG %b ramenbot v%b [https://github.com/argot42/ramenbot.git]\r\n' % (str.encode(info['sender_nick'], 'utf-8'), str.encode(__version__, 'utf-8'))]


    def tell(info, args):
        return None


    def lastseen(info, args):
        return None


    def log_join(info):
                
