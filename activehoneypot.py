# TODO: Clean up these imports
import sys
import subprocess
import urllib.request
import time
import fs
from fs import tempfs
from fs.osfs import OSFS

#Added by Shlomo
#import datetime
import MySQLdb
import requests
import os
import pyrebase

from datetime import time, datetime
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

SUPPORTED_COMMANDS = ["ls", "df", "ifconfig", "uname", "wget", "exit", "shutdown", "whoami", "pwd", "cd", "rm", "rmdir", "cat"]


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
    filesDownloaded = 0
    filesys = None
    attackerNum = 0
    working_directory = "/home"

    def dataReceived(self, data):  # TODO: Start implementation of the protocol!
       # ipAddr = self.transport.getPeer().address.host
       # commandsEntered = self.ipAddr + '-'+ self.sessionNum + '-commands.txt'
        fp = open("/opt/tomcat/webapps/ActiveHoneypotWeb/logfiles/"+self.logFolder, "a+")

        if data == b'\r':  # Convert weird line returns to be proper
            data = b'\r\n'
        elif data == b'\x03':  # Quit on receiving Ctrl+C
            self.transport.loseConnection()
            return
        if data == b'\r\n' or data == b'\n' or data == b'\r' or data == b'\n\r':
            #self.showPrompt()
            return

        data = self.bytestoString(data)  # convert the raw bytes to a string so we can manipulate it
        timestamp = '[{:%Y-%m-%d %H:%M:%S}]'.format(datetime.now())
        fp.write(timestamp + " " + data + "<br/>\n")
        command = self.commandWithoutArguments(data)  # get the command without any arguments
        arguments = self.commandGetArguments(data)
        print("Test of command without arguments function: " + command)

        executableAllowed = self.isCommandSupported(command)

        if executableAllowed:
            if command == "ls":
                self.ls_command(arguments)
            elif command == "wget":
                self.wget_command(arguments)
            elif command =="uname":
                self.uname_command(arguments)
            elif command == "exit" or command == "shutdown":
                self.exit_command(arguments)
                self.transport.loseConnection()
            elif command == "df":
                self.df_command(arguments)
            elif command == "ifconfig":
                self.ifconfig_command(arguments)
            elif command == "whoami":
                self.whoami_command(arguments)
            elif command == "pwd":
                self.pwd_command(arguments)
            elif command == "cd":
                self.cd_command(arguments)
            elif command == "rm":
                self.rm_command(arguments)
            elif command == "rmdir":
                self.rmdir_command(arguments)
            elif command == "cat":
                self.cat_command(arguments)
            #elif command == "passwd":
            #    self.passwd_command(arguments)
            else:
                print("ERROR: Function for given command not found.\n")
        elif executableAllowed == False and command.isspace() == False:
            response = command + ": command not found"
            fp.write(timestamp + " " +response + "<br/>\n")
            self.sendLine(response)

        fp.close()
        self.showPrompt()
        return

    def sendLine(self, string):
        string = string + "\r\n"
        self.transport.write(string)
        return

    def connectionMade(self):  # Run when connection is first made.
        print("self.logFolder: ", self.logFolder)
        self.logMetadata()
        self.displayMessageOfDay()
        self.transport.write("\r\n")
        self.showPrompt()
        self.filesys = FileSystem()

    def commandWithoutArguments(self, data):  # return first 'word' of a string, no arguments
        return data.split(' ', 1)[0]

    def commandGetArguments(self, data):
        fullString = data.split(' ')
        result = []
        for entry in fullString[1:]:
            result.append(entry)
        return result

    def isCommandSupported(self, command):  # Checks config to see if the sent command is allowed to run
        if command in SUPPORTED_COMMANDS:
            print("command "+ command + " is supported")
            return True
        return False

    def bytestoString(self, bytes):
        return bytes.decode("utf-8").rstrip()


    # Commands

    #TODO: write passwd command, needs interactivity which we don't support yet
    #def passwd_command(self, arguments=[]):
    #    if arguments:
    #        user_to_change = arguments[1]
    #    else:
    #        user_to_change = "root"

    def pwd_command(self, arguments=[]):
        self.sendLine(self.working_directory)
        return

    def cd_command(self, arguments=[]):
        if not arguments:
            self.working_directory = "/"
            return
        string_dir = arguments[0]
        if string_dir[:1] == "/":
            if filesys.filesys.isdir(string_dir):
                print("Found directory: " + string_dir)
                self.working_directory = string_dir
                return
        else:
            string_dir = self.working_directory + "/" + string_dir
            print("Searching for " + string_dir)
            if filesys.filesys.isdir(string_dir):
                print("Found directory: " + string_dir)
                self.working_directory = string_dir
                return
        self.sendLine("bash: cd: "+ string_dir +": No such file or directory.")
        return

    def cat_command(self, arguments=[]):
        if not arguments:
            self.sendLine("cat: missing operand")
            self.sendLine("Try 'cat --help' for more information.")
            return
        else:
            string_dir = arguments[0]
            if not string_dir[:1] == "/":
                string_dir = self.working_directory + "/" + string_dir
            if self.filesys.filesys.isdir(string_dir):
                self.sendLine("cat: " + string_dir + ": Is a directory")
                return
            if not self.filesys.filesys.isfile(string_dir):
                self.sendLine("cat: " + string_dir + ": File does not exist")
                return
            else:
                pointer = self.filesys.filesys.open(string_dir, "r")
                for line in pointer:
                    self.sendLine(line)
                pointer.close()
                return
            return


    def whoami_command(self, arguments=[]):
        self.sendLine("root")
        return

    def ifconfig_command(self, arguments=[]):
        self.sendLine("eth0      Link encap:Ethernet  HWaddr 08:22:27:3a:cd:14")
        self.sendLine("          inet addr:10.0.2.15  Bcast:10.0.2.255  Mask:255.255.255.0")
        self.sendLine("          UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1")
        self.sendLine("          RX packets:104664 errors:0 dropped:0 overruns:0 frame:0")
        self.sendLine("          TX packets:26173 errors:0 dropped:0 overruns:0 carrier:0")
        self.sendLine("          collisions:0 txqueuelen:1000")
        self.sendLine("          RX bytes:123000109 (123.0 MB)  TX bytes:2187316 (2.1 MB)")
        self.sendLine("")
        return

    def ls_command(self, arguments=[]):
        ls_string = ""
        for file in self.filesys.filesys.listdir(self.working_directory):
            ls_string = ls_string + file + "\r\n" # TODO: Make the formatting nicer.
        self.sendLine(ls_string)
        return

    def rm_command(self, arguments=[]):
        if not arguments:
            self.sendLine("rm: missing operand")
            self.sendLine("Try 'rm --help' for more information.")
            return
        else:
            string_dir = arguments[0]
            if not string_dir[:1] == "/":
                string_dir = self.working_directory + "/" + string_dir
            print("Searching to delete: " + string_dir)
            if self.filesys.filesys.isfile(string_dir):
                print("Found and deleting.")
                self.filesys.filesys.remove(string_dir)
                return
            elif self.filesys.filesys.isdir(string_dir):
                self.sendLine("rm: cannot remove '" + string_dir + "': Is a directory")
                return
            self.sendLine("rm: cannot remove '" + string_dir + "': No such file or directory")
        return

    def rmdir_command(self, arguments=[]):
        if not arguments:
            self.sendLine("rmdir: missing operand")
            self.sendLine("Try 'rmdir --help' for more information.")
            return
        else:
            string_dir = arguments[0]
            if not string_dir[:1] == "/":
                string_dir = self.working_directory + "/" + string_dir
            print("Searching to delete: " + string_dir)
            if self.filesys.filesys.isdir(string_dir):
                print("Found and deleting.")
                self.filesys.filesys.removedir(string_dir)
                return
            elif self.filesys.filesys.isfile(string_dir):
                self.sendLine("rmdir: cannot remove '" + string_dir + "': Is a file")
                return
            self.sendLine("rmdir: cannot remove '" + string_dir + "': No such file or directory")
        return



    def df_command(self, arguments=[]):
        #if not arguments:
        self.sendLine("Filesystem     1K-blocks    Used Available Use% Mounted on")
        self.sendLine("udev             2539452       0   2539452   0% /dev")
        self.sendLine("/dev/sda1        9156984 6489424   2179368  75% /")
        return


    def wget_command(self, arguments=[]):
        if not arguments:
            self.sendLine("wget: missing URL\n\rUsage: wget [OPTION]... [URL]...\n\r\n\rTry `wget --help' for more options.")
        else:
            print("Downloading file from " + arguments[0])
            self.sendLine("Resolving "+str(arguments[0])+"... 64.170.98.42, 4.31.198.61, 4.31.198.62, ...\r\n")
            self.sendLine("Connecting to "+arguments[0]+"... connected.\r\n")
            self.sendLine("HTTP request sent, awaiting response... 200 OK\r\n")
            time.sleep(0.5)
            self.sendLine("Length: 12136 (12K) [binary]\r\n")
            time.sleep(0.5)
            self.sendLine("\r\n\r\nfile\t\t100%[======================================>]  11.85K  --.-KB/s    in 0.003s\r\n")
            self.sendLine("2018-03-25 02:01:58 (4.27 MB/s) - ‘rfc1149’ saved [12136/12136]")
            urllib.request.urlretrieve(arguments[0], "attackerfile-" + str(self.filesDownloaded))
            self.filesDownloaded = self.filesDownloaded + 1
        return

    def uname_command(self, arguments=[]):
        if not arguments:
            self.sendLine("Linux")
            return
        else:
            flag = arguments[0].replace("-", "")
            print("Uname command run with flag: " + flag)
            if flag=="a":
                self.sendLine("Linux root 4.13.0-37-generic #42~16.04.1-Ubuntu SMP Wed Mar 7 16:03:28 UTC 2018 x86_64 x86_64 x86_64 GNU/Linux")
                return
            elif flag == "s":
                self.sendLine("Linux")
                return
            elif flag == "o":
                self.sendLine("GNU/Linux")
            else:
                self.sendLine("uname: invalid option -- '" + flag + "'")
                self.sendLine("Try 'uname --help' for more information.")
                return
            return

    def exit_command(self, arguments=[]):
        self.transport.loseConnection()
        return

    def displayMessageOfDay(self):
        self.sendLine("\r\nWelcome to Ubuntu 11.10 (GNU/Linux 3.0.0-12-generic i686)\r\n")
        self.sendLine("\r\n* Documentation https://help.ubuntu.com/\r\n")
        self.sendLine("\r\n278 packages can be updated.\r\n71 updates are security updates.\r\n")
        self.sendLine("\r\nThe programs included with the Ubuntu system are free software:")
        self.sendLine("the exact distribution terms for each program are described in the")
        self.sendLine("individual files in /usr/share/doc/*/copyright.\r\n")
        self.sendLine("Ubuntu comes with ABSOLUTELY NO WARRANTY, the extent permitted by\r\napplicable law.")
        #file = open("./content/motd")
        #for line in file:
        #    self.transport.write(line)
        return

    def showPrompt(self):
        prompt = "\r\nroot@servermachine:~$ "
        self.transport.write(prompt)
        return

    def logMetadata(self):
        #MySQL
        fp = open("dbPassword.txt", "r")
        dbPass = fp.readline()
        dbPass = dbPass.rstrip('\n')
        fp.close()

        #Firebase
        fpFb = open("fbkey.txt", "r")
        fbKey = fpFb.readline()
        fbKey = fbKey.rstrip('\n')
        fpFb.close()
        self.attackerNum += 1;

        self.ipAddr = self.transport.getPeer().address.host
        self.logFolder = self.ipAddr + '-' + str(self.sessionNum) + '-commands.txt'
        while (os.path.isfile("/opt/tomcat/webapps/ActiveHoneypotWeb/logfiles/"+self.logFolder)):
            self.sessionNum+=1
            self.logFolder = self.ipAddr +'-'+str(self.sessionNum)+'-commands.txt'

        access = datetime.now()
        accessTime = str(access.hour) + ":" + str(access.minute) + ":" + str(access.second)
        accessDate = str(access.year) + "/" + str(access.month) + "/" + str(access.day)

        URL = 'http://ip-api.com/json/'+self.ipAddr
        PARAMS = {'fields':'57597'}
        r = requests.get(url = URL, params = PARAMS)
        data = r.json()
        status = data['status']
        lat = lon = ""
        print(data)
        if(status != 'fail'):
            city = data['city']
            country = data['country']
            state = data['regionName']
            lat = str(data['lat'])
            lon = str(data['lon'])

            #Insert to Database
            db = MySQLdb.connect("activehoneypot-instance1.c6cgtt72anqv.us-west-2.rds.amazonaws.com", "ahpmaster", dbPass, "activehoneypotDB")
            cursor = db.cursor()
            sql = "INSERT INTO `activehoneypotDB`.`attacker` (`ip_address`, `username`, `passwords`, `time_of_day_accessed`, `logFile`, `sessions`, `country`, `city`, `state`, `date_accessed`, `latitude`, `longitude`) VALUES ('%s', '%s','%s', '%s', '%s','%s', '%s','%s', '%s', '%s','%s', '%s')"% (self.ipAddr, 'root', 'password', accessTime, self.logFolder, self.sessionNum, country, city, state, accessDate, lat, lon);

            try: #Execute SQL command
                cursor.execute(sql)
                db.commit()
                print("Commit logMetadata")
            except:
                db.rollback()
                print("Can't Commit logMetadata")
            db.close()

            fbConfig = {'apiKey': fbKey, 'authDomain': 'honeypot-1c941.firebaseapp.com', 'databaseURL': 'https://honeypot-1c941.firebaseio.com', 'storageBucket': 'honeypot-1c941.appspot.com'}
            fb = pyrebase.initialize_app(fbConfig)
            fddb = fb.database()
            data = {"attackerID": self.attackerNum, "ip_address": self.ipAddr, "username": "root", "passwords": "password", "time_of_day_accessed": accessTime, "logFile": self.logFolder, "sessions": self.sessionNum, "country": country, "city": city, "state": state , "date_accessed": accessDate, "latitude": lat, "longitude": lon}
            fddb.child("attacks").push(data)
       
        elif(data['message'] == 'private range'):
            db = MySQLdb.connect("activehoneypot-instance1.c6cgtt72anqv.us-west-2.rds.amazonaws.com", "ahpmaster", dbPass, "activehoneypotDB")
            cursor = db.cursor()
            sql = "INSERT INTO `activehoneypotDB`.`attacker` (`ip_address`, `username`, `passwords`, `time_of_day_accessed`, `logFile`, `sessions`,`country`, `date_accessed`) VALUES ('%s', '%s','%s', '%s', '%s','%s', '%s', '%s')"% (self.ipAddr, 'root', 'password', accessTime, self.logFolder, self.sessionNum, "localhost",  accessDate);


            fbConfig = {'apiKey': fbKey, 'authDomain': 'honeypot-1c941.firebaseapp.com', 'databaseURL': 'https://honeypot-1c941.firebaseio.com', 'storageBucket': 'honeypot-1c941.appspot.com'}
            fb = pyrebase.initialize_app(fbConfig)
            fbdb = fb.database()
            data = {"attackerID": self.attackerNum, "ip_address": self.ipAddr, "username": "root", "passwords": "password", "time_of_day_accessed": accessTime, "logFile": self.logFolder, "sessions": self.sessionNum, "date_accessed": accessDate}
            fbdb.child("attacks").push(data)

            try: #Execute SQL command
                cursor.execute(sql)
                db.commit()
                print("Commit logMetadata")
            except:
                db.rollback()
                print("Can't Commit logMetadata")
            db.close()

        else:
            print("Can't Commit logMetadata because ", data['message'], ".") 

class HoneypotSession(object):
    def __init__(self, avatar):
        pass
    #def getPty(self, terminal, windowSize, attrs):
        #pass
    def execCommand(self, proto, cmd):
        raise Exception("Remote command execution mode is disabled.")

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

class HoneypotPasswordAuth(FilePasswordDB):
    pass

def honeypotHashFunction(username, passwordFromNetwork, passwordFromFile):
    #print("Username: " + username.decode("utf-8"))
    #print("Network Given Password: "+ passwordFromNetwork.decode("utf-8"))

    if((passwordFromNetwork.decode("utf-8"))!=(passwordFromFile.decode("utf-8"))):
        file = open('failedpasswordattempts', "a+")
        file.write(username.decode("utf-8")+":"+passwordFromNetwork.decode("utf-8")+"\n")
        file.close()

        #INSERT to database
        fp = open("dbPassword.txt", "r")
        dbPass = fp.readline()
        dbPass = dbPass.rstrip('\n')
        fp.close()
        access = datetime.now()
        accessTime = str(access.hour) + ":" + str(access.minute) + ":" + str(access.second)
        accessDate = str(access.year) + "/" + str(access.month) + "/" + str(access.day)

        print("tryingToOpenDb")
        db = MySQLdb.connect("activehoneypot-instance1.c6cgtt72anqv.us-west-2.rds.amazonaws.com", "ahpmaster", dbPass, "activehoneypotDB")
        cursor = db.cursor()
        sql = "INSERT INTO `activehoneypotDB`.`login_attempts` (`usernames`, `passwords`, `usernames_passwords`, `time_access`, `date_access`) VALUES ('%s','%s', '%s', '%s','%s')"% ( username.decode("utf-8"), passwordFromNetwork.decode("utf-8"), username.decode("utf-8")+":"+passwordFromNetwork.decode("utf-8"), accessTime, accessDate);

        try: #Execute SQL command
           cursor.execute(sql)
           db.commit()

        except MySQLdb.Error as e:
           print(e)
        except:
           print("can't execute passwords INSERT")
           db.rollback() 
        ipAddr = "0.0.0.0" 
        sql2 = "INSERT INTO `activehoneypotDB`.`attacker` (`ip_address`, `username`, `passwords`, `time_of_day_accessed`, `logFile`, `date_accessed`) VALUES ('%s', '%s', '%s','%s', '%s','%s')"% (ipAddr, username.decode("utf-8"), passwordFromNetwork.decode("utf-8"), accessTime, "notLoggedIn.txt", accessDate);

        #Firebase
        fp = open("fbkey.txt", "r")
        fbKey = fp.readline()
        fbKey = fbKey.rstrip('\n')
        fp.close()
        
        fbConfig = {'apiKey': fbKey, 'authDomain': 'honeypot-1c941.firebaseapp.com', 'databaseURL': 'https://honeypot-1c941.firebaseio.com', 'storageBucket': 'honeypot-1c941.appspot.com'}
        fb = pyrebase.initialize_app(fbConfig)
        fbdb = fb.database()
        data = { "ip_address": ipAddr, "username": username.decode("utf-8"), "passwords": passwordFromNetwork.decode("utf-8"), "time_of_day_accessed": accessTime, "logFile": "notLoggedIn.txt", "country": country, "city": city, "state": state , "date_accessed": accessDate}
        fbdb.child("attacks").push(data)

        try: #Execute SQL command
           cursor.execute(sql2)
           db.commit()
           print("Commit sql2")
        except:
           db.rollback()
           print("Can't Commit sql2")
        db.close()

    return passwordFromNetwork

class FileSystem(object):
    def __init__(self):
        self.filesys = tempfs.TempFS()
       
        #dirs = ["bin", "boot", "cdrom", "dev", "etc", "home", "lib", "lib64", "lost+found", "media", "mnt", "opt", "root", "run", "sbin", "snap", "srv", "sys", "tmp", "usr", "var"]
        dirs = ["etc", "boot"] # smaller filesystem for demo, also we should not load /home/ as that has our ssh keys and stuff

        for my_dir in dirs:
           my_fs = OSFS("/"+ my_dir)
           try:
              fs.copy.copy_fs(my_fs, self.filesys.makedir("/"+my_dir+"/"), walker=None, on_copy=None)
              print("dir: " + my_dir + " created")
           except:
              print("EXCEPTION: " + my_dir)
           #self.filesys.tree()

        #pointer = self.filesys.open("/newfile","w+")
        #pointer.write("Contents of a file.\r\n")
        #pointer.close()
        
        self.filesys.makedir("/home")
        pointer = self.filesys.open("/home/notes","w+")
        pointer.write("my username for email is bob, my password for email is password")
        pointer.close()

        print("File tree initalized:\r\n")
        self.filesys.tree()

portal = portal.Portal(HoneypotRealm())
filesys = FileSystem()
passwdfile = HoneypotPasswordAuth("passwords", hash=honeypotHashFunction)
portal.registerChecker(passwdfile)
factory = HoneypotFactory()
factory.portal = portal

reactor.listenTCP(2222, factory)  # Open TCP port using specified factory to handle connections.
reactor.listenTCP(2223, factory, interface="::") # Listen on this port for IPV6 interfaces (RaspPi direct network support)
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
