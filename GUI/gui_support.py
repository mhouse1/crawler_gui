'''
Created on Aug 24, 2014
@author: Dynames

@details  contains functions to support a GUI interface, by inheriting GuiSupport it is possible
          to access all the same functionality a GUI user would have by simply calling the functions.
          There is also a ConfigParser which saves and loads the user configurations in the GUI.
          All the communication is sent via a parallel process that is launched when the user
          configures the communication port.
'''
from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
from builtins import range
from builtins import object
import gtk
import os
import configparser
import sys

import Communications

def get_bin_with_padding(number,padding):
    '''
    where number is a positive or negative integer
    and padding is number of fill bits
    '''
    if number < 0 :
        value = bin(int(number)& pow(2,padding)-1)[2:]
    else:
        value = ('0b'+("{:0%db}"%padding).format(number))[2:]
    return value

class CfgFile(object):
    ''' manages a GUI configuration file 
    has the ability to create, save, and load configuration file
    configuration data saved is typically data in text boxes, combo boxes, and other object states
    on GUI startup if a configuration file exists it is loaded 
    '''
    def __init__(self,builder):
        self.builder = builder
        self.config_object = configparser.ConfigParser()
        self.config_file_name = 'config.ini'
        
        #a list of names of objects classfied as settings
        self.settings =[
                        'GCode_File_Location'
                        ,'autoConnect'
                        # ,'reverse_x'
                        # ,'reverse_y'
                        # ,'reverse_z'
                        # ,'feed_cut'
                        # ,'speed_start'
                        # ,'speed_change'
                        # ,'gcode_scale'
                        # ,'layer_thickness'
                        # ,'layer_numbers'
                        ] 
        
    def create_config_file(self,config_object, config_file_name):
        f = open(config_file_name,'w')
        config_object.read(config_file_name)
        config_object.add_section('settings')
        config_object.write(f)
        f.close()
        print('created Kshatria config file')
        
    def save_config_file(self):
        #self.config_object.set('settings', 'g-code file','none')
        for item in self.settings:
            obj = self.builder.get_object(item)
            #print obj.__class__.__name__
            if obj.__class__.__name__ == 'Entry':
                try:
                    self.config_object.set('settings', item,obj.get_text())
                except Exception as err:
                    print(err)
            elif obj.__class__.__name__ == 'CheckButton':
                try:
                    self.config_object.set('settings', item,obj.get_active())
                except Exception as err:
                    print(err)     
        self.config_object.write(open(self.config_file_name,'w'))
        print('saved config file')
        
    def load_settings(self):
        '''create and fill config file if it does not exist
        load_settings should be called only after self.settings has been appended to
        '''
        if not os.path.isfile(self.config_file_name) :
            
            self.create_config_file(self.config_object, self.config_file_name)
        else:#read config file
            self.config_object.read(self.config_file_name)
        #print self.settings
        #get object then set as value in config file
        for item in self.settings:
            obj = self.builder.get_object(item)
            
            #print item
            #if obj.__class__ == ''
            if obj.__class__.__name__ == 'Entry':
                if item == 'GCode_File_Location':
                    self.gcode_file = self.config_object.get('settings', item)
                    print('set gcode file to ',self.gcode_file)
                try:
                    obj.set_text(self.config_object.get('settings', item))
                except Exception as err:
                    print(err)
            elif obj.__class__.__name__ == 'CheckButton':
                try:
                    obj.set_active( 1 if 'True' == self.config_object.get('settings',item ) else 0)
                except Exception as err:
                    print(err)     
        #self.GTKGCode_File.set_text(self.config_object.get('settings', 'g-code file'))

        print('loaded config file')

class CfgData(object):
    def __init__(self, builder,cfg_handle):
        #cfg_file.__init__(self)
        self.CfObjects = []
        self.PackedData = []
        self.classification ='cfdata'
        
        name_of_config_data_objects =[#'HMin','HMax',
                                      #'LMin','LMax',
                                      'pulsewidth_x_h','pulsewidth_x_l',
                                      'pulsewidth_y_h','pulsewidth_y_l',
                                      'pulsewidth_z_h','pulsewidth_z_l',
                                      #'SPer','SInc'
                                      ]
        
        cfg_handle.settings.extend(name_of_config_data_objects)

        #add all config objects to list
        for item in name_of_config_data_objects:
            self.addCfDataObject(builder.get_object(item))
        
#     def load_default(self, config_object, config_file_name):
#         if not os.path.isfile(config_file_name):
#             cfg_file.create_config_file()
#             
    def addCfDataObject(self,TxtObj):
        #objectDictionary = {gtk.Buildable.get_name(TxtObj):TxtObj}
        self.CfObjects.append(TxtObj)
    def All(self):
        return self.CfObjects

    def send(self):
        '''
        sends packed data over serial channel
        data will be in the format defined by protocol wrapper
        [Classification][Type][Data]
        [CRC32][Classification][Type][Data]
        
        call get_packedData to get the data to send
        '''
        #print self.get_packedData()[0]
        #if not Communications.active_serial == None:
#         print self.get_packedData()
#         raw_input('packed data')
#         for data in self.get_packedData():
#             C
        for data in self.get_packedData():
            Communications.transmit(data)


def get_com_port_list():
    
    #create an instance of Liststore with data
    liststore = gtk.ListStore(int,str)
    Com_List = Communications.list_serial_ports()
    liststore.append([0,"Select a valid serial port:"])
    for port_number in range(len(Com_List)):
        #print port_number
        liststore.append([port_number,Com_List[port_number]])
    return liststore
        
class ComCombo(object):
    '''deals with the combo box that allow selection of com port to use
    '''
    def __init__(self,builder):
        '''initialize the combo box
        '''
        self.name = 'Com_channel_combo_box'
        self.builder = builder
        #get an instance of the combo box
        self.Com_channel_combo = self.builder.get_object(self.name)
        #set the ListStore as the Model of the ComboBox
        
        
        #create an instance of the gtk CellRendererText object and pack into
        self.cell = gtk.CellRendererText()
        self.Com_channel_combo.pack_start(self.cell,True)
        self.Com_channel_combo.add_attribute(self.cell,'text',1)
        self.Com_channel_combo.set_active(0)
        self.Com_channel_combo.set_model(get_com_port_list())
        
    def rescan(self):
        #get a updated com port list and set as combo box options
        self.Com_channel_combo.set_model(get_com_port_list())
    

class GsComboBox(object):
    '''deals with the combo box that allow selection of com port to use
    '''
    def __init__(self,builder,obj_name, options):
        '''initialize the combo box
        '''
        self.name = obj_name
        self.builder = builder
        #get an instance of the combo box
        self.combo_obj = self.builder.get_object(self.name)
        #set the ListStore as the Model of the ComboBox
        
        
        #create an instance of the gtk CellRendererText object and pack into
        self.cell = gtk.CellRendererText()
        self.combo_obj.pack_start(self.cell,True)
        self.combo_obj.add_attribute(self.cell,'text',1)
        self.combo_obj.set_active(0)
        self.combo_obj.set_model(self._get_options(options))
        
    def _get_options(self,options):
        #create an instance of Liststore with data
        liststore = gtk.ListStore(int,str)
#         liststore.append([0,"set_direction"])
#         liststore.append([1,"up"])
#         liststore.append([2,"down"])
        for index, option in enumerate(options):
            liststore.append([index,option])
        #print 'list store',self.name,liststore
        return liststore
                    

    def get_selection(self):
        index = self.combo_obj.get_active()
        model = self.combo_obj.get_model()
        item = model[index][1]
        return item

    def get_selection_index(self):
        index = self.combo_obj.get_active()
        return index        
                    
class DirectionCombo(object):
    '''deals with the combo box that allow selection direction
    '''
    def __init__(self,builder,name):
        '''initialize the combo box
        '''
        self.name = name #'DirXComboBox'
        #cfg_handle.settings.extend(self.name)
        self.builder = builder
        #get an instance of the combo box
        self.Com_channel_combo = self.builder.get_object(self.name)
        #set the ListStore as the Model of the ComboBox
          
        
        #create an instance of the gtk CellRendererText object and pack into
        self.cell = gtk.CellRendererText()
        self.Com_channel_combo.pack_start(self.cell,True)
        self.Com_channel_combo.add_attribute(self.cell,'text',1)
        self.Com_channel_combo.set_active(0)
        self.Com_channel_combo.set_model(self.get_options())
    def get_options(self):
    
        #create an instance of Liststore with data
        liststore = gtk.ListStore(int,str)
        liststore.append([0,"set_direction"])
        liststore.append([1,"up"])
        liststore.append([2,"down"])
        return liststore
            
    def rescan(self):
        #get a updated com port list and set as combo box options
        self.Com_channel_combo.set_model(get_com_port_list())
            