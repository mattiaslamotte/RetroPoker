# RetroPoker
RetroPoker is a Texas Hold'em client/server application written in Python 3.6.

Full instructions including server.exe and videos can be found on Google drive: 
https://drive.google.com/file/d/1Rx-f8S60IGxU7kMu3Ay-fyl59fCRBqEE/view?usp=sharing

As long as it's not for Commercial purposes, feel free to make any changes you wish to the client application.

The client runs smoothly on Windows, Macs or iPads using Pythonista 3.

a Demo server is currently running on IP 52.175.53.52. Feel free to use it as you please. We have a blast playing with it with friends anywhere (using zoom or skype video to communicate). 

You can also run the server on your own machine. There's a video on the google drive explaining how to set up your own VM on Azure with 
the poker server running.

The server currently only accomodates 1 poker room. If the room has been in use in the last 10 minutes, the server prevents new 
users from joining. If the server has not been in use in the last 10 minutes but has been in use since the last reboot, the next attempted user login resets all the session variables. If that happens, restart the client login process to successfully use the server. 

I have been thinking of a way of resetting the session variables before a re-login attempt, but as the server is single threaded, it's hard to do this without having a socket event being generated. I guess I could have a second application (like a server assistant application) that would occasionally connect through a socket connection to trigger a doesTheServerNeedResettingEvent but that doesn't seem very elegant either.

Have Fun!

Mattias
