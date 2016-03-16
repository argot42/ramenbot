import re, datetime

from rutils import __version__, symbol_map
from chopsticks import Chopsticks

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
                chop = Chopsticks(parser_info['tellfile'])
                chop.userub( ((matched.group('sender_nick'),datetime.datetime.timestamp(datetime.datetime.utcnow())),) )


            elif matched.group('irc_command') == 'PRIVMSG':
                return Ramen.resolv_com(parser_info, matched.group('sender_nick'), matched.group('receiver'), matched.group('msg_body'))


        # list of users in the channel
        matched = re.match(r'.+ = %s :%s((?: (?:(?:%%|~|&|@|\+)\w+|\w+))*)' % (parser_info['channel'], parser_info['nick']), msg_content)
        if matched:

            # .translate(symbol_map) removes nickname symbols
            # .split(' ') separates users into a list
            users = matched.group(1)[1:].translate(symbol_map).split(' ')
            Ramen.log_join(parser_info, users) 


    def pong(pong_string):
        return [b'PONG %b\r\n' % (str.encode(pong_string, 'utf-8'))]


    def join(channel):
        return [b'JOIN %b\r\n' % (str.encode(channel, 'utf-8'))]


    def resolv_com(info, nick, receiver, com):
        # obtain command name
        print("COM->",com)
        matched = re.match(r'\.(?P<com_id>\w+)(?P<args>(?: (?:\S+))*)', com)

        # if it dosn't match a command check for stored msgs
        # yeah this is fucking messy but fuck you i'm tired
        if not matched:
            return Ramen.read_msgs(info, nick, receiver)

        # check if the msg is priv or pub
        # if priv change receiver
        if receiver[0] != '#':
            receiver = nick

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

        elif comid == 'int':
            return Ramen.inte(receiver, args)
       
        else:
            return None


    def help(info, nick, receiver, args):
        if not args[0]:
            return [b'PRIVMSG %b :List of Commands:\r\n' % (str.encode(receiver, 'utf-8')),\
                    b'PRIVMSG %b :- help\r\n' % (str.encode(receiver, 'utf-8')),\
                    b'PRIVMSG %b :- lastseen\r\n' % (str.encode(receiver, 'utf-8')),\
                    b'PRIVMSG %b :- tell\r\n' % (str.encode(receiver, 'utf-8')),\
                    b'PRIVMSG %b :- source\r\n' % (str.encode(receiver, 'utf-8')),\
                    b'PRIVMSG %b :- int\r\n' % (str.encode(receiver, 'utf-8')),\
                    b'PRIVMSG %b :Try .help <command_name> to check command\'s syntax\r\n' % (str.encode(receiver, 'utf-8'))]

        elif args[0] == 'help':
            return [b'PRIVMSG %b :.help [command]: shows command sintax or, without arguments, the list of commands.\r\n' % (str.encode(receiver, 'utf-8'))]

        elif args[0] == 'lastseen':
            return [b'PRIVMSG %b :.lastseen <user>: shows timestamp of a user\'s last connection.\r\n' % (str.encode(receiver, 'utf-8'))]

        elif args[0] == 'tell':
            return [b'PRIVMSG %b :.tell <user>: leave a message for a disconnected user. he\'ll receive it when he writes again on the channel.\r\n' % (str.encode(receiver, 'utf-8'))]

        elif args[0] == 'source':
            return [b'PRIVMSG %b :.source: ramenbot is libre baby.\r\n' % (str.encode(receiver, 'utf-8'))]

        elif args[0] == 'int':
            return [b'PRIVMSG %b :.int <somthing>: Intesifies something.\r\n' % (str.encode(receiver, 'utf-8'))]


    def source(info, nick, receiver):
        return [b'PRIVMSG %b :ramenbot v%b [https://github.com/argot42/ramenbot.git]\r\n' % (str.encode(receiver, 'utf-8'), str.encode(__version__, 'utf-8'))]


    def tell(info, nick, receiver, args):
        if not args[0]:
            return [b'PRIVMSG %b :Try .help tell.\r\n' % (str.encode(receiver, 'utf-8'))]
        elif len(args) < 1:
            return [b'PRIVMSG %b :The msg need a body.\r\n' % (str.encode(receiver, 'utf-8'))]

        chop = Chopsticks(info['tellfile'])

        try:
            if receiver[0] != '#':
                chop.storemsg(nick, args[0], args[1:], 1)

            else:
                chop.storemsg(nick, args[0], args[1:], 0)


        except:
            return [b'PRIVMSG %b :For some reason the message couldn\'t be stored, sorry :c\r\n' % (str.encode(receiver, 'utf-8'))]

        else:
            return [b'PRIVMSG %b :The msg will be delivered :)\r\n' % (str.encode(receiver, 'utf-8'))]

    def lastseen(info, nick, receiver, args):
        if not args[0]:
            return [b'PRIVMSG %b :Baka, this command needs a valid nick as argument.\r\n' % (str.encode(receiver, 'utf-8'))]

        chop = Chopsticks(info['tellfile'])

        # retrieves user lastseen timestamp from database
        # and converts it into a datetime obj
        timestamp = chop.user_rts(args[0])

        if not timestamp:
            return [b'PRIVMSG %b :That person didn\'t connect while I was around\r\n' % (str.encode(receiver, 'utf-8'))]

        date = datetime.datetime.fromtimestamp(timestamp)

        return [b'PRIVMSG %b :%b was last seen %b utc\r\n' % (str.encode(receiver, 'utf-8'), str.encode(args[0], 'utf-8'), str.encode(date.strftime('on %Y-%m-%d at %H:%M:%S'), 'utf-8'))]


    def inte(receiver, args):
        if not args[0]:
            return [b'PRIVMSG %b :Needs argument to intensify\r\n' % (str.encode(receiver, 'utf-8'))]

        return [b'PRIVMSG %b :[%b INTENSIFIES]\r\n' % (str.encode(receiver, 'utf-8'), str.encode(' '.join(args).upper(), 'utf-8'))]


    def log_join(info, users):
        chop = Chopsticks(info['tellfile'])
        
        timest = datetime.datetime.timestamp(datetime.datetime.utcnow())
        usr_tupl = tuple()
        for user in users:
            usr_tupl += ((user, timest),)

        chop.userub(usr_tupl) 


    def read_msgs(info, nick, receiver):
        chop = Chopsticks(info['tellfile'])
        msgs = chop.retrievemsg(nick)

        pack = []
        for msg in msgs:
            if not msg[2]:
                sendto = receiver
            else: 
                sendto = nick

            pack.append(b'PRIVMSG %b :%b left this msg for %b: %b\r\n' % (str.encode(sendto, 'utf-8'), str.encode(msg[0], 'utf-8'), str.encode(nick, 'utf-8'), str.encode(msg[1], 'utf-8')))


        return pack
