'''
Created on Nov. 13, 2019

@author: Mike

@details    crawler GUI
'''
import gtk
import time, os, sys
from collections import OrderedDict 

import Communications, data_parser
import simulate
import gui_support
import threading
import multiprocessing
import gobject

#Allow only the main thread to touch the GUI (gtk) part, while letting other threads do background work.
gobject.threads_init()

script_location = os.path.dirname(os.path.abspath(__file__))
class CrawlerGUI():    
    def __init__(self):
        '''
        inherits GUI support object and links it to GUI signals
        to provide an action to a user response.
        '''
        
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


        self.inputKp = self.builder.get_object('entry1')
        self.inputKi = self.builder.get_object('entry2')
        self.inputMaxPIDOut = self.builder.get_object('entry3')

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
             
        #load GUI default values from a settings file                
        self.cfg_file_handle.load_settings()
        
        self.autoConnect          = self.builder.get_object('autoConnect')  
        if self.autoConnect.get_active():
            print('auto connecting')
            self.ComComboHandle.rescan()
            try:
                widget = self.builder.get_object('Com_channel_combo_box')
                #self.index = widget.get_active() #index indicate the nth item current selected in combobox
                self.index = 1
                self.model = widget.get_model()
                self.item = self.model[self.index][1] #item is the text in combo box

                #set selection state 0 as a false state
                if not self.index == 0:
                    print('selected', self.item)
                    Communications.consumer_portname = self.item
                    Communications.serial_activated = True
            except:
                #print(str(e))
                print('could not auto connect to radio, make sure its plugged in and nothing is already using it ')
        

        #set current gcode file to whatever file path is 
        #displayed in the GCode file path text box
        self.set_gcode_file()
        
        #show the GUI window
        self.window = self.builder.get_object("window1")
        self.window.show()
        self.comthread = None

        #gobject.timeout_add(1000,self.data_update)
        self.data_update()

        self.status_of_relays = OrderedDict([
            ('togglebutton1', False),
            ('togglebutton2', False),
            ('togglebutton3', False),
            ('togglebutton4', False),
            ('togglebutton5', False),
            ('togglebutton6', False),
            ('togglebutton7', False),
            ('togglebutton8', False),
        ])

        self.radiation_on = False

    ###################### Actions for all signals#########################
    def on_togglebutton1_toggled(self,widget):
        if self.radiation_on == False:
            d = gtk.Dialog()
            d.add_buttons(gtk.STOCK_YES, 1, gtk.STOCK_NO, 2)

            label = gtk.Label('Warning! You are about to enable radiation, are you sure?')
            label.show()
            d.vbox.pack_start(label)

            answer = d.run()
            d.destroy()
            self.radiation_on = True
            return True
        if self.radiation_on == True:
            self.radiation_on = False

    def on_speedScale_value_changed(self,widget):
        '''
        set percentage of speed
        '''
        speed = int(widget.get_value())*4096/100
        print('sending speed', str(speed))
        Communications.SendCommand(2,speed)
    def on_speedScale1_value_changed(self,widget):
        '''
        set percentage of Left/Right
        '''
        Communications.SendCommand(3,int(widget.get_value())*4096/100)

    def on_speedScale2_value_changed(self,widget):
        '''
        set percentage of ramp rate
        '''
        Communications.SendCommand(9,int(widget.get_value()))

    def on_entry2_editing_done(self,widget):
        Communications.SendCommand(3,int(widget.get_text()))

    def on_checkbutton4_toggled(self,widget):
        #check box for enable running
        Communications.SendCommand(0,widget.get_active())

    def on_checkbutton5_toggled(self,widget):
        #check box for enabling or disabling PI loop
        Communications.SendCommand(1,widget.get_active())

    def toggled_a_relay(self,widget):
        #print 'clicked', widget.get_label(), gtk.Buildable.get_name(widget), widget.get_active()
        self.status_of_relays[gtk.Buildable.get_name(widget)] = widget.get_active()
        #print self.status_of_relays
        val = 0
        for index, key in enumerate(self.status_of_relays):
            #print key, self.status_of_relays[key]
            val = val+((index+1)*self.status_of_relays[key])
        Communications.SendCommand(5,val)

    def on_button11_clicked(self,widget):
        Communications.SendCommand(4,0)

    def on_button12_clicked(self,widget):
        Communications.SendCommand(4,4095)

    def on_button13_clicked(self,widget):
        Communications.SendCommand(4,2056)

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
    
    def on_shutdown_clicked(self,widget):
        '''
        When the 'shutdown radio and quit GUI' button is clicked,
        shut down the user side LoRa radio.
        
        Since the user side LoRa radio is a computer with its own OS
        I recommended doing this before disconnecting the USB cable from the computer
        '''
        print('shutting down radio...')
        try:
            Communications.com_handle.write('shutdown radio now\r')
        except:
            pass
        sys.exit(0)
        # time.sleep(1)
        # Communications.com_handle.write('\x03')
        # time.sleep(1)
        # Communications.com_handle.write('sudo shutdown -r now')

    def on_button14_clicked(self,widget):
        '''
        default kp = 0.01 and ki 
        set kp to 0.1 and ki to 4 to for very fast response

        use command 8 

        settings:
        speed 10%
        Kp = .1
        ki = 4.0
        Max pid out = 10


        CMD:2,163#6,50#7,2000#8,500#1,1#0,0#
        max pid out = 5


        got it working at
        .4 = kp
        4 = ki
        3 =max pid output
        speed = 7
        '''
        kp = self.inputKp.get_text()
        ki = self.inputKi.get_text()
        max_pid_output = self.inputMaxPIDOut.get_text()
        print('kp {} ki {}'.format(kp, ki))
        Communications.SendCommand(6,int(float(kp)*1000))
        Communications.SendCommand(7,int(float(ki)*1000))
        Communications.SendCommand(8,int(float(max_pid_output)*100))

    def on_button15_clicked(self,widget):
        '''
        clear timeout fault 

        crawler expects a keep alive command every X seconds, if not received crawler will default to 
        safe mode. in safe mode crawler stops running until it receives clear fault command and user disable and reenable run 
        '''
        print('clearing timeout fault')
        Communications.SendCommand(11,0)

    ###################### End of actions for all signals#################
    def _quit_program(self):
        '''
        save a configuration file before terminating GUI thread
        '''
        #send ascii for ctrl-c  to radio to terminate python script
        Communications.com_handle.write('\x03')
        self.cfg_file_handle.save_config_file()
        gtk.main_quit()
        
    def data_update(self):
        '''
        runs periodically to update GUI data
        '''
        #print 'called data update'
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

    print 'Terminated All Threads'
