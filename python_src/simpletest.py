import collections
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
    print 'Fingerprinting...'
    djv.fingerprint_directory("..\\audio", [".wav"])

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
        dq = collections.deque(maxlen=5)
        while True:
            secs = 1
            song = djv.recognize(MicrophoneRecognizer, seconds=secs)
            song_name = song['song_name'] if song is not None else None
            
            dq.append(song_name)
            dq_summary = {s: sum(1 for i in dq if i == s) for s in dq}
            print dq_summary, 
            modal_song = sorted(dq_summary.iteritems(), key=lambda x:x[1], reverse=True)[0]
            print modal_song
            if modal_song[1] < len(dq) / 2.0:
                print 'No consensus'
                continue

            modal_song_name = modal_song[0]

            if modal_song_name is not None:
#                sys.stdout.write("\r%s" % song['song_name'])
#                sys.stdout.flush()
                if modal_song_name != last_lyrics:
                    if USE_DISP:
                        disp.update_text(lines[modal_song_name])
                    else:
                        print lines[modal_song_name]
                last_lyrics = modal_song_name
            else:
                print '.', 
    if USE_DISP:
        thread = threading.Thread(target=process_djv)
        thread.daemon = True
        thread.start()
        gtk.main()
    else:
        print 'Running recognition'
        process_djv()
                
#        if song is None:
#            print "Nothing recognized -- did you play the song out loud so your mic could hear it? :)"
#        else:
#            print "From mic with %d seconds we recognized: %s\n" % (secs, song)

    # Or use a recognizer without the shortcut, in anyway you would like
#    recognizer = FileRecognizer(djv)
#    song = recognizer.recognize_file("mp3/Josh-Woodward--I-Want-To-Destroy-Something-Beautiful.mp3")
#    print "No shortcut, we recognized: %s\n" % song
