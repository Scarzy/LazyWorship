import json
from dejavu import Dejavu
from dejavu.recognize import BaseRecognizer

class StreamRecogniser(BaseRecognizer):
    def __init__(self, dejavu):
        super(StreamRecogniser, self).__init__(dejavu)
    
    def recognise_stream(self, stream):
        match = self._recognize(*stream)
        return match

class dejavu_handler():
    def __init__(self):
        with open("dejavu.cnf") as f:
            config = json.load(f)
        self.djv = Dejavu(config)
    
    def fingerprint(self, dir, ext):
        self.djv.fingerprint_directory(dir, ext)
    
    def recognise(self, stream):
        song = djv.recognize(StreamRecogniser)
        
    
