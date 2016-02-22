import re

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

        else:
            i = 0
            for word in msg_splited:
                if not word:
                    continue
                
                if word[0:2] == ':.':
                    return Ramen.resolv_com(parser_info, msg_splited[i:])

                i+= 1



    def pong(pong_string):
        return b'PONG %b\r\n' % (str.encode(pong_string, 'utf-8'))


    def join(channel):
        return b'JOIN %b\r\n' % (str.encode(channel, 'utf-8'))


    def help(info, args):
        return b'PRIVMSG %b :no help yet\r\n' % (str.encode(info['channel'], 'utf-8'))


    def resolv_com(info, com):
        match = re.match(r':\.(?P<com_id>\w+)', com[0])

        if not match:
            return None


        if match.group('com_id') == 'help':
            return Ramen.help(info, com[1:])

        elif match.group('com_id') == 'tell':
            print("TELL")

        elif match.group('com_id') == 'lastseen':
            print("LAST")

        else:
            return None
