import socket
import select
import errno
import sys
import platform

''' Texas Hold'em Poker client application written by Mattias Lamotte in May 2020
This Poker client application runs on Python 3.x on Windows, Macs and iPads/iPhones (running
on Pythonista 3). If running on Pythonista 3, you need to clear the console cache every 45-60
minutes, or the console cache will eventually be so large that the application crashes (there's 
a clear button on upper right of pythonista console window). The Server and ReadMe files can be
downloaded on google drive: http://github.com/mattiaslamotte/retropoker

To run this client, you can either run the client.exe file in the google folder above, or run this
script after installing python 3.5+ on https://www.python.org/downloads/.

While running the .exe file will give you all kinds of security warnings as I'm not a vetted
Apple developper, it will allow you to avoid having to install Python on that machine.

On Macs, the security warnings can be bypassed by doing CTRL-double click on the application. On the
PC, i have a video in the google drive folder showing how to install the server on a virtual server.
'''
print('***********************************************************************')
print('                  ****   *****  *****  ****     ***                    ')
print('                  *   *  *        *    *   *   *   *                   ')
print('                  ****   ****     *    ****    *   *                   ')
print('                  *  *   *        *    *  *    *   *                   ')
print('                  *   *  *****    *    *   *    ***                    ')
print('                                                                       ')
print('                  ****    ***   *   *  *****   ****                    ')
print('                  *   *  *   *  *  *   *       *   *                   ')
print('                  ***    *   *  ***    ****    ****                    ')
print('                  *      *   *  *  *   *       *   *                   ')
print('                  *       ***   *   *  *****   *   *                   ')
print('***********************************************************************')
print(' ')
HEADER_LENGTH = 10

PORT =1235
#print('Unless you have installed your own RetroPoker server, ignore the server IP')
#print('address prompt below. Just press enter to use the default poker server on')
#print('IP address 52.175.53.52')
print('If the server is busy with a game you will need to wait for 5 minutes of inactivity')
print('to be able to start a game with up to 6 people anywhere in the world.')
print('')
'''
IP = input("Server IP address?: ")
if len(IP)==0: #if playing multiple games or testing, it's useful to avoid multiple entry of IP address
    # default IP to be edited every time public/local IP of server changes
    # Mattias Lamotte is providing a public testing server on 52.175.53.52 '''
IP = "52.175.53.52" #"127.0.0.1"
#print("The default testing public server will be used...")

my_username = input("Username: ")
#connection begins immediately after username entry
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP,PORT))
client_socket.setblocking(False)
print("should be connected?")

class Player: #used to display publicly visible info for each player.
    def __init__(self,playerName,playerID):
        #all values below are just placeholders. All values are dictated by server.
        self.playerName = playerName
        self.playerID = playerID
        self.dollarWallet = 1000
        self.wins = 0 # now used to track wins (originally thought I was using this real estate to track BuyIns)
        self.status = "waiting"
    #def getName(self,playerID):

#numpy was quadrupling the size of .exe file so I decided to cut it by replicating np.roll
def rolling(theList, quantity):
    quantity *= -1  # allows to mimick numpy.roll - not same behavior as reversing < > signs below
    if quantity > 0:  # may have to switch
        tempList = theList[:quantity]
        theList = theList[quantity:]
        theList = theList + tempList
        return theList
    elif quantity < 0:
        tempList = theList[quantity:]
        theList = theList[:quantity]
        theList = tempList + theList
    return theList  # no matter what, 0 included

class Display: #creation of overall display object which contains player objects.
    def __init__(self,totalPlayers):
        self.playerList = []
        self.activePlayer = 0 #placeholder
        self.yourPlayerID = -1 #placeholder
        self.potSize = 0
        self.commonCards = "XX XX XX XX XX "
        self.totalPlayers = totalPlayers
        self.myCards = 'XX XX ' # 2 personal cards displayed at bottom of table
        self.myHand = '' # 2 Pair, 4 of a Kind etc
        self.toggle = 1 #used to change suit colors on macs and iPads



    def printTable(self):
        #playerList stays static but we need to roll table to ensure this player is always shown on bottom
        player=[]
        BI=[]
        wallet=[]
        status=[]
        for playerx in self.playerList:
            player.append(playerx.playerName)
            BI.append(playerx.wins)
            wallet.append(playerx.dollarWallet)
            status.append(playerx.status)
        #Player with cursor goes in caps with brackets for easy spotting
        player[self.activePlayer] = "< "+ player[self.activePlayer].upper() + " >"
        #roll the table so that player/client always appears at bottom of table
        roll = -self.yourPlayerID
        player = rolling(player,roll)
        BI = rolling(BI,roll)
        wallet = rolling(wallet,roll)
        status = rolling(status,roll)
    #create the display table to adjust to the number of players
        if len(player) < 6:
            p5ln1 = ""
            p5ln2 = ""
        else:
            p5ln1 = f"{player[5]}({BI[5]})"
            p5ln2 = f"{status[5]} ($={wallet[5]})"

        if len(player) < 5:
            p4ln1 = ""
            p4ln2 = ""
        else:
            p4ln1 = f"{player[4]}({BI[4]})"
            p4ln2 = f"{status[4]} ($={wallet[4]})"

        if len(player) < 4:
            p3ln1 = ""
            p3ln2 = ""
        else:
            p3ln1 = f"{player[3]}({BI[3]})"
            p3ln2 = f"{status[3]} ($={wallet[3]})"
        if len(player) < 3:
            p2ln1 = ""
            p2ln2 = ""
        elif len(player)<5:
            p2ln1 = f"{player[2]}({BI[2]}) ($={wallet[2]})"
            p2ln2 = f"{status[2]} "
        else:
            p2ln1 = f"{player[2]}({BI[2]})"
            p2ln2 = f"{status[2]}($={wallet[2]})"

        #unfortunately uniform characters are displayed differently on Windows and Macs
        #the server therefore sends suits in plain characters and clients translate these suits
        #to the correct uniform characted for that platform
        def replaceWin(string): #for windows 7
            string = string.replace('spades',chr(6))
            string = string.replace('hearts',chr(3))
            string = string.replace('clubs', chr(5))
            string = string.replace('diamonds', chr(4))
            return string
        #transform suits for macs and iPads
        def replaceMac1(string):  #Light colored suits - Can be harder to read
            string = string.replace('spades', u'\u2664')
            string = string.replace('hearts', u'\u2661')
            string = string.replace('clubs', u'\u2667')
            string = string.replace('diamonds', u'\u2662')
            return string
        def replaceMac2(string): #smaller darker suit symbols - default for macs and windows 10
            string = string.replace('spades', u'\u2660')
            string = string.replace('hearts', u'\u2665')
            string = string.replace('clubs', u'\u2663')
            string = string.replace('diamonds', u'\u2666')
            return string
        if platform.system() == "Windows": #Unicode works won windows 10
            if platform.platform()[8] == '7': #means it's either windows 7 or 70!
                self.commonCards = replaceWin(self.commonCards)
                display.myCards = replaceWin(display.myCards)
            else: #we presume it's windows 10 or newer
                self.commonCards = replaceMac2(self.commonCards)
                display.myCards = replaceMac2(display.myCards)
        elif display.toggle == 1: #Macs and iPads
            self.commonCards = replaceMac2(self.commonCards)
            display.myCards = replaceMac2(display.myCards)
        else: #toggle == -1
            self.commonCards = replaceMac1(self.commonCards)
            display.myCards = replaceMac1(display.myCards)

    #2 different set-up. 1 table up to 4 players and 1 table for 5 or 6 players
        if len(player) < 5: #2-4 player table
            print('***********************************************************************')
            print(f'                        {p2ln1}')#'{player[2]}({BI[2]}) (w={wallet[2]} )')
            print(f'                                {p2ln2}')#'{status[2]}')
            print('')
            print(f'                            Total POT= ${self.potSize}                  ')
            print(f'{player[1]}({BI[1]})              {self.commonCards}                      {p3ln1}')
            print(f'($={wallet[1]}). {status[1]}                                       {p3ln2}')
            print('')
            print(f'                            {status[0]}')
            print(f'                           {player[0]}({BI[0]}) ($={wallet[0]})')
            print(f'                           {display.myCards} ({display.myHand})')
            print('***********************************************************************')
        else: # 5-6 player table
            print('***********************************************************************')
            print(f'{p2ln1}              {p3ln1}                  {p4ln1}')
            print(f' {p2ln2}             {p3ln2}               {p4ln2}')
            print('')
            print(f'                            Total POT= ${self.potSize}                  ')
            print(f'{player[1]}({BI[1]})              {self.commonCards}                        {p5ln1}')
            print(f'($={wallet[1]}). {status[1]}                                        {p5ln2}')
            print('')
            print(f'                            {status[0]}')
            print(f'                           {player[0]}({BI[0]}) ($={wallet[0]})')
            print(f'                           {display.myCards} ({display.myHand})')
            print('***********************************************************************')

#helper function to parse through each data variable sent
def getInfo():
    requestString_header = client_socket.recv(HEADER_LENGTH)
    requestString_length = int(requestString_header.decode("utf-8").strip())
    requestString = client_socket.recv(requestString_length).decode("utf-8")
    return requestString


username = my_username.encode("utf-8")
username_header = f"{len(username):<{HEADER_LENGTH}}".encode("utf_8")
#***** Data starts being sent here
client_socket.send(username_header + username)

#key flag to launch input request on client. Prompt is assigned by turn based system run by server
newRequest = False #when true, the prompt appears on that client

while True:
    if newRequest:
        print(requestString) #request string sent by server (like "C)all, F)old, R)aise?")
        message = input(f"{my_username} >")
        if len(message) == 0:
            message = " "
        if message == "toggle" or message == "TOGGLE":
            display.toggle *= -1
            print("suits have been toggled - will start appearing differently")
            display.printTable()
        if message:
            message = message.encode("UTF_8")
            message_header = f"{len(message):<{HEADER_LENGTH}}".encode("utf_8")
            client_socket.send(message_header + message)
        newRequest = False #otherwise input box comes back everytime
    try:
        while True:
            #receive things from the server
            instruction_header = client_socket.recv(HEADER_LENGTH)
            if not len(instruction_header): #connection is closed
                print("connection closed by the server")
                sys.exit()
                
            instruction_length = int(instruction_header.decode("utf-8").strip())
            instruction = client_socket.recv(instruction_length).decode("utf-8")
            
            if instruction == "PRINT": #used for receiving printLn. Server can send any info to be printed on client
                print(getInfo())
                #print("printed")
            
            if instruction == "REQUEST": #same as above but sends client cursor. needs response...
                
                requestString = getInfo()
                newRequest = True  #this simply creates the input box on next loop so user can respond

            #Sqwak is a sepearte instruction that only sends client specific info that other players must not see
            #makes it impossible to manifuplate client source code to see other players' cards
            if instruction == "SQWAK": #sent regularly to update player/client's card and hand
                display.yourPlayerID = int(getInfo())
                display.myCards = getInfo()
                display.myHand = getInfo()


            # sent to update on non-player specific info and re-prints table
            if instruction == "UPDATETABLE": #single send per turn
                #totalPlayers = getInfo()
                display.potSize = int(getInfo())
                display.commonCards = getInfo()
                display.activePlayer = int(getInfo()) #where cursor currently is -should be in Bold

                display.printTable()

            # sent to update each player's specific info (inc other players)
            if instruction == "UPDATEPLAYER": # n player send per turn
                
                playerID = int(getInfo())
                display.playerList[playerID].dollarWallet = int(getInfo())
                display.playerList[playerID].wins = int(getInfo())
                display.playerList[playerID].status = getInfo()

            # used at beginning to launch the poker table once all players have joined
            if instruction == "SETUP":
                totalPlayers = int(getInfo())
                display = Display(totalPlayers)
                for count in range(totalPlayers):
                    #only item is playerName
                    playerName = getInfo()
                    print("adding " + playerName)
                    display.playerList.append(Player(playerName, count)) #playerID and name are added here
                #should be followed by immediate UPDATE
                print("setup completed")

    #You want to ignore all IOerrors except for socket reading errors
    except IOError as e:
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            print('Reading error',str(e))
            sys.exit(exit)
        continue

    #all general errors will cause the program to fail anyway so you might just as well end the pain!
    except Exception as e:
        print('General error',str(e))
        sys.exit()
        pass
