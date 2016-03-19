import re, datetime, urllib.request, json

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
        return [b'PONG %b\r\n' % (pong_string.encode('utf-8'))]


    def join(channel):
        return [b'JOIN %b\r\n' % (channel.encode('utf-8'))]


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

        elif comid == 'src':
            return Ramen.source(info, nick, receiver)

        elif comid == 'int':
            return Ramen.inte(receiver, args)
       
        elif comid == 'w':
            return Ramen.weather(receiver, args)

        elif comid == 'wiki':
            return Ramen.wiki(receiver, args)

        else:
            return None


    def help(info, nick, receiver, args):
        if not args[0]:
            return [b'PRIVMSG %b :List of Commands:\r\n' % (receiver.encode('utf-8')),\
                    b'PRIVMSG %b :- help\r\n' % (receiver.encode('utf-8')),\
                    b'PRIVMSG %b :- lastseen\r\n' % (receiver.encode('utf-8')),\
                    b'PRIVMSG %b :- tell\r\n' % (receiver.encode('utf-8')),\
                    b'PRIVMSG %b :- src\r\n' % (receiver.encode('utf-8')),\
                    b'PRIVMSG %b :- int\r\n' % (receiver.encode('utf-8')),\
                    b'PRIVMSG %b :- w\r\n' % (receiver.encode('utf-8')),\
                    b'PRIVMSG %b :- wiki\r\n' % (receiver.encode('utf-8')),\
                    b'PRIVMSG %b :Try .help <command_name> to check command\'s syntax\r\n' % (receiver.encode('utf-8'))]

        elif args[0] == 'help':
            return [b'PRIVMSG %b :.help [command]: shows command sintax or, without arguments, the list of commands.\r\n' % (receiver.encode('utf-8'))]

        elif args[0] == 'lastseen':
            return [b'PRIVMSG %b :.lastseen <user>: shows timestamp of a user\'s last connection.\r\n' % (receiver.encode('utf-8'))]

        elif args[0] == 'tell':
            return [b'PRIVMSG %b :.tell <user>: leave a message for a disconnected user. he\'ll receive it when he writes again on the channel.\r\n' % (receiver.encode('utf-8'))]

        elif args[0] == 'src':
            return [b'PRIVMSG %b :.src: ramenbot is libre baby.\r\n' % (receiver.encode('utf-8'))]

        elif args[0] == 'int':
            return [b'PRIVMSG %b :.int <somthing>: Intesifies something.\r\n' % (receiver.encode('utf-8'))]

        elif args[0] == 'w':
            return [b'PRIVMSG %b :.w <city>, <region>, [<country>], [<unit>]: Tells you the climate in that region\r\n' % (receiver.encode('utf-8'))]

        elif args[0] == 'wiki':
            return [b'PRIVMSG %b :.wiki <something>: Looks something up in wikipedia\r\n' % (receiver.encode('utf-8'))]


    def source(info, nick, receiver):
        return [b'PRIVMSG %b :ramenbot v%b [https://github.com/argot42/ramenbot.git]\r\n' % (receiver.encode('utf-8'), __version__.encode('utf-8'))]


    def tell(info, nick, receiver, args):
        if not args[0]:
            return [b'PRIVMSG %b :Try .help tell.\r\n' % (receiver.encode('utf-8'))]
        elif len(args) < 1:
            return [b'PRIVMSG %b :The msg need a body.\r\n' % (receiver.encode('utf-8'))]

        chop = Chopsticks(info['tellfile'])

        try:
            if receiver[0] != '#':
                chop.storemsg(nick, args[0], args[1:], 1)

            else:
                chop.storemsg(nick, args[0], args[1:], 0)


        except:
            return [b'PRIVMSG %b :For some reason the message couldn\'t be stored, sorry :c\r\n' % (receiver.encode('utf-8'))]

        else:
            return [b'PRIVMSG %b :The msg will be delivered :)\r\n' % (receiver.encode('utf-8'))]

    def lastseen(info, nick, receiver, args):
        if not args[0]:
            return [b'PRIVMSG %b :Baka, this command needs a valid nick as argument.\r\n' % (receiver.encode('utf-8'))]

        chop = Chopsticks(info['tellfile'])

        # retrieves user lastseen timestamp from database
        # and converts it into a datetime obj
        timestamp = chop.user_rts(args[0])

        if not timestamp:
            return [b'PRIVMSG %b :That person didn\'t connect while I was around\r\n' % (receiver.encode('utf-8'))]

        date = datetime.datetime.fromtimestamp(timestamp)

        return [b'PRIVMSG %b :%b was last seen %b utc\r\n' % (receiver.encode('utf-8'), args[0].encode('utf-8'), date.strftime('on %Y-%m-%d at %H:%M:%S').encode('utf-8'))]


    def inte(receiver, args):
        if not args[0]:
            return [b'PRIVMSG %b :Needs argument to intensify\r\n' % (receiver.encode('utf-8'))]

        return [b'PRIVMSG %b :[%b INTENSIFIES]\r\n' % (receiver.encode('utf-8'), ' '.join(args).upper().encode('utf-8'))]


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

            pack.append(b'PRIVMSG %b :%b left this msg for %b: %b\r\n' % (sendto.encode('utf-8'), msg[0].encode('utf-8'), nick.encode('utf-8'), msg[1].encode('utf-8')))


        return pack


    def weather(receiver, args):
        try:
            url = Ramen.parse_weather(args)
        except RuntimeError as err:
            return [b'PRIVMSG %b :%b\r\n' % (receiver.encode('utf-8'), err.args[1].encode('utf-8'))]
            
        with urllib.request.urlopen(url) as response:
            res_obj = json.loads(response.read().decode('utf-8'))

        # place info
        place = res_obj['query']['results']['channel']['location']
        # todays weather
        wea = res_obj['query']['results']['channel']['item']['forecast'][0]

        return [b'PRIVMSG %b :Current conditions in %b, %b, %b - %b High: %b Low: %b\r\n'\
                % (receiver.encode('utf-8'),\
                    place['city'].encode('utf-8'), place['region'].encode('utf-8'), place['country'].encode('utf-8'),\
                    wea['text'].encode('utf-8'), wea['high'].encode('utf-8'), wea['low'].encode('utf-8'))] 


    def parse_weather(args):
        if not args[0]:
            raise RuntimeError('no_arguments', 'You must provide arguments for this command')

        # [[city], [region], [country]*, [unit]*]
        # * = not mandatory
        info = [[], [], [], 'c'] 
        count = 0

        for value in args:
            if value[0] == ':':
                if value == ':c' or ':f':
                    info[-1] = value[1] 
                continue

            info[count].append(value)

            if value[-1] == ',':
                count+=1

        if not info[0] or not info[1]:
            raise RuntimeError('city_region', 'You must provide at least a city and a region or country')

        map_table = {ord(','):'', ord(' '):'%20'}

        city = ' '.join(info[0]).translate(map_table)
        region = '%2C%20' + ' '.join(info[1]).translate(map_table)

        if not info[2]:
            country = ''
        else:
            country = '%2C%20' + ' '.join(info[2]).translate(map_table)

        unit = info[3]

        base_url = 'https://query.yahooapis.com/v1/public/'
        query_url = 'yql?q=select%20*%20from%20weather.forecast%20where%20woeid%20in%20(select%20woeid%20from%20geo.places(1)%20where%20text%3D%22{city}{region}{country}%22)%20and%20u%3D%22{unit}%22&format=json'.format(city=city, region=region, country=country, unit=unit)

        return base_url + query_url


    def wiki(receiver, args):
        if not args[0]:
            return [b'PRIVMSG %b :This commands needs at least one argument\r\n' % (receiver.encode('utf-8'))]

        # set up search
        search = '+'.join(args)
        url = 'https://en.wikipedia.org/w/api.php?action=query&format=json&prop=info&titles={title}&inprop=url'.format(title=search)
        user_agent = 'mozilla/5.0 (x11; linux x86_64; rv:38.9)'
        headers = {'user-agent':user_agent}

        req = urllib.request.Request(url, None, headers)
        with urllib.request.urlopen(req) as response:
            obj_res = json.loads(response.read().decode('utf-8'))

        item = obj_res['query']['pages'].popitem()
        if item[0] == '-1':
            return [b'PRIVMSG %b :No article found\r\n' % (receiver.encode('utf-8'))]

        else:
            return [b'PRIVMSG %b :%b\r\n' % (receiver.encode('utf-8'), item[1]['canonicalurl'].encode('utf-8'))]
