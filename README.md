# RetroPoker
RetroPoker is a Texas Hold'em client/server application written in Python 3.6. The server is running on an Azure VM and can be tested by launching either the Windows or MacOS client.  

video demo and client.exe files can be found here:
https://drive.google.com/drive/folders/1NFoF7Ac0XchOLYRQ6jj7d6yfRQ8tTcXr?usp=sharing

server.exe and videos can be found on Google drive: 
https://drive.google.com/drive/folders/1t7VFOOF6qrWnA6YAbxc3baYw7t83376N?usp=sharing

The client application runs smoothly on Windows, Macs (or iPads using Pythonista 3 with the older non-GUI version).

<p align="center"><img src="https://github.com/mattiaslamotte/RetroPoker/blob/master/ScreenshotRetropoker.jpg" alt="screenshot" width="500"> </p>

The mac executable version is in a zip file format. You will need to do ctrl-click to open it (otherwise it will tell you that security settings prevent this type of file to be opened). On the windows .exe file, there's also a warning but if you click "more info" in the warning dialog box, it then gives you the option to "run anyway".

If you run the source code, you will need to have Python 3.5 or upwards installed (just go to http://python.org/downloads to install the latest version). On Macs, there is a conflict between Tkinter and python 3.7 (it works fine on version 3.9 which is the latest version of python).

While downloading python and running the source code on windows is a piece of cake, it's a bit more complicated on Macs as the default version of Python is the pre-installed python 2.7 version. Usually, Macs should have HomeBrew pre-installed, and you can simply type "brew switch python 3.9.0" in Terminal to upgrade your default Python to its latest version.

Have Fun!

Mattias
