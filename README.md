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



give your pi a unique hostname
details:https://thepihut.com/blogs/raspberry-pi-tutorials/19668676-renaming-your-raspberry-pi-the-hostname

how to kill python
pi@raspberrypi:/home/crawler_gui/GUI $ ps -ef | grep python3
pi         746   656  0 01:35 pts/1    00:00:00 grep --color=auto python3
pi@raspberrypi:/home/crawler_gui/GUI $ kill 746
-bash: kill: (746) - No such process
pi@raspberrypi:/home/crawler_gui/GUI $ kill 656