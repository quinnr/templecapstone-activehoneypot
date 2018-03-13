from twisted.conch.ssh import factory
from twisted.conch.ssh.transport import SSHServerTransport
from twisted.conch import recvline
from twisted.internet import reactor
from twisted.conch.ssh.keys import Key
from twisted.cred.portal import Portal

print("Starting SSH server.")

print("Opening public and private key files.")
with open('id_rsa') as privateKeyFile:
    privateKeyText = privateKeyFile.read()
    privateKey = Key.fromString(data=privateKeyText)

with open('id_rsa.pub') as publicKeyFile:
    publicKeyText = publicKeyFile.read()
    publicKey = Key.fromString(data=publicKeyText)


# Todo: Implement actual portal code
class HoneypotPortal(Portal):
    pass


# Todo: Implement factory code
class HoneypotFactory(factory.SSHFactory):
    privateKeys = {'ssh-rsa': privateKey}
    publicKeys = {'ssh-rsa': publicKey}
    portal = Portal(None)  # This should later be changed to HoneypotPortal instead of none once that class is ready.


reactor.listenTCP(2222, HoneypotFactory())  # Open TCP port using specified factory to handle connections.
reactor.run()

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
