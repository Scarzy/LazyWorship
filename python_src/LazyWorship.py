#!/usr/bin/env python

import re
import gtk
import display
import db_mysql
import threading
import record_wav
import collections
import dejavu_handler
from dejavu.recognize import MicrophoneRecognizer


class LazyWorship():
    def __init__(self, dejavu_mic=False):
        self.disp = display.display()
        self.djv = dejavu_handler.dejavu_handler()
        self.dejavu_mic = dejavu_mic
        self.dq = collections.deque(maxlen=5)
        self.last_song = ""
        if dejavu_mic:
            pass
        else:
            self.rwav = record_wav.AudioRecorder()
            self.rwav.setWindowSizeSecs(1)
            self.rwav.setWindowStepSizeSecs(1)
        self.db = db_mysql.Database()
        pass
    
    def run(self):
        self.au_thread = threading.Thread(target=self.run_recorder)
        self.au_thread.daemon = True
        self.au_thread.start()
        gtk.main()
        pass
    
    def run_recorder(self):
        self.buff = []
        while True:
            fname = ""
            if self.dejavu_mic:
                # their reader
                mic_res = self.djv.djv.recognize(MicrophoneRecognizer, seconds=1)
                if mic_res is not None:
                    fname = mic_res['song_name']
            else:
                # our reader
                while len(self.buff) == 0:
                    self.buff = self.rwav.getWindowBuffer()
                fname = self.djv.recognise(self.buff)
            song, verse, part = self.fname_to_parts(self.get_verse(fname))
            self.disp.update_text(self.db.get_lyrics(song, verse, part))
            
    def fname_to_parts(self, fname):
        song = "unknown"
        verse = 0
        part = 0
        if fname is not None:
            match = re.match('^([a-z_]+)-v([0-9]+)-p([0-9]+)$', fname)
            if match is not None:
                song = match.group(1)
                verse = int(match.group(2))
                part = int(match.group(3))
        return song, verse, part

    def get_verse(self, value):
        self.dq.append(value)
        self.last_song
        dq_summary = {s: sum(1 for i in self.dq if i == s) for s in self.dq}
        modal_song = sorted(dq_summary.iteritems(), key=lambda x:x[1], reverse=True)[0]
        if modal_song[1] < len(self.dq) / 2.0:
            return self.last_song
        else:
            self.last_song = modal_song[0]
            return modal_song[0]

    def import_prints(self, dirs, ext):
        for d in dirs:
            self.djv.fingerprint(d, ext)
        pass



import argparse
parser = argparse.ArgumentParser(description='Song presentation software that advances based on audio analysis')
parser.add_argument('--import_dir', metavar='DIR', nargs='*', help='Any directories that you with to import fingerprints of')
parser.add_argument('--import_ext', metavar='EXT', nargs='*', help='Any directories that you with to import fingerprints of', default=['.wav'])
parser.add_argument('--dejavu_mic', action='store_true', help='Any directories that you with to import fingerprints of', default=False)
args = parser.parse_args()

lazyworship = LazyWorship(args.dejavu_mic)
if args.import_dir is not None:
    lazyworship.import_prints(args.import_dir, args.import_ext)
lazyworship.run()
