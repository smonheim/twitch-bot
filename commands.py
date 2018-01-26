import os
import configparser

class commands:
    commands = configparser.ConfigParser()
    fileHooks = {}

    def __init__(self):
        if os.path.isfile('commands.ini'):
            self.commands.read('commands.ini')
            self.setDefaults()
            self.setFileHooks()
            self.default = False
        else:
            self.generateDefaultCommands()
            self.default = True

    def setDefaults(self):
        self.commands.set("DEFAULT","type","1")
        self.commands.set("DEFAULT","trigger","")
        self.commands.set("DEFAULT","response","")
        self.commands.set("DEFAULT","defaultResponse","")
        self.commands.set("DEFAULT","reply","0")
        self.commands.set("DEFAULT","period","-1")
        self.commands.set("DEFAULT","adminOnly","0")

    def generateDefaultCommands(self):
        self.commands.add_section("cmdPing")
        self.commands.set("cmdPing","type","1")
        self.commands.set("cmdPing","trigger","!ping")
        self.commands.set("cmdPing","response","Pong!")

        with open('commands.ini', 'w') as f:
            self.commands.write(f)

    # Update fileHooks list
    def setFileHooks(self):
        # Clear current fileHooks
        self.fileHooks.clear()

        # Loop through all commands, serch for fileHooks and add them
        for i in self.commands:
            if int(self.commands[i]["type"]) == 4:
                with open(self.commands[i]['response'], 'r') as f:
                    self.fileHooks[i] = f.read()

    def reloadCommands(self):
        self.commands.clear()
        self.commands.read("commands.ini")
        self.commands.setDefaults()
        self.setFileHooks()
