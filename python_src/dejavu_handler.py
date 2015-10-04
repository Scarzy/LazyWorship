import json
import warnings
from dejavu import Dejavu
from dejavu.recognize import BaseRecognizer, FileRecognizer

warnings.filterwarnings("ignore")

class StreamRecogniser(BaseRecognizer):
    def __init__(self, dejavu):
        super(StreamRecogniser, self).__init__(dejavu)
    
    def recognise_stream(self, stream):
        chan_stream = [stream[0:-1], stream[0:-1]]
        match = self._recognize(*chan_stream)
        return match
    
    def recognize(self, stream):
        self.recognise_stream(stream)

class dejavu_handler():
    def __init__(self, dejavu_mic=False):
        with open("dejavu.cnf") as f:
            config = json.load(f)
        self.djv = Dejavu(config)
    
    def fingerprint(self, dir, ext):
        self.djv.fingerprint_directory(dir, ext)
    
    def recognise(self, stream):
        song = self.djv.recognize(StreamRecogniser, stream)
        
    
