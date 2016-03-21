import re, datetime, urllib.request, json

from rutils import __version__, symbol_map
from chopsticks import Chopsticks

class Ramen:
    def parse(msg_content, parser_info):
        print(msg_content)

        # bot pings server
        matched = re.match(r'PING :(?P<ping_id>\w+)', msg_content)
        if matched:
            return Ramen.pong(matched.group('ping_id'))

        # bot joins channel
        matched = re.match(r'^:%s' % parser_info['nick'], msg_content)
        if matched:
            return Ramen.join(parser_info['channel'])

        # bot reads msgs
        matched = re.match(r'^:(?P<sender_nick>[\w, -]+)!\S+ (?P<irc_command>\w+)(?: (?P<receiver>[#\w, -]+|[\w, -]+))* :(?P<msg_body>.+)$', msg_content)
        if matched:
            if matched.group('irc_command') == 'JOIN':
                chop = Chopsticks(parser_info['tellfile'])
                chop.userub( ((matched.group('sender_nick'),datetime.datetime.timestamp(datetime.datetime.utcnow())),) )


            elif matched.group('irc_command') == 'PRIVMSG':
                return Ramen.resolv_com(parser_info, matched.group('sender_nick'), matched.group('receiver'), matched.group('msg_body'))


        # list of users in the channel
        matched = re.match(r'.+ = %s :%s((?: (?:[(?:%%|~|&|@|\+)\w, -]+|[\w, -]+))*)' % (parser_info['channel'], parser_info['nick']), msg_content)
        if matched:

            # .translate(symbol_map) removes nickname symbols
            # .split(' ') separates users into a list
            users = matched.group(1)[1:].translate(symbol_map).split(' ')
            Ramen.log_join(parser_info, users) 


    def pong(pong_string):
        return [Ramen.build_msg(body=pong_string, msg_type='PONG')]


    def join(channel):
        return [Ramen.build_msg(msg_type='JOIN', send_to=channel)]


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
       
        elif comid == 'weather':
            return Ramen.weather(receiver, args)

        elif comid == 'wiki':
            return Ramen.wiki(receiver, args)

        else:
            return None


    def help(info, nick, receiver, args):
        if not args[0]:
           return [Ramen.build_msg(send_to=receiver, body='List of Commands:'),\
                   Ramen.build_msg(send_to=receiver, body='- help'),\
                   Ramen.build_msg(send_to=receiver, body='- int'),\
                   Ramen.build_msg(send_to=receiver, body='- lastseen'),\
                   Ramen.build_msg(send_to=receiver, body='- src'),\
                   Ramen.build_msg(send_to=receiver, body='- tell'),\
                   Ramen.build_msg(send_to=receiver, body='- weather'),\
                   Ramen.build_msg(send_to=receiver, body='- wiki'),\
                   Ramen.build_msg(send_to=receiver, body='Try .help <command_name> to check command\'s syntax')]
                   

        elif args[0] == 'help':
            return [Ramen.build_msg(send_to=receiver, body='.help [command]: shows command sintax or, without arguments, the list of commands')]

        elif args[0] == 'lastseen':
            return [Ramen.build_msg(send_to=receiver, body='.lastseen <user>: shows timestamp of a user\'s last connection')]


        elif args[0] == 'tell':
            return [Ramen.build_msg(send_to=receiver, body='.tell <user>: leave a message for a disconnected user. he\'ll receive it when he writes again on the channel')]

        elif args[0] == 'src':
            return [Ramen.build_msg(send_to=receiver, body='.src: ramenbot is libre baby')]

        elif args[0] == 'int':
            return [Ramen.build_msg(send_to=receiver, body='.int <somthing>: Intesifies something')]

        elif args[0] == 'weather':
            return [Ramen.build_msg(send_to=receiver, body='.weather <city>, <region>, [<country>], [<unit>]: Tells you the climate in that region')]

        elif args[0] == 'wiki':
            return [Ramen.build_msg(send_to=receiver, body='.wiki <something>: Looks something up in wikipedia')]


    def source(info, nick, receiver):
        return [Ramen.build_msg(send_to=receiver, body='ramenbot v{0} [https://github.com/argot42/ramenbot.git]', fparts=(__version__,))]


    def tell(info, nick, receiver, args):
        if not args[0]:
            return [Ramen.build_msg(send_to=receiver, body='Try .help tell')]
        elif len(args) < 1:
            return [Ramen.build_msg(send_to=receiver, body='The msg need a body')]

        chop = Chopsticks(info['tellfile'])

        try:
            if receiver[0] != '#':
                chop.storemsg(nick, args[0], args[1:], 1)

            else:
                chop.storemsg(nick, args[0], args[1:], 0)


        except:
            return [Ramen.build_msg(send_to=receiver, body='For some reason the message couldn\'t be stored, sorry :c')]

        else:
            return [Ramen.build_msg(send_to=receiver, body='The msg will be delivered :3')]

    def lastseen(info, nick, receiver, args):
        if not args[0]:
            return [Ramen.build_msg(send_to=receiver, body='Baka, this command needs a valid nick as argument')]

        chop = Chopsticks(info['tellfile'])

        # retrieves user lastseen timestamp from database
        # and converts it into a datetime obj
        timestamp = chop.user_rts(args[0])

        if not timestamp:
            return [Ramen.build_msg(send_to=receiver, body='That person didn\'t connect while I was around')]

        date = datetime.datetime.fromtimestamp(timestamp)

        return [Ramen.build_msg(send_to=receiver, body='{0} was last seen {1} utc', fparts=(args[0], date.strftime('on %Y-%m-%d at %H:%M:%S')))]


    def inte(receiver, args):
        if not args[0]:
            return [Ramen.build_msg(send_to=receiver, body='Needs argument to intensify')]

        return [Ramen.build_msg(send_to=receiver, body='[{0} INTENSIFIES]', fparts=(' '.join(args).upper(),))]


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

            pack.append(Ramen.build_msg(send_to=sendto, body='{0} left this msg for {1}: {2}', fparts=(msg[0], nick, msg[1])))


        return pack


    def weather(receiver, args):
        try:
            url = Ramen.parse_weather(args)
        except RuntimeError as err:
            return [Ramen.build_msg(send_to=receiver, body='{0}', fparts=(err.args[1],))]
            
        with urllib.request.urlopen(url) as response:
            res_obj = json.loads(response.read().decode('utf-8'))


        # check if the query was succesful
        chan = res_obj['query']['results']['channel']
        if not 'location' in chan:
            return [Ramen.build_msg(send_to=receiver, body='It\'s Yahoo Weather\'s fault >:(')]

        place = chan['location']
        
        # todays weather
        wea = chan['item']['forecast'][0]

        return [Ramen.build_msg(send_to=receiver, body='Current conditions in {0}, {1}, {2} - [{3}] High: {4} Low: {5}',fparts=(\
                place['city'], place['region'], place['country'],\
                wea['text'], wea['high'], wea['low']))]


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
            return [Ramen.build_msg(send_to=receiver, body='This commands needs at least one argument')]

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
            return [Ramen.build_msg(send_to=receiver, body='No article found')]

        else:
            return [Ramen.build_msg(send_to=receiver, body='{0}', fparts=(item[1]['canonicalurl']))]


    def build_msg(send_to='', body='', msg_type='PRIVMSG', fparts=()):
        header_content = [msg_type]
        if send_to: header_content.append(send_to)

        if msg_type in ['JOIN', 'NICK']:
            msg_body = ''
        else:
            msg_body = ' :' + body.format(*fparts)

        return ('{0}{1}\r\n'.format(' '.join(header_content), msg_body)).encode('utf-8')
