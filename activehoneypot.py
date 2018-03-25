# TODO: Clean up these imports
import sys
import os
import subprocess
import datetime

from twisted.conch import avatar
from twisted.conch.ssh import factory, session, userauth, connection, keys
from twisted.conch.ssh.transport import SSHServerTransport
from twisted.cred import portal
from twisted.cred.checkers import FilePasswordDB
from twisted.cred.portal import Portal
from twisted.internet import reactor, protocol
from twisted.python import log, components
from zope.interface import implementer

# TODO: Need to replace these keys I copied from the internet with newly generated keys, using the ssh-keygen moduli generation
PRIMES = {
    2048: [(2,
            24265446577633846575813468889658944748236936003103970778683933705240497295505367703330163384138799145013634794444597785054574812547990300691956176233759905976222978197624337271745471021764463536913188381724789737057413943758936963945487690939921001501857793275011598975080236860899147312097967655185795176036941141834185923290769258512343298744828216530595090471970401506268976911907264143910697166165795972459622410274890288999065530463691697692913935201628660686422182978481412651196163930383232742547281180277809475129220288755541335335798837173315854931040199943445285443708240639743407396610839820418936574217939)],
    4096: [(2,
            889633836007296066695655481732069270550615298858522362356462966213994239650370532015908457586090329628589149803446849742862797136176274424808060302038380613106889959709419621954145635974564549892775660764058259799708313210328185716628794220535928019146593583870799700485371067763221569331286080322409646297706526831155237865417316423347898948704639476720848300063714856669054591377356454148165856508207919637875509861384449885655015865507939009502778968273879766962650318328175030623861285062331536562421699321671967257712201155508206384317725827233614202768771922547552398179887571989441353862786163421248709273143039795776049771538894478454203924099450796009937772259125621285287516787494652132525370682385152735699722849980820612370907638783461523042813880757771177423192559299945620284730833939896871200164312605489165789501830061187517738930123242873304901483476323853308396428713114053429620808491032573674192385488925866607192870249619437027459456991431298313382204980988971292641217854130156830941801474940667736066881036980286520892090232096545650051755799297658390763820738295370567143697617670291263734710392873823956589171067167839738896249891955689437111486748587887718882564384870583135509339695096218451174112035938859)],
}

SUPPORTED_COMMANDS = ["ls", "du", "ifconfig", "uname", "wget"]


log.startLogging(sys.stderr)
print("Starting SSH server.")

print("Opening public and private key files.")
with open('id_rsa') as privateKeyFile:
    privateKeyText = privateKeyFile.read()
    privateKey = keys.Key.fromString(data=privateKeyText)

with open('id_rsa.pub') as publicKeyFile:
    publicKeyText = publicKeyFile.read()
    publicKey = keys.Key.fromString(data=publicKeyText)


# Todo: Implement actual portal code
class HoneypotPortal(Portal):
    pass


@implementer(portal.IRealm)
class HoneypotRealm(object):
    def requestAvatar(self, avatarID, mind, *interfaces):
        return interfaces[0], HoneypotAvatar(
            avatarID), lambda: None  # This lambda:None can be replaced with a function to run on logout


class HoneypotAvatar(avatar.ConchUser):
    def __init__(self, username):
        avatar.ConchUser.__init__(self)
        self.username = username
        # print("USERNAME IS "+ self.username.decode("utf-8")) # You can get the password from this line to save it in a logfile,
        # trying to find out where to get the password
        self.channelLookup.update({b'session': session.SSHSession})

    pass


class HoneypotProtocol(protocol.Protocol):  # Contains functions for handling input and output from the connection
    
    sessionNum = 0
    ipAddr = ''
    logFolder = ""
    def dataReceived(self, data):  # TODO: Start implementation of the protocol!
       # ipAddr = self.transport.getPeer().address.host
       # commandsEntered = self.ipAddr + '-'+ self.sessionNum + '-commands.txt'
        fp = open(self.logFolder, "a")

        if data == b'\r':  # Convert weird line returns to be proper
            data = b'\r\n'
        elif data == b'\x03':  # Quit on receiving Ctrl+C
            self.transport.loseConnection()
            return

        data = self.bytestoString(data)  # convert the raw bytes to a string so we can manipulate it
        fp.write(data + "\n")
        command = self.commandWithoutArguments(data)  # get the command without any arguments
        print("Test of command without arguments function: " + command)

        executableAllowed = self.isCommandSupported(command)

        if executableAllowed:
            response = command + ": command is allowed to execute"
            print(response + "\n")
            self.ls_command()

        if executableAllowed == False:
            response = command + ": command not found"
            fp.write(response + "\n")
            self.sendLine(response)

            self.showPrompt()

    def sendLine(self, string):
        string = string + "\r\n"
        self.transport.write(string)
        return

    def connectionMade(self):  # Run when connection is first made.
        self.logMetadata()
	self.displayMessageOfDay()
        self.transport.write("\r\n")
        self.showPrompt()

    def commandWithoutArguments(self, data):  # return first 'word' of a string, no arguments
        return data.split(' ', 1)[0]

    def isCommandSupported(self, command):  # Checks config to see if the sent command is allowed to run
        if command in SUPPORTED_COMMANDS:
            return True
        return False

    def bytestoString(self, bytes):
        return bytes.decode("utf-8").rstrip()


    # Commands
    def ls_command(self, arguments=[]):
        self.sendLine("Desktop\tPublic\tTemplates\n\rDocuments\tDownloads\tMusic\n\rPictures")
        return

    def displayMessageOfDay(self):
        file = open("./content/motd")
        for line in file:
            self.transport.write(line)
        return

    def showPrompt(self):
        prompt = "root@servermachine:~$ "
        self.transport.write(prompt)
        return

    def logMetadata(self):
	ipAddr = self.transport.getPeer().address.host

    	self.logFolder = ipAddr + '-' + str(self.sessionNum) + '-commands.txt'
        while (os.path.isfile(self.logFolder)):
            	self.sessionNum+=1
  	    	self.logFolder = ipAddr +'-'+str(self.sessionNum)+'-commands.txt'

	access = datetime.datetime.now()
	accessTime = str(access.hour) + ":" + str(access.minute) + ":" + str(access.second)
	accessDate = str(access.year) + "/" + str(access.month) + "/" + str(access.day)
	print("accessTime: ", accessTime, " accessDate: ", accessDate, "\n") 
	#get location

class HoneypotSession(object):
    def __init__(self, avatar):
        pass

    ## Currently the SSH client gives a weird error about PTY sessions, this code doesn't work but
    ## is my current attempt to fix that.
    # def getPty(self, term, windowSize, attrs):
    # print("PTY session")
    # self.windowSize = windowSize
    # protocol = HoneypotProtocol()
    # transport = SSHSessionProcessProtocol(self)
    # protocol.makeConnection(transport)
    # transport.makeConnection(session.wrapProtocol(protocol))
    # return None

    def execCommand(self, proto, cmd):
        raise Exception("Remote command execution mode is disabled.")

    # def request_pty_req(self, data):
    # return True
    # raise Exception("PTY requested")

    def openShell(self, transport):
        protocol = HoneypotProtocol()
        protocol.makeConnection(transport)
        transport.makeConnection(session.wrapProtocol(protocol))

    def eofReceived(self):
        pass

    def closed(self):
        pass


components.registerAdapter(HoneypotSession, HoneypotAvatar, session.ISession)


# Todo: Implement factory code
class HoneypotFactory(factory.SSHFactory):
    privateKeys = {b'ssh-rsa': privateKey}
    publicKeys = {b'ssh-rsa': publicKey}
    protocol = SSHServerTransport
    services = {
        b'ssh-userauth': userauth.SSHUserAuthServer,
        b'ssh-connection': connection.SSHConnection
    }

    def getPrimes(self):
        return PRIMES


portal = portal.Portal(HoneypotRealm())
passwdfile = FilePasswordDB("passwords")
portal.registerChecker(passwdfile)
factory = HoneypotFactory()
factory.portal = portal

reactor.listenTCP(2222, factory)  # Open TCP port using specified factory to handle connections.
reactor.run()
print("Server successfully running")
# TODO: Implement the Protocol basics
# class InputOutputProtocol(recvline.HistoricRecvLine):
#     def __init__(self, user):
#         self.user = user
#
#     def connectionMade(self):
#         recvline.HistoricRecvLine.connectionMade(self)
#         self.initializeScreen(self)
#         self.terminal.write("This is a test")
#         self.terminal.nextLine()
#         self.showPrompt()
#
#     def showPrompt(self):
#         self.terminal.write("> ")
#
#     def lineReceived(self, line):
#         line = line.strip()
