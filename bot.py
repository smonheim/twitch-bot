import socket as sock

class bot:
    __socket = sock.socket()
    host = None
    port = None
    username = None
    password = None
    channel = None

    def __init__(self, __host, __port, __username, __password, __channel, __timeout):
        self.host = __host
        self.port = __port
        self.username = __username
        self.password = __password
        self.channel = __channel
        self.sentMessages = 0
        self.receivedMessages = 0
        self.__socket.settimeout(__timeout)

    def sendMessage(self, message, encoding='UTF-8'):
        self.__socket.send(bytes(message+'\r\n', encoding))

    def connect(self):
        try:
            self.__socket.connect((self.host, self.port))
            return True
        except:
            return False

    def login(self):
        self.sendMessage('PASS' + self.password)
        self.sendMessage('NICK' + self.username)
        self.sendMessage('USER' + self.username)
        self.sendMessage('JOIN #' + self.channel)

    def sendChatMessage(self, message, incrementMessages=True):
        self.sendMessage('PRIVMSG #' + self.channel + ' :' + message)

        if incrementMessages:
            self.sentMessages += 1

    def getResponse(self.length=4096):
        return self.__socket.recv(length).decode()
