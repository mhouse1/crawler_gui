@echo off

set pylib=C:\Python27\Lib
echo Copying PyGTK files to %pylib%....
robocopy %appdata%\crawler_gui\PyGTK2.24.0\* %pylib%