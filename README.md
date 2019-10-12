# crawler_gui
* A cross platform GUI:supports Windows, Mac OS, Linux

* Control Page
![Control Page](https://github.com/mhouse1/crawler_gui/blob/master/Documentation/GUI_View1.PNG)

* Full screen
![Test Page](https://github.com/mhouse1/crawler_gui/blob/master/Documentation/GUI_View2.PNG)

* Configuration screen
![Test Page](https://github.com/mhouse1/crawler_gui/blob/master/Documentation/GUI_View3.PNG)


* Test Page
![Test Page](https://github.com/mhouse1/crawler_gui/blob/master/Documentation/GUI_View4.PNG)


SSH using PuTTY defaul
Host Name: raspberrypi
Port: 22
Connection Type: SSH
Click Open
Login as: pi
Password: raspberry


on mac:
to ping raspberry and see ip addresses
    ping raspberrypi.local

use command :ssh pi@raspberrypi.local
password: raspberry


enable copy and paste over VNC
    sudo apt-get install autocutsel 
    sudo reboot
copy paste should work now
use shit+ctrl+v

installing gtk

    sudo apt-get install glade
    sudo apt-get install libgtk-3-dev


python3 gtk
from gi.repository import Gtk as gtk

importError: No module named 'Queue'
resolve: in python3 use import queue as Queue

pip3 is broken
resolve: use pip to install new pakages for python3 using command example
python3 -m pip install pyserial


can't connect via filazilla
    Error:        	Disconnected: No supported authentication methods available (server sent: publickey)
resolve: try connecting using sftp://192.168.0.112 or whatever your local ip is, to see your ip, use command: hostname -I 



====================== On Windows ============================
install python3 ; i installed python-3.7.4.exe
	https://www.python.org/downloads/ 
	run the exe and choose custom install location C:\Python3
after the install run command: "python -V" to display python version installed
example:
	PS C:\Users\Mech1\Documents\crawler_gui\GUI> python -V
	Python 3.7.4
	note: on other non windows system you'd normally do python3 to specify run python3

Other required modules:
pip install pyserial
pip install --upgrade setuptools
note: running pip install pygtk may fail saying you need pygobject
but installing pygobject will fail saying you need " error: Microsoft Visual C++ 14.0 is required"
in that case download and intall visual studio build tools from here
 http://go.microsoft.com/fwlink/?LinkId=691126&fixForIE=.exe.
note: do NOT do pip install serial, it will install the wrong thing

	
