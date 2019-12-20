Outfile "crawler.exe"

InstallDir $APPDATA\crawler_gui

Section Dependencies
	SetOutPath $INSTDIR
	File python-2.7.17.amd64.msi
	File pygi-aio-3.24.1_rev1-setup.exe
	ExecWait 'msiexec /i "$INSTDIR\python-2.7.17.amd64.msi"'
	ExecWait pygi-aio-3.24.1_rev1-setup.exe
SectionEnd

Section
	SetOutPath $INSTDIR
	File bytestream0.txt
	File Communications.py
	File config.ini
	File Crawler.glade
	File data_parser.py
	File emergency1.png
	File emergency2.jpg
	File gui_support.py
	File main.py
	File simulate.py
	File test_serial.py
	File PyGTK2.24.0-legacy.zip
	nsisunz::UnzipToLog "PyGTK2.24.0-legacy.zip" "C:\Python27\Lib\"
	CreateShortCut "$DESKTOP\Crawler GUI.lnk" "$INSTDIR\main.py"
	CreateShortCut "$SMPROGRAMS\Crawler GUI.lnk" "$INSTDIR\main.py"
	WriteUninstaller "$INSTDIR\uninstall.exe"
	CreateShortCut "$SMPROGRAMS\Uninstall Crawler GUI.lnk" "$INSTALLDIR\uninstall.exe"

SectionEnd

Section "uninstall"

	Delete "$INSTDIR\uninstall.exe"
	Delete "$INSTDIR\bytestream0.txt"
	Delete "$INSTDIR\Communications.py"
	Delete "$INSTDIR\config.ini"
	Delete "$INSTDIR\Crawler.glade"
	Delete "$INSTDIR\data_parser.py"
	Delete "$INSTDIR\emergency1.png"
	Delete "$INSTDIR\emergency2.jpg"
	Delete "$INSTDIR\gui_support.py"
	Delete "$INSTDIR\main.py"
	Delete "$INSTDIR\simulate.py"
	Delete "$INSTDIR\test_serial.py"
	Delete "$DESKTOP\Crawler GUI.lnk"
	Delete "$SMPROGRAMS\Crawler GUI.lnk"
	Delete "$SMPROGRAMS\Uninstall Crawler GUI.lnk"
	Delete "$INSTDIR\pygi-aio-3.24.1_rev1-setup.exe"
	Delete "$INSTDIR\python-2.7.17.amd64.msi"
	Delete "$INSTDIR\PyGTK2.24.0-legacy.zip"
	
SectionEnd