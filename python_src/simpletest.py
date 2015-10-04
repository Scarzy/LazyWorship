import warnings
import json
import sys
import threading

USE_DISP = False

if USE_DISP:
    import display
    import gtk

warnings.filterwarnings("ignore")

from dejavu import Dejavu
from dejavu.recognize import FileRecognizer, MicrophoneRecognizer

# load config from a JSON file (or anything outputting a python dictionary)
with open("dejavu.cnf") as f:
    config = json.load(f)

if __name__ == '__main__':

    # create a Dejavu instance
    djv = Dejavu(config)

    # Fingerprint all the mp3's in the directory we give it
    djv.fingerprint_directory("/home/thomas/Documents/projects/LazyWorship/test_audio-nonfree/chris_tomlin-amazin_grace_verses", [".wav"])

    # Recognize audio from a file
#    song = djv.recognize(FileRecognizer, "mp3/Sean-Fournier--Falling-For-You.mp3")
#    print "From file we recognized: %s\n" % song
    if USE_DISP:
        disp = display.display()

    lines = {'0': "Amazing grace\nHow sweet the sound\nThat saved a wretch like me\nI once was lost, but now I'm found\nWas blind, but now I see",
             '1':"'Twas grace that taught my heart to fear\nAnd grace my fears relieved\nHow precious did that grace appear\nThe hour I first believed",
             '2': "The Lord has promised good to me\nHis word my hope secures\nHe will my shield and portion be\nAs long as life endures",
             '3': "The earth shall soon dissolve like snow\nThe sun forbear to shine\nBut God, Who called me here below,\nWill be forever mine.\nWill be forever mine.\nYou are forever mine.",
             'c0': "My chains are gone\nI've been set free\nMy God, my Savior has ransomed me\nAnd like a flood His mercy reigns\nUnending love, amazing grace",
             'c1': "My chains are gone\nI've been set free\nMy God, my Savior has ransomed me\nAnd like a flood His mercy reigns\nUnending love, amazing grace",
             'c2': "My chains are gone\nI've been set free\nMy God, my Savior has ransomed me\nAnd like a flood His mercy reigns\nUnending love, amazing grace"
             }

    # Or recognize audio from your microphone for `secs` seconds
    def process_djv():
        last_lyrics = 0
        while True:
            secs = 1
            song = djv.recognize(MicrophoneRecognizer, seconds=secs)
            if song is not None:
#                sys.stdout.write("\r%s" % song['song_name'])
#                sys.stdout.flush()
                if song['song_name'] == last_lyrics:
                    if USE_DISP:
                        disp.update_text(lines[song['song_name']])
                    else:
                        print lines[song['song_name']]
                last_lyrics = song['song_name']
    if USE_DISP:
        thread = threading.Thread(target=process_djv)
        thread.daemon = True
        thread.start()
        gtk.main()
    else:
        process_djv()
                
#        if song is None:
#            print "Nothing recognized -- did you play the song out loud so your mic could hear it? :)"
#        else:
#            print "From mic with %d seconds we recognized: %s\n" % (secs, song)

    # Or use a recognizer without the shortcut, in anyway you would like
#    recognizer = FileRecognizer(djv)
#    song = recognizer.recognize_file("mp3/Josh-Woodward--I-Want-To-Destroy-Something-Beautiful.mp3")
#    print "No shortcut, we recognized: %s\n" % song
