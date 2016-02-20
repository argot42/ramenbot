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
        ircsock = 
