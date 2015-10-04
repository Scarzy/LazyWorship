#!/usr/bin/env python

import gtk
import display
import threading
import record_wav
import dejavu_handler



class LazyWorship():
    def __init__(self):
        self.disp = display.display()
        self.djv = dejavu_handler.dejavu_handler()
        self.rwav = record_wav.AudioRecorder()
        gtk.main()
        pass
    
    def __run_recorder(self):
        while True:
            self.buff = self.rwav.getBuffer()
            self.djv.recognise(self.buff)

    def import_prints(self, dirs):
        self.djv.fingerprint(dirs)
        pass



import argparse
parser = argparse.ArgumentParser(description='Song presentation software that advances based on audio analysis')
parser.add_argument('--import_dir', metavar='DIR', nargs='*', help='Any directories that you with to import fingerprints of')
args = parser.parse_args()

lazyworship = LazyWorship()
if args.import_dir is not None:
    lazyworship.import_prints(args.import_dir)
