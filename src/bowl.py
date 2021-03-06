import sys, socket, ssl
from os.path import expanduser

from ramen import Ramen
from chopsticks import Chopsticks
from sqlite3 import OperationalError

class Bowl:
    def __init__(self, host='', port=0, nick='', realname='', channel='', tellfile='', ssl=False):
        self.host = host
        self.port = port
        self.nick = nick
        self.realname = realname
        self.channel = channel
        self.tellfile = expanduser(tellfile)
        self.ssl = ssl

        # creating tellfile.db
        chop = Chopsticks(self.tellfile)

        # setup db table structure
        chop.setup("""CREATE TABLE IF NOT EXISTS user(nickname TEXT PRIMARY KEY NOT NULL, lastseen REAL, cozy INTEGER NOT NULL, autism INTEGER NOT NULL);
                CREATE TABLE IF NOT EXISTS msg(id_msg INTEGER PRIMARY KEY NOT NULL, body TEXT, sender_id INTEGER NOT NULL, receiver_id INTEGER NOT NULL, priv INTEGER NOT NULL, FOREIGN KEY(sender_id) REFERENCES user(nickname))""")


    def connect(self):
        # connect to server
        ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ircsock.connect((self.host, self.port))

        if self.ssl:
            ircsock = ssl.wrap_socket(ircsock)

        # send nick and user info 
        ircsock.send(Ramen.build_msg(msg_type='NICK', send_to=self.nick))
        ircsock.send(Ramen.build_msg(msg_type='USER', send_to=' '.join([self.nick, self.nick, self.nick]), body=self.realname))

        parser_info = {"nick": self.nick,\
                        "channel": self.channel,\
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
