'''
Created on Nov. 13, 2019

@author: Mike

@details    crawler GUI
'''
import gtk
import time, os

import Communications, data_parser
import simulate
import gui_support
from gui_support import GuiSupport
import threading
import multiprocessing
import gobject

#Allow only the main thread to touch the GUI (gtk) part, while letting other threads do background work.
gobject.threads_init()

script_location = os.path.dirname(os.path.abspath(__file__))
class CrawlerGUI(GuiSupport):    
    def __init__(self):
        '''
        inherits GUI support object and links it to GUI signals
        to provide an action to a user response.
        '''
        super(CrawlerGUI,self).__init__()
        
        #read *.glade xml file that has the gui layout info
        #build the gui interface using xml file
        #connect gui signals to call back functions
        self.gladefile = "Crawler.glade"
        self.builder = gtk.Builder()
        self.builder.add_from_file(self.gladefile)
        self.builder.connect_signals(self)


        #use builder object to get a handle to configuration file
        self.cfg_file_handle  = gui_support.CfgFile(self.builder)
        
        #use builder to get a handle to the COM port drop down object
        self.ComComboHandle = gui_support.ComCombo(self.builder)

        #use builder to get gcode file path text box object
        self.GTKGCode_File = self.builder.get_object('GCode_File_Location')
        
        #use builder to get GUI tab/pages object
        self.notebook = self.builder.get_object('notebook1')

        #use builder and config file handle to get config data
        #pass CfData cfg_file_handle because we want those items to be saved to cfg file too
        self.CNCConfigData = gui_support.CfgData(self.builder,self.cfg_file_handle)
        
        self.CNCCommand = gui_support.CncCommand(self.builder,self.cfg_file_handle)
        self.SendSinleCFData = gui_support.SendSinleCFData(self.builder,self.cfg_file_handle)
        self.ManualControlData = gui_support.ManualControlData(self.builder,self.cfg_file_handle)
        
        #drop down GUI objects used to set routing direction
        xdirection_combo_options = ['left','right']
        ydirection_combo_options = ['backward','forward']
        zdirection_combo_options = ['counter-clockwise','clockwise']
        self.DirXComboHandle = gui_support.GsComboBox(self.builder,'DirX',xdirection_combo_options)
        self.DirYComboHandle = gui_support.GsComboBox(self.builder,'DirY',ydirection_combo_options)
        self.DirZComboHandle = gui_support.GsComboBox(self.builder,'DirZ',zdirection_combo_options)

        #labels
        self.batteryLevel       = self.builder.get_object('label24')
        self.distanceTraveled       = self.builder.get_object('label34')
        self.encoder1 = self.builder.get_object('label35')
        self.encoder2 = self.builder.get_object('label36')
        self.encoder3 = self.builder.get_object('label37')
        self.encoder4 = self.builder.get_object('label38')

        #toggle buttons
        self.crawlDirection = self.builder.get_object('togglebutton9')
        self.disableBalancing = self.builder.get_object('togglebutton11')

        self.emergencyStopImage = self.builder.get_object('image7')
        self.emergencyToggle = False
                                               

        #slider, aka scale objects
        self.inclineLeftRight       = self.builder.get_object('hscale1')
        self.inclineFrontBack       = self.builder.get_object('vscale1')
        self.movementLeftRight      = self.builder.get_object('hscale2')
        self.movementReverseForward = self.builder.get_object('hscale3')
        self.crawlerSpeed          = self.builder.get_object('speedScale')                        
        
        self.inclineLeftRight.set_digits(2)#sets number of display percisions
        #self.inclineLeftRight.set_has_origin(True)#this does not work
        
        #self.inclineLeftRight.set_fill_level(float(12345))
        #self.inclineLeftRight.set_vexpand(True)
        #self.inclineLeftRight   = self.builder.get_object('hscale1')
        #self.inclineLeftRight.set_digits()
        
        #self.inclineLeftRight.set_fill_level(float(12345))
        #self.inclineLeftRight.set_value_pos(9)#not sure what this does
        #self.inclineLeftRight.set_value(0)#this works to set value of scale
        
        #self.inclineLeftRight.set_vexpand(True)        

        
        #load GUI default values from a settings file                
        self.cfg_file_handle.load_settings()
        
        #set current gcode file to whatever file path is 
        #displayed in the GCode file path text box
        self.set_gcode_file()
        
        #show the GUI window
        self.window = self.builder.get_object("window1")
        self.window.show()
        self.comthread = None

        #gobject.timeout_add(1000,self.data_update)
        self.data_update()

    ###################### Actions for all signals#########################
    def on_speedScale_value_changed(self,a):
        '''
        set percentage of speed
        '''
        print 'speed event'


    def on_togglebutton9_clicked(self,widget):
        '''
        forward
        '''
        status = widget.get_active()

        if not status:
            widget.set_label('REVERSE')
            print 'send direction command',status
        else:
            widget.set_label('FORWARD')
            print 'send direction command',status
    
    def on_eventbox1_button_press_event(self,a,b):
        print 'eventbox pressed'
        self.emergencyToggle = not self.emergencyToggle
        if self.emergencyToggle:
            self.emergencyStopImage.set_from_file(os.path.join(script_location,'emergency2.jpg'))
        else:
            self.emergencyStopImage.set_from_file(os.path.join(script_location,'emergency1.png'))


    def on_image7_button_press_event(self,widget):

        print 'Send stop command'

    def on_togglebutton11_toggled(self,widget):
        #crawlForward = self.crawlForward.get_active()
        #crawlReverse = self.crawlReverse.get_active()
        disableBalancing = self.disableBalancing.get_active()
        print 'send disable balancing ', disableBalancing
        # if manual == True:
        #     self.toggleAutonomous.set_active(False)
        #     self.toggleSemiAuto.set_active(False)
      
    def on_rescan_coms_clicked(self,widget, data = None):
        '''
        rescan for available serial ports and update drop down box
        to display serial ports available
        '''
        self.ComComboHandle.rescan()

    def on_button6_clicked(self,widget):
        Communications.com_handle.close()
        Communications.consumer_portname = None
        Communications.serial_activated = False
        
    def on_Com_channel_combo_box_changed(self,widget, data = None):
        '''
        set combo box selection as active serial channel
        '''
        self.index = widget.get_active() #index indicate the nth item
        self.model = widget.get_model()
        self.item = self.model[self.index][1] #item is the text in combo box

        #set selection state 0 as a false state
        if not self.index == 0:
            print('selected', self.item)
            Communications.consumer_portname = self.item
            Communications.serial_activated = True
        #self.builder.get_object("label1").set_text(self.item)
    
    def notebook1_switch_page_cb(self,  notebook, page, page_num, data=None):
        '''
        do something when the gui changes from one tab to another
        this currently does nothing
        '''
        self.tab = notebook.get_nth_page(page_num)
        self.switched_page = notebook.get_tab_label(self.tab).get_label()
        print 'switched to page ',self.switched_page
    
    def on_Quit_activate(self,widget, data = None):
        '''
        exit gui and save config file
        '''
        print 'quitting...'
        self._quit_program()
    
    def on_window1_destroy(self, widget, data = None):
        '''
        exit gui and save config file
        '''
        print 'quitting...'
        self._quit_program()
    
    def set_gcode_file(self):
        '''
        set current gcode file to whatever file path is 
        displayed in the GCode file path text box
        '''
        
        self.gcode_file = self.GTKGCode_File.get_text()
        
    def on_Browse_For_GCode_pressed(self, widget, data = None):
        '''
        on button press open file chooser window to allow user to select 
        gcode file to use for routing
        '''
        print 'Browsing for GCode file'
        self.fcd = gtk.FileChooserDialog("Open...",None,gtk.FILE_CHOOSER_ACTION_OPEN,
                 (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                  gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        self.response = self.fcd.run()
        if self.response == gtk.RESPONSE_OK:
            self.gcode_file = self.fcd.get_filename()
            print "Selected filepath: %s" % self.gcode_file
            self.fcd.destroy()
            self.GTKGCode_File.set_text(self.gcode_file)
    
    ###################### End of actions for all signals#################
    def _quit_program(self):
        '''
        save a configuration file before terminating GUI thread
        '''
        self.cfg_file_handle.save_config_file()
        gtk.main_quit()
        
    def data_update(self):
        print 'called data update'
        if data_parser.data_frame:
            self.encoder1.set_text(str(data_parser.data_frame['encoder1']))
            self.encoder2.set_text(str(data_parser.data_frame['encoder2']))
            self.encoder3.set_text(str(data_parser.data_frame['encoder3']))
            self.encoder4.set_text(str(data_parser.data_frame['encoder4']))
            self.inclineLeftRight.set_value(data_parser.data_frame['roll'])

        # self.batteryLevel.set_text(str(simulate.battery_level))
        
        gobject.timeout_add(1000,self.data_update)

if __name__ == "__main__":
    print 'starting crawler GUI'
    #start communication for reading and writing
    comthreadWriter = threading.Thread(target = Communications.set_writer)
    comthreadWriter.daemon = True #terminate thread when program ends
    comthreadWriter.start()
    comthreadReader = threading.Thread(target = Communications.set_reader)
    comthreadReader.daemon = True #terminate when program ends
    comthreadReader.start()

    # #used for Demonstrating GUI operation
    # simulator = threading.Thread(target = simulate.simulate_data)
    # simulator.daemon = True #terminate when program ends
    # simulator.start()

    
    #GUI thread    
    main = CrawlerGUI()
    gtk.main()
