import sys, socket

from ramen import Ramen

class Bowl:
    def __init__(self, host, port, nick, realname, channel, tellfile):
        self.host = host
        self.port = port
        self.nick = nick
        self.realname = realname
        self.channel = channel
        self.tellfile = tellfile

    def connect(self):
        # connect to server
        ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ircsock.connect((self.host, self.port))

        # send nick and user info 
        ircsock.send(b'NICK %b\r\n' % self.nick)
        ircsock.send(b'USER %b %b %b :%b\r\n' % (self.nick, self.nick, self.nick, self.realname))

        parser_info = {"nick": (self.nick.decode('utf-8')),\
                        "channel": (self.channel.decode('utf-8')),\
                        "tellfile": self.tellfile\
                        }

        while True:
            readbuffer = str()
            readbuffer = readbuffer + ircsock.recv(1024).decode('utf-8')
            temp = readbuffer.split('\n')
            print(temp)

            for line in temp:
                t = str.rstrip(line)
                t = str.split(t)

                if not line:
                    continue

                # parse recieved msg
                response = Ramen.parse(line, parser_info)

                # if response not null send it
                if not response:
                    continue

                ircsock.send(response)
