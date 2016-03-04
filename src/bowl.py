import sys, socket
from os.path import expanduser, isfile

from ramen import Ramen
from chopsticks import Chopsticks
from sqlite3 import OperationalError

class Bowl:
    def __init__(self, host, port, nick, realname, channel, tellfile):
        self.host = host
        self.port = port
        self.nick = nick
        self.realname = realname
        self.channel = channel
        self.tellfile = expanduser(tellfile)

        # if file exist do nothing
        if isfile(self.tellfile):
            return

        # if not
        # creating tellfile.db
        chop = Chopsticks(self.tellfile)

        # setup db table structure
        chop.setup(["CREATE TABLE user(id_user INTEGER PRIMARY KEY NOT NULL, nickname TEXT UNIQUE, lastseen INTEGER)", "CREATE TABLE msg(id_msg INTEGER PRIMARY KEY NOT NULL, body TEXT, sender_id INTEGER NOT NULL, receiver_id INTEGER NOT NULL, FOREIGN KEY(sender_id) REFERENCES user(id_user), FOREIGN KEY(receiver_id) REFERENCES user(id_user))"])


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

            for line in temp:

                if not line:
                    continue

                # parse recieved msg and return a list with responses
                response = Ramen.parse(line, parser_info)

                # if response not null send it
                if not response:
                    continue

                for msg in response:
                    ircsock.send(msg)
