#!/usr/bin/env python

import re
import gtk
import display
import db_mysql
import threading
import record_wav
import dejavu_handler


class LazyWorship():
    def __init__(self):
        self.disp = display.display()
        self.djv = dejavu_handler.dejavu_handler()
        self.rwav = record_wav.AudioRecorder()
        self.db = db_mysql.Database()
        gtk.main()
        pass
    
    def __run_recorder(self):
        while True:
            self.buff = self.rwav.getBuffer()
            fname = self.djv.recognise(self.buff)
            song, verse, part = self.fname_to_parts(fname)
            self.disp.update_lyrics(self.db.get_lyrics(song, verse, part))
            
    def fname_to_parts(self, fname):
        match = re.match('^([a-z_]+)-v([0-9]+)-p([0-9]+)$', fname)
        song = "unknown"
        verse = 0
        part = 0
        if match is not None:
            song = match.groups(1)
            verse = match.groups(2)
            part = match.groups(3)
        return song, verse, part

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
