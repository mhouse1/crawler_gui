Outfile "crawler.exe"

InstallDir $APPDATA\crawler_gui

Section

	#SetShellVarContext all

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

	CreateShortCut "$DESKTOP\Crawler GUI.lnk" "$INSTDIR\main.py"
	CreateShortCut "$SMPROGRAMS\Crawler GUI.lnk" "$INSTDIR\main.py"

	WriteUninstaller "$INSTDIR\uninstall.exe"

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
	
SectionEnd