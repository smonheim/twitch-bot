import config as cfig
import bot as udpbot
import commands as twitchcommands
import sys
import urllib.request
import random

# Load the config settings
print('==> Loading settings')
conf = cfig.config()

# Check if we have generated a default config.ini, if so exit
if conf.default == True:
    print('[!] Could not find config.ini. A default config.ini has been generated in the bot folder response. Please edit it and run the bot again.')
    sys.exit()

# If we haven't generated a default config.ini, check if it's valid
if conf.verifyConfigFile() == False:
    print('[!] Invalid config file')
    sys.exit()
else:
    print('==> Settings loaded')

# Load commands.ini
print('==> Loading commands')
cmd = twitchcommands.commands()

# Check if we have generated a default commands.ini, if so exit
if cmd.default == True:
    print('[!] Could not find command.ini. A default command.ini has been generated in the bot folder response. Please edit it and run the bot again.')
    sys.exit()

# Ini files are valid, create a bot instance
print('==> Connecting to Twitch IRC server')
bot = udpbot.bot(conf.config['auth']['host'], int(conf.config['auth']['port']), conf.config['auth']['username'], conf.config['auth']['password'], conf.config['auth']['channel'], int(conf.config['auth']['timeout']))

# Connect to IRC server
if bot.connect() == False:
    print('[!] Connection error response. Please check your internet connection and config.ini file')
    sys.exit()

# Send login packets
print('==> Logging in')
bot.login()

# Check login errors
response = bot.getResponse()
if response.lower().find('error') != -1:
    print('[!] Login error response. Please check your config.ini file')
    if conf.config['debug']['showServerOutput']: print('/r/n/r/n' + response)
    sys.exit()

# Send start message if needed
if conf.config['chat']['startMessage'] != '':
    bot.sendChatMessage(conf.config['chat']['startMessage'])

# No errors, start the loop
print('==> smoonybot is listening!')
while 1:
    # Debug message
    conf.debugMessage('==> Looping...')

    # Loop through all file hooks
    for i in cmd.fileHooks:
        try:
            # Get content of that file
            oldContent = cmd.fileHooks[i]
            newContent = open(cmd.commands[i]['response'], 'r').read()

            # If content is different, update fileHook and send message
            if newContent != oldContent and newContent != '':
                cmd.fileHooks[i] = newContent
                print('==> Content changed, sending new content to chat (' + i + ')')
                bot.sendChatMessage(newContent)
        except:
            print('[!] Error while reading file (' + i + ')')

    try:
        # Get new packets
        response = bot.getResponse().lower()

        # Check if we have new packets
        # TODO: this if is probably useless
        if response != None:
            # Make sure this is a PRIVMSG packet
            if response.find('privmsg') != -1:
                # Increment received messages
                bot.receivedMessages += 1

                # Get who has sent the message
                rFrom = response.split('!')[0][1:]

                # Set final message to empty
                message=''

                # Check if that message triggered an interal command
                if response.find('!reloadcmd') != -1:
                    # Reload commands (!reloadCmd)
                    bot.sendChatMessage('Commands reloaded!')
                    cmd.reloadCommands()
                # elif response.find('!othercommand') != -1: ...

                # Check if that message triggered a custom command
                # Loop through all commands
                for i in cmd.commands:
                    # Get command data
                    cmdName = i
                    cmdType = int(cmd.commands[i]['type'])
                    cmdTrigger = cmd.commands[i]['trigger'].lower()
                    cmdResponse = cmd.commands[i]['response']
                    cmdDefaultResponse = cmd.commands[i]['defaultResponse']
                    cmdReply = int(cmd.commands[i]['reply'])
                    cmdPeriod = int(cmd.commands[i]['period'])
                    cmdAdminOnly = int(cmd.commands[i]['adminOnly'])
                    cmdFirstValue = int(cmd.commands[i]['firstValue'])
                    cmdSecondValue = int(cmd.commands[i]['secondValue'])
                    cmdPossibleAnswers = [x for x in cmd.commands[i]['possibleAnswers'].split(',')]

                    # Make sure the command has valid response and period (default for non-periodic commands is -1)
                    if cmdResponse != '' and cmdPeriod != 0:
                        if cmdType == 1:
                            # Normal command
                            if response.find(cmdTrigger) != -1:
                                if cmdAdminOnly == 1 and not conf.isAdmin(rFrom):
                                    print('==> ' + rFrom + ' triggered a simple admin command, but they are not an admin')
                                else:
                                    print('==> ' + rFrom + ' triggered a simple command (' + cmdName + ')')
                                    message=cmdResponse
                                    if cmdReply == 1: message=rFrom + ' >> ' + message

                        elif cmdType == 2:
                            # Periodic command
                            if bot.receivedMessages % cmdPeriod == 0:
                                print('==> Sending periodic command (' + cmdName + ')')
                                message=cmdResponse
                                bot.receivedMessages = 0

                        elif cmdType == 3:
                            # API command
                            if response.find(cmdTrigger) != -1:
                                try:
                                    # Get API content and send it
                                    req = urllibot.request.Request(cmdResponse,data=None,headers={'User-Agent': 'Mozilla/5.0'})
                                    apiResponse = urllibot.request.urlopen(req).read().decode('UTF-8')
                                    message=apiResponse
                                    if cmdReply == 1: message=rFrom + ' >> ' + message
                                    print('==> ' + rFrom + ' triggered an API command (' + cmdName + ')')
                                except:
                                    print('[!] Error while requesting API command (' + cmdName + ')')

                        elif cmdType == 5:
                            # File read command
                            if response.find(cmdTrigger) != -1:
                                try:
                                    # Read file content and send it
                                    print('==> ' + rFrom + ' triggered a file read command (' + cmdName + ')')
                                    content = open(cmdResponse, 'r').read()

                                    # If content is empty, send default response
                                    if content == '':
                                        message = cmdDefaultResponse
                                    else:
                                        message = content

                                    if cmdReply == 1: message=rFrom + ' >> ' + message
                                except:
                                    print('[!] Error while reading file (' + i + ')')

                        elif cmdType == 6:
                            # Callout command, any command that uses a recipient name at the end
                            if response.find(cmdTrigger) != -1:
                                if cmdAdminOnly == 1 and not conf.isAdmin(rFrom):
                                    print('==> ' + rFrom + ' triggered a simple admin command, but they are not an admin')
                                else:
                                    print('==> ' + rFrom + ' triggered a simple command (' + cmdName + ')')
                                    recipient = response.split(' ')[-1]
                                    message=cmdResponse + recipient
                                    if cmdReply == 1: message=rFrom + ' >> ' + message

                        elif cmdType == 7:
                            # any type of command that uses the form: subject cmdReplay user name
                            if response.find(cmdTrigger) != -1:
                                if cmdAdminOnly == 1 and not conf.isAdmin(rFrom):
                                    print('==> ' + rFrom + ' triggered a simple admin command, but they are not an admin')
                                else:
                                    print('==> ' + rFrom + ' triggered a simple command (' + cmdName + ')')
                                    recipient = response.split(' ')[-1].strip('\r\n')
                                    message = recipient + ' ' + cmdResponse + ' ' + rFrom
                                    if cmdReply == 1: message=rFrom+' >> ' + message

                        elif cmdType == 8:
                            # Command that answers yes or no questions with 
                            if response.find(cmdTrigger) != -1:
                                text = response.split(':')[2]
                                try:
                                    question = text.split(' ', 1)[1].strip('\r\n')
                                except:
                                    question = False
                                if cmdAdminOnly == 1 and not conf.isAdmin(rFrom):
                                    print('==> ' + rFrom + ' triggered a simple admin command, but they are not an admin')
                                else:
                                    if question:
                                        print('==> ' + rFrom + ' triggered a simple command (' + cmdName + ')')
                                        answerIndex = random.randint(cmdFirstValue, cmdSecondValue)
                                        message = rFrom + ' asked: ' + question + ' '*30 + cmdResponse + ' ' + cmdPossibleAnswers[answerIndex]
                                        if cmdReply == 1: message=rFrom+' >> ' + message
                                    else:
                                        print('==> ' + rFrom + ' triggered a simple command (' + cmdName + ') without a question!')
                                        answerIndex = random.randint(cmdFirstValue, cmdSecondValue)
                                        message = 'You must ask me a question if you want an answer ' + rFrom
                                        if cmdReply == 1: message=rFrom + ' >> ' + message

                # Send final message if needed
                if message != '':
                    bot.sendChatMessage(message)

            # Print received packet if needed
            if int(conf.config['debug']['showServerOutput']) == 1:
                print(response, end='')
    except:
        pass
