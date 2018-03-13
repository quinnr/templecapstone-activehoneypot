from twisted.conch.ssh import factory
from twisted.conch.ssh.transport import SSHServerTransport
from twisted.conch import recvline

print("This is a test.")


class HoneypotFactory(factory.SSHFactory):
    protocol = SSHServerTransport

class InputOutputProtocol(recvline.HistoricRecvLine):
    def __init__(self, user):
        self.user = user

    def connectionMade(self):
        recvline.HistoricRecvLine.connectionMade(self)
        self.initializeScreen(self)
        self.terminal.write("This is a test")
        self.terminal.nextLine()
        self.showPrompt()

    def showPrompt(self):
        self.terminal.write("> ")

    def lineReceived(self, line):
        line = line.strip()