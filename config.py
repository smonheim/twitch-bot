import configparser
import os

class config:
    config = configparser.ConfigParser()

    def __init__(self):
        if os.path.isfile('config.ini'):
            self.config.read('config.ini')
            self.default = False
        else:
            self.generateNewConfig()
            self.default = True

    def verifyConfigFile(self):
        try:
            self.config.get('auth', 'host')
            self.config.get('auth', 'port')
            self.config.get('auth', 'username')
            self.config.get('auth', 'password')
            self.config.get('auth', 'channel')
            self.config.get('auth', 'timeout')
            self.config.get('chat', 'startMessage')
            self.config.get('chat', 'botAdmins')
            self.config.get('debug', 'showServerOutput')
            self.config.get('debug', 'showDebugMessages')
            print(self.config.get('auth', 'username'))
            return True
        except:
            return False

    def generateNewConfig(self):

        self.config.add_section('auth')
        self.config.set('auth', 'host', 'irc.twitch.tv')
        self.config.set('auth', 'port', '6667')
        self.config.set('auth', 'username', 'TWITCH_BOT_USERNAME')
        self.config.set('auth', 'password', 'TWITCH_BOT_OAUTH_TOKEN')
        self.config.set('auth', 'channel', 'YOUR_TWITCH_CHANNEL')
        self.config.set('auth', 'timeout', '2')

        self.config.add_section('chat')
        self.config.set('chat', 'startMessage', "Hi! I'm RageMageBot!")
        self.config.set('chat', 'botAdmins', 'admin1,admin2')

        self.config.add_section('debug')
        self.config.set('debug', 'showServerOutput', '0')
        self.config.set('debug', 'showDebugMessages', '0')

        with open('config.ini', 'w') as f:
            self.config.write(f)


    def isAdmin(self, who):
        return who in self.config['chat']['botAdmins'].split(',')


    def debugMessage(self, message):
        if int(self.config['debug']['showDebugMessages']) == 1:
            print(message)
