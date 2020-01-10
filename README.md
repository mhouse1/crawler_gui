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

Using FileZilla to connect to raspberry
Host: stfp://raspberrypi.local Username:pi Password:raspberry

on mac to ssh to crawler side radio: 
ssh pi@raspberrypi1.local
password:raspberry

on windows:
connection to userside radio using winscp
hostname:pi@raspberrypi1
username:pi
password: raspberry

connection via putty to user side radio
hostname:pi@raspberrypi1
username:pi
password:raspberry

give your pi a unique hostname
details:https://thepihut.com/blogs/raspberry-pi-tutorials/19668676-renaming-your-raspberry-pi-the-hostname

how to kill python
pi@raspberrypi:/home/crawler_gui/GUI $ ps -ef | grep python3
pi         746   656  0 01:35 pts/1    00:00:00 grep --color=auto python3
pi@raspberrypi:/home/crawler_gui/GUI $ kill 746
-bash: kill: (746) - No such process
pi@raspberrypi:/home/crawler_gui/GUI $ kill 656

Installation:
pygtk-all-in-one-2.24.2.win32-py2.7.msi (31.6MB)
Python 2.7.8
Windows 10



#########################################################################################
After flashing the cloned image
update to latest crawler_gui scripts
For crawler side radio, connect to computer via usb serial com port, change interfacing options using command:
    sudo raspi-config
set Interfacing Options > Serial > 
Would you like a login shell to be accessible over serial? No
Would you like the serial port hardware to be enabled? Yes


############################################################################################
for crawler side radio we must add the radio script as a service so when it boots it automatically starts
INFO:https://www.raspberrypi.org/documentation/linux/usage/systemd.md

In order to have a command or program run when the Pi boots, you can add it as a service. Once this is done, you can start/stop enable/disable from the linux prompt.

Creating a service
On your Pi, create a .service file for your service, for example:

myscript.service

[Unit]
Description=My service
After=network.target

[Service]
ExecStart=/usr/bin/python3 -u main.py
WorkingDirectory=/home/pi/myscript
StandardOutput=inherit
StandardError=inherit
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
So in this instance, the service would run Python 3 from our working directory /home/pi/myscript which contains our python program to run main.py. But you are not limited to Python programs: simply change the ExecStart line to be the command to start any program/script that you want running from booting.

Copy this file into /etc/systemd/system as root, for example:

sudo cp myscript.service /etc/systemd/system/myscript.service
Once this has been copied, you can attempt to start the service using the following command:

sudo systemctl start myscript.service
Stop it using following command:

sudo systemctl stop myscript.service
When you are happy that this starts and stops your app, you can have it start automatically on reboot by using this command:

sudo systemctl enable myscript.service
The systemctl command can also be used to restart the service or disable it from boot up!

Some things to be aware of:

The order in which things are started is based on their dependencies — this particular script should start fairly late in the boot process, after a network is available (see the After section).
You can configure different dependencies and orders based on your requirements.