"""
@author          Michael House
@organisation    Terrafirma Technology, Inc.
@date            10/10/2019

@details         test serial coms

                 note: on the raspberry pi you must access the serial port via /dev/serial0
                 also serial port must be enabled in via "sudo raspi-config" interfacting options
"""
from distutils.core import setup
import py2exe
import os

# Find GTK+ installation path
__import__('gtk')
m = sys.modules['gtk']
gtk_base_path = m.__path__[0]

setup(
    name = 'main',
    description = 'crawler gui',
    version = '1.0',

    windows = [
                  {
                      'script': 'main.py',
                      #'icon_resources': [(1, "handytool.ico")],
                  }
              ],

    options = {
                  'py2exe': {
                      'packages':'encodings',
                      # Optionally omit gio, gtk.keysyms, and/or rsvg if you're not using them
                      'includes': 'cairo, pango, pangocairo, atk, gobject, gio, gtk.keysyms, rsvg',
                  }
              },

    data_files=[
                   'handytool.glade',
                   'readme.txt',
                   # If using GTK+'s built in SVG support, uncomment these
                   #os.path.join(gtk_base_path, '..', 'runtime', 'bin', 'gdk-pixbuf-query-loaders.exe'),
                   #os.path.join(gtk_base_path, '..', 'runtime', 'bin', 'libxml2-2.dll'),
               ]
)
