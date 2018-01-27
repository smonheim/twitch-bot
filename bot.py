import socket as sock

class bot:
    __socket = sock.socket()
    host = None
    port = None
    username = None
    password = None
    channel = None

    def __init__(self, __host, __port, __username, __password, __channel, __timeout):
        self.length= 4096
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
        self.sendMessage('PASS ' + self.password + '\r\n')
        self.sendMessage('NICK ' + self.username + '\r\n')
        self.sendMessage('USER ' + self.username + '\r\n')
        self.sendMessage('JOIN #' + self.channel + '\r\n')

    def sendChatMessage(self, message, incrementMessages=True):
        self.sendMessage('PRIVMSG #' + self.channel + ' :' + message)

        if incrementMessages:
            self.sentMessages += 1

    def getResponse(self, length=4096):
        message = self.__socket.recv(length).decode()
        print(message)
        return message
