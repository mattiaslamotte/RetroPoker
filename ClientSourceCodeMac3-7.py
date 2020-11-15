import socket
import select
import errno
import sys
import platform
import threading
import queue
import time

''' Texas Hold'em Poker client application written by Mattias Lamotte in May 2020
This Poker client application runs on Python 3.x on Windows, Macs and iPads/iPhones (running
on Pythonista 3). If running on Pythonista 3, you need to clear the console cache every 45-60
minutes, or the console cache will eventually be so large that the application crashes (there's 
a clear button on upper right of pythonista console window). The Server and ReadMe files can be
downloaded on google drive: 
https://drive.google.com/drive/folders/1LJoqfU47_05zRQ3HesHfKktzzqlI_I29?usp=sharing
To run this client, you can either run the client.exe file in the google folder above, or run this
script after installing python 3.x on https://www.python.org/downloads/.

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
print('                         by Mattias Lamotte')
print(' ')
print('Starting Instructions: The game launches after the username is entered. 8 players at a time can join a game. One player should hold off'+
      ' from pressing the buttons until all the other players have joined. The game starts after all players have pressed a button to acknowledge they are ready to start.')
print('')

print('New players cannot join after the game is launched. The server resets after 5 minutes of inactivity. In the event the game needs to be restarted, close clients and just wait for 5mins.')
print('')
print('Entering the code "9876" in the betting amount box puts that player in "Auto-Fold" mode. This is usefull if one of the players needs to take a break without disrupting the game flow for the other players.')
print('')
print('Maximum bet and raise is set to $1000. Each player starts with $10,000. Game ends after either preset amount of time or when 1st player goes bust.')
print('')




HEADER_LENGTH = 10

PORT =1235

#IP = input("What is the server IP address? (leave blank for default): ")
#if len(IP)==0: #if playing multiple games or testing, it's useful to avoid multiple entry of IP address
    # default IP to be edited every time public/local IP of server changes
    # Mattias Lamotte is providing a public testing server on 52.175.53.52
IP = "52.175.53.52" #"127.0.0.1" #CHANGE THIS IP ADDRESS IF YOU ARE RUNNING YOUR OWN SERVER
    #print("The default testing public server will be used...")

my_username = input("Username: ")

print(" ")
print("     LEAVE THIS WINDOW OPEN OR THE WHOLE GAME WILL TERMINATE ")
#connection begins immediately after username entry


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
    def __init__(self):
        self.playerList = []
        self.activePlayer = 0 #placeholder
        self.yourPlayerID = -1 #placeholder
        self.potSize = 0
        self.commonCards = "XX XX XX XX XX "
        self.totalPlayers = 2
        self.myCards = 'XX XX ' # 2 personal cards displayed at bottom of table
        self.myHand = '' # 2 Pair, 4 of a Kind etc
        self.toggle = 1 #used to change suit colors on macs and iPads
        self.mainText = "" #used to append stuff to main window
        self.newRequest = True #used to make sure that the player realises that it's there turn
        self.phase = 1 #P)ass,Fold, Bet is 1 / F)old, Call, Raise is 2
    # helper function to parse through each data variable sent


'''
def main():
    
    # key flag to launch input request on client. Prompt is assigned by turn based system run by server
    

    while True:
        
        #these are now going to be in the GUI
        if newRequest:

            print(requestString)  # request string sent by server (like "C)all, F)old, R)aise?")
            theText.insert(END, requestString + "\n")
            message = input(f"{my_username} >")
            if len(message) == 0:
                message = " "
            
            if message:
                message = message.encode("UTF_8")
                message_header = f"{len(message):<{HEADER_LENGTH}}".encode("utf_8")
                client_socket.send(message_header + message)
            newRequest = False  # otherwise input box comes back everytime
        try:
            
'''
        


#############  GUI STARTS HERE #####################

class Goui:
    def __init__(self,root,queue,socket,display):
        self.queue = queue
        self.root= root
        self.socket = socket
        self.display = display
        fontStyleP0 = tkFont.Font(family='Arial', size=16)
        fontStylePlayers = tkFont.Font(family='Arial', size=13)
        fontStylePot = tkFont.Font(family='Arial', size=16)
        
        #All the GUI comes below here
        root.title('Retro Poker')
        root.geometry('750x600')
        
        topFrame = Frame(root,borderwidth=1)
        topFrame.pack(side=TOP,pady=10)
        midFrame = LabelFrame(root,text="Main Poker Table", borderwidth=2,width=680)
        midFrame.pack(side=TOP,pady=10)
        #midFrame.place(x=10, y=10, anchor="nw")
        #placeHolder10
        #placeHolder10= Label(midFrame,width=1,height=1,bg="red")
        #placeHolder10.grid(column=1,row=0,padx=1,pady=1)
        self.labelp2 = Label(midFrame, text="", font=fontStylePlayers, width =14, height=5)
        self.labelp2.grid(column=1,row=1,columnspan= 2, rowspan=2, padx=1, pady=1)
        #placeHolder13= Label(midFrame,width=1,height=1,bg="red")
        #placeHolder13.grid(column=1,row=3,padx=1,pady=1)
        self.labelp1 = Label(midFrame, text="", font=fontStylePlayers, width =14, height=10) #P1 below P2
        self.labelp1.grid(column=1,row=4,columnspan= 2, rowspan=2, padx=1, pady=1)
        #placeHolder16= Label(midFrame,width=1,height=1,bg="red")
        #placeHolder16.grid(column=1,row=6,padx=1,pady=1)
        #pot column
        #placeHolder30= Label(midFrame,width=1,height=1,bg="red")
        #placeHolder30.grid(column=3,row=0,padx=1,pady=1, sticky="NW")
        self.labelp3 = Label(midFrame, text="", font=fontStylePlayers, width =14, height=5) #P1 below P2
        self.labelp3.grid(column=3,row=1,columnspan= 1, rowspan=2, padx=0, pady=1)
        self.labelp4 = Label(midFrame, text="", font=fontStylePlayers, width =14, height=5) #P1 below P2
        self.labelp4.grid(column=4,row=1,columnspan= 1, rowspan=2, padx=0, pady=1)
        self.labelp5 = Label(midFrame, text="", font=fontStylePlayers, width =14, height=5) #P1 below P2
        self.labelp5.grid(column=5,row=1,columnspan= 1, rowspan=2, padx=0, pady=1)
        #setup pot frame label (where frame will fit later)
        self.potLbl = Label(midFrame, text="Poker Table\n\nOne player should holdout from pressing buttons\nuntil all the joining players can see this Poker Table", font=fontStylePot, width =46, height=10,bg="gainsboro") #P1 below P2
        self.potLbl.grid(column=3,row=3,columnspan= 3, rowspan=3, padx=1, pady=1)
        self.labelp0 = Label(midFrame, text="Game will start when every player\nhas pressed on buttons below", font=fontStyleP0, width =35, height=5, anchor='n') #P0 below Pot
        self.labelp0.grid(column=3,row=6,columnspan= 3, rowspan=3, padx=1, pady=4)
        #right most column
        #placeHolder60= Label(midFrame,width=1,height=1,bg="red")
        #placeHolder60.grid(column=6,row=0,padx=1,pady=1, sticky="NW")
        self.labelp6 = Label(midFrame, text="", font=fontStylePlayers, width =14, height=5) #P1 below P2
        self.labelp6.grid(column=6,row=1,columnspan= 2, rowspan=2, padx=1, pady=1)
        self.labelp7 = Label(midFrame, text="", font=fontStylePlayers, width =14, height=10) #P1 below P2
        self.labelp7.grid(column=6,row=3,columnspan= 3, rowspan=2, padx=1, pady=1)
        
        
        
        theText = ""  #A huge amount of garbage that could never properly fit on a line A huge amount of garbage that could never properly fit on a line "
        mainScroll= Scrollbar(topFrame)
        self.mainText = Text(topFrame, height=6, width=85)
        self.mainText.pack(side=LEFT)#,fill=Y)
        mainScroll.pack(side=RIGHT)
        mainScroll.config(command=self.mainText.yview)
        self.mainText.config(yscrollcommand=mainScroll.set)
        self.mainText.insert(END, theText + theText)
        self.mainText.see(END) #pushes text cursor to end so it displays bottom of box (may have to be repeated).
        #Last Frame starts here
        bottomFrame = Frame(root,borderwidth=1)
        bottomFrame.pack(side=TOP,pady=10)
        
        self.FoldBtn = Button(bottomFrame,text="Fold",command=self.foldClick, width =10, border=3, padx = 5)
        self.FoldBtn.grid(column=0,row=0)
        invislabel1 = Label(bottomFrame, width =2, height=1)
        invislabel1.grid(column=1,row=0, padx=1, pady=1)
        self.passCallBtn = Button(bottomFrame,text="Call", command=self.passCallClick, width =10, border=3, padx = 5)
        self.passCallBtn.grid(column=2,row=0)
        invislabel2 = Label(bottomFrame, width = 20, height=1) #distance between Bet/raise button and others
        invislabel2.grid(column=3,row=0, padx=1, pady=1)
        self.betRaiseBtn = Button(bottomFrame,text="Bet", command=self.betRaiseClick, width =10, border=3, padx = 5)
        self.betRaiseBtn.grid(column=4,row=0)
        invislabel3 = Label(bottomFrame, width =2, height=1)
        invislabel3.grid(column=5,row=0, padx=1, pady=1)
        self.betVar = StringVar()
        self.betVar.set("20")
        self.betEntry = Entry(bottomFrame,textvariable=self.betVar, width=7, relief=SUNKEN, justify=CENTER, border=3)
        self.betEntry.grid(column=6,row=0, padx=1,pady=1)
        
        self.labelList = [self.labelp0,
                          self.labelp1,
                          self.labelp2,
                          self.labelp3,
                          self.labelp4,
                          self.labelp5,
                          self.labelp6,
                          self.labelp7] 
#############  GUI ends HERE #####################
    #outward bound messages can only be sent when server is waiting for signal
    def foldClick(self):
        if self.display.newRequest:
            message='fold'
            message = message.encode("UTF_8")
            message_header = f"{len(message):<{HEADER_LENGTH}}".encode("utf_8")
            self.socket.send(message_header + message)
            #need to consider that continually pressing button may skip turn
            #may need: if self.display.newRequest = True then it becomes False
            self.display.newRequest = False
        
    def passCallClick(self):
        if self.display.newRequest:
            if self.display.phase == 1:
                message = 'pass'
            else: message = 'call'
            message = message.encode("UTF_8")
            message_header = f"{len(message):<{HEADER_LENGTH}}".encode("utf_8")
            self.socket.send(message_header + message)
            self.display.newRequest = False
    
    def betRaiseClick(self):
        if self.display.newRequest:
            if self.display.phase == 1:
                message = 'bet'+ str(self.betVar.get())
            else: message = 'raise' + str(self.betVar.get())
            message = message.encode("UTF_8")
            message_header = f"{len(message):<{HEADER_LENGTH}}".encode("utf_8")
            self.socket.send(message_header + message)
            if int(self.betVar.get()) < 1001:
                self.display.newRequest = False
    
    def clearActivePlayer(self):
        for label in self.labelList:
            label['bg'] = root.cget('bg') #'#f0f0f0'
            
    def setActivePlayerFlag(self,playerMappingList,activePlayerList):
        #first get activePlayerList index - where there's a true value
        index = activePlayerList.index(1)
        self.labelList[playerMappingList[index]]['bg'] ='#f7f7f7'
        #iterate through labels - should really map this just once with dict
        #for label,count in zip(self.labelList, range(len(self.labelList))):
            #if count == index:
                #self.labelList[index]['bg'] ='#f7f7f7'
        
    def printTable(self):
        #playerList stays static but we need to roll table to ensure this player is always shown on bottom
        player=[]
        BI=[]
        wallet=[]
        status=[]
        activePlayerList=[]
        for playerx in self.display.playerList:
            player.append(playerx.playerName)
            BI.append(playerx.wins)
            wallet.append(playerx.dollarWallet)
            status.append(playerx.status)
            activePlayerList.append(0)
        #Player with cursor goes in caps with brackets for easy spotting
        #player[self.display.activePlayer] = "< "+ player[self.display.activePlayer].upper() + " >"
        activePlayerList[self.display.activePlayer] = 1 #tracks which player is active
        #roll the table so that player/client always appears at bottom of table
        roll = -self.display.yourPlayerID
        player = rolling(player,roll)
        BI = rolling(BI,roll)
        wallet = rolling(wallet,roll)
        status = rolling(status,roll)
        activePlayerList = rolling(activePlayerList,roll)
        
        
            
        #unfortunately uniform characters are displayed differently on Windows and Macs
        #the server therefore sends suits in plain characters and clients translate these suits
        #to the correct uniform characted for that platform
        def replaceWin(string): #for windows 7
            string = string.replace('spades',' '+ chr(6))
            string = string.replace('hearts',' '+ chr(3))
            string = string.replace('clubs', ' '+ chr(5))
            string = string.replace('diamonds',' '+  chr(4))
            return string
        #transform suits for macs and iPads
        def replaceMac1(string):  #Light colored suits - Can be harder to read
            string = string.replace('spades', ' '+ u'\u2664')
            string = string.replace('hearts', ' '+ u'\u2661')
            string = string.replace('clubs', ' '+ u'\u2667')
            string = string.replace('diamonds', ' '+ u'\u2662')
            return string
        def replaceMac2(string): #smaller darker suit symbols - default for macs and windows 10
            string = string.replace('spades', ' '+ u'\u2660')
            string = string.replace('hearts', ' '+ u'\u2665')
            string = string.replace('clubs', ' '+ u'\u2663')
            string = string.replace('diamonds', ' '+ u'\u2666')
            return string
        '''
        if platform.system() == "Windows": #Unicode works won windows 10
            if platform.platform()[8] == '7': #means it's either windows 7 or 70!
                self.display.commonCards = replaceWin(self.display.commonCards)
                self.display.myCards = replaceWin(self.display.myCards)
            else: #we presume it's windows 10 or newer
                self.display.commonCards = replaceMac2(self.display.commonCards)
                self.display.myCards = replaceMac2(self.display.myCards)
        elif display.toggle == 1: #Macs and iPads
            self.display.commonCards = replaceMac2(self.display.commonCards)
            self.display.myCards = replaceMac2(self.display.myCards)
        else: #toggle == -1 '''
        self.display.commonCards = replaceMac2(self.display.commonCards)
        self.display.myCards = replaceMac2(self.display.myCards)
        #debug
        #self.labelp6['text']:'newRequest \n' + str(self.display.newRequest) +'\n' + str(self.display.phase)
               
        #setting layout here
        self.clearActivePlayer() #clears all the colors on player labels
        playerMappingList = []
        self.potLbl['text'] = f'Total POT= ${self.display.potSize} \n \n {self.display.commonCards}'
        self.labelp0['text'] = f'{status[0]} \n {player[0]}({BI[0]}) ($={wallet[0]}) \n\n {self.display.myCards} ({self.display.myHand})'
        self.labelp1['text'] = f'{player[1]}({BI[1]}) \n ($={wallet[1]})\n {status[1]}'
        playerMappingList.append(0)
        playerMappingList.append(1)
        if len(player) < 5: #2-4 player table
            if len(player)>2:
                self.labelp4['text'] = f'{player[2]}({BI[2]}) \n ($={wallet[2]})\n {status[2]}'
                playerMappingList.append(4)
            if len(player)>3:
                self.labelp7['text'] = f'{player[3]}({BI[3]}) \n ($={wallet[3]})\n {status[3]}'
                playerMappingList.append(7)
        elif len(player) > 6:
            self.labelp2['text'] = f'{player[2]}({BI[2]}) \n ($={wallet[2]})\n {status[2]}'
            self.labelp3['text'] = f'{player[3]}({BI[3]}) \n ($={wallet[3]})\n {status[3]}'
            self.labelp4['text'] = f'{player[4]}({BI[4]}) \n ($={wallet[4]})\n {status[4]}'
            self.labelp5['text'] = f'{player[5]}({BI[5]}) \n ($={wallet[5]})\n {status[5]}'
            playerMappingList.append(2)
            playerMappingList.append(3)
            playerMappingList.append(4)
            playerMappingList.append(5)
            if len(player) ==8:
                self.labelp6['text'] = f'{player[6]}({BI[6]}) \n ($={wallet[6]})\n {status[6]}'
                self.labelp7['text'] = f'{player[7]}({BI[7]}) \n ($={wallet[7]})\n {status[7]}'
                playerMappingList.append(6)
                playerMappingList.append(7)
            else: 
                self.labelp7['text'] = f'{player[6]}({BI[6]}) \n ($={wallet[6]})\n {status[6]}'
                playerMappingList.append(7)
        else: #5 or 6 players
            self.labelp3['text'] = f'{player[2]}({BI[2]}) \n ($={wallet[2]})\n {status[2]}'
            self.labelp4['text'] = f'{player[3]}({BI[3]}) \n ($={wallet[3]})\n {status[3]}'
            playerMappingList.append(3)
            playerMappingList.append(4)
            if len(player)== 6:
                self.labelp5['text'] = f'{player[4]}({BI[4]}) \n ($={wallet[4]})\n {status[4]}'
                self.labelp7['text'] = f'{player[5]}({BI[5]}) \n ($={wallet[5]})\n {status[5]}'
                playerMappingList.append(5)
                playerMappingList.append(7)
            else: 
                self.labelp7['text'] = f'{player[4]}({BI[4]}) \n ($={wallet[4]})\n {status[4]}'
                playerMappingList.append(7)
        self.setActivePlayerFlag(playerMappingList,activePlayerList) 
            
    
        
    def processIncoming(self):
        '''Deals with all the messages currently in the Queue'''
        while self.queue.qsize():
            #debug info here
             
            try:
                msg = self.queue.get()
                #debug info here
                #self.labelp6['text']='newRequest \n' + str(self.display.newRequest) +'\n' + str(self.display.phase)
                if msg == 0: #msg 0 is used to update just the 
                    #update the main text window
                    self.mainText.insert(END, self.display.mainText)
                    self.mainText.see(END) #pushes text cursor to end so it displays bottom of box (may have to be repeated).
                    #here we update puttons to have the correct function on them
                    #clear it so it stops updatingrepeating lines
                    
                    self.display.mainText =""
                    if self.betVar.get() == "9876": #This is used for an emergency departure
                        self.foldClick()
                if msg== 1:
                    self.printTable() #update the table
                #this needs to be verified constantly or program can block
                if self.display.phase == 1:
                    self.passCallBtn['text']= 'Pass'
                    self.betRaiseBtn['text']= 'Bet'
                else:
                    self.passCallBtn['text']= 'Call'
                    self.betRaiseBtn['text']= 'Raise'
                #debug info here
                #self.labelp7['text']='newRequest \n' + str(self.display.newRequest) +'\n' + str(self.display.phase) 
            except queue.Empty:
                pass
            except:
                self.betRaiseBtn['text']= 'Bug'
                

            
class ThreadedClient:
    '''This launches the main GUI and the worker thread for I/O  '''
    def __init__(self,master):
        self.master = master
        
        #create the queue
        self.queue = queue.Queue()
        self.display = Display()
        
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((IP, PORT))
        self.client_socket.setblocking(False)
        self.username = my_username.encode("utf-8")
        self.username_header = f"{len(self.username):<{HEADER_LENGTH}}".encode("utf_8")
        #***** Data starts being sent here
        self.client_socket.send(self.username_header + self.username)
        #we check that the user is logged-in properly before launching the GUI
        self.validateLogin()
        
        #set up gui
        self.gui = Goui(master,self.queue,self.client_socket,self.display)
        
        #setup threaded asynchroniuos i/o
        self.running=1
        self.thread1 = threading.Thread(target=self.workerThread1)
        self.thread1.start()
        
        #start periodic call in GUI to see if something new is now in Queue.
        self.periodicCall()
        
    def getInfo(self):
        requestString_header = self.client_socket.recv(HEADER_LENGTH)
        requestString_length = int(requestString_header.decode("utf-8").strip())
        requestString = self.client_socket.recv(requestString_length).decode("utf-8")
        return requestString
        
    def periodicCall(self):
        '''check every 200ms if there's something new in the Q'''
        self.gui.processIncoming()
        if not self.running:
            #This is to stop stuff if things are shutting down 
            import sys
            sys.exit()
        self.master.after(200,self.periodicCall)
        
    def workerThread1(self):
        '''handling the I/O here, and writing in the display object, which can then be read in the GUI'''
        #force the dialog box to print out on start of thread
        self.queue.put(0)
        while self.running:
            try:
                while True:
                    
                    # receive things from the server
                    instruction_header = self.client_socket.recv(HEADER_LENGTH)
                    if not len(instruction_header):  # connection is closed
                        print("connection closed by the server")
                        sys.exit()
    
                    instruction_length = int(instruction_header.decode("utf-8").strip())
                    instruction = self.client_socket.recv(instruction_length).decode("utf-8")
    
                    if instruction == "PRINT":  # used for receiving printLn. Server can send any info to be printed on client
                        self.display.mainText += '\n'+ str(self.getInfo()) 
                        self.queue.put(0)
        
                    if instruction == "REQUEST":  # same as above but sends client cursor. needs response...
                        self.display.mainText += '\n'+ str(self.getInfo())
                        if 'P)ass' in self.display.mainText:
                            self.display.phase= 1
                        elif 'C)all' in self.display.mainText:
                            self.display.phase= 2
                        #time.sleep(1)
                        self.display.newRequest = True
                        self.queue.put(0)
                          # this simply creates the input box on next loop so user can respond
        
                    # Sqwak is a seperate instruction that only sends client specific info that other players must not see
                    # makes it impossible to manipulate client source code to see other players' cards
                    if instruction == "SQWAK":  # sent regularly to update player/client's card and hand
                        self.display.yourPlayerID = int(self.getInfo())
                        self.display.myCards = self.getInfo()
                        self.display.myHand = self.getInfo()
                        
        
                    # sent to update on non-player specific info and re-prints table
                    if instruction == "UPDATETABLE":  # single send per turn
                        # totalPlayers = getInfo()
                        self.display.potSize = int(self.getInfo())
                        self.display.commonCards = self.getInfo()
                        self.display.activePlayer = int(self.getInfo())  # where cursor currently is -should be in Bold
    
                        self.queue.put(1) #display.printTable()
    
                    # sent to update each player's specific info (inc other players)
                    if instruction == "UPDATEPLAYER":  # n player send per turn
    
                        playerID = int(self.getInfo())
                        self.display.playerList[playerID].dollarWallet = int(self.getInfo())
                        self.display.playerList[playerID].wins = int(self.getInfo())
                        self.display.playerList[playerID].status = self.getInfo()
                        
    
                    # used at beginning to launch the poker table once all players have joined
                    if instruction == "SETUP":
                        self.display.totalPlayers = int(self.getInfo())
                        for count in range(self.display.totalPlayers):
                            # only item is playerName
                            playerName = self.getInfo()
                            self.display.mainText += playerName + '\n'
                            self.display.playerList.append(Player(playerName, count))  # playerID and name are added here
                        # should be followed by immediate UPDATE
                        self.display.mainText += "Setup completed! \n"
                        self.queue.put(0)
            
            # You want to ignore all IOerrors except for socket reading errors
            except IOError as e:
                if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                    print('Reading error', str(e))
                    sys.exit(exit)
                continue
            
    def validateLogin(self):
        '''Sole purpose of this method is to validate the login before launching the GUI listening thread'''
        while True:
            try:
                instruction_header = self.client_socket.recv(HEADER_LENGTH)
                if not len(instruction_header):  # connection is closed
                    print("connection closed by the server")
                    sys.exit()

                instruction_length = int(instruction_header.decode("utf-8").strip())
                instruction = self.client_socket.recv(instruction_length).decode("utf-8")
                if instruction == "PRINT" or instruction =="REQUEST":  # used for receiving printLn. Server can send any info to be printed on client
                    self.display.mainText += '\n'+ str(self.getInfo()) 
                    #Below is not efficient but it creates a more seamless experience for player
                    #check if server is rebooting session variables from last game, and resend player name if it is
                    if 'on board' in self.display.mainText:
                        return #the validation is done the program can run
                    if 're-launch' in self.display.mainText:
                        self.display.mainText = 'Everyone on board? (click any button when ready, with one player being hold-out until everyone has launched)'
                        time.sleep(0.2) #give time to server to do its reset and re-listen
                        #resend username details after 200 ms
                        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        self.client_socket.connect((IP, PORT))
                        self.client_socket.setblocking(False)
                        self.client_socket.send(self.username_header + self.username)
                        return
                    if 'inactive for 5 mins' in self.display.mainText:
                        return #need to do this or user can't see server feedback
            except IOError as e:
                if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                    print('Reading error', str(e))
                    sys.exit(exit)
                continue
                    
                    
from tkinter import *
import tkinter.font as tkFont
root = Tk()

client = ThreadedClient(root)
#keep this at very end of program
root.mainloop()
