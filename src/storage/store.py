import json

class store():
    def __init__(self, name):
        self._name = name
        self._lyrics = []
        self._features = []
    def add_lyrics(self, lyric):
        self._lyrics.append(lyric)
    def add_features(self, vol, freq, lyric=None):
        self._features.append({'vol': vol, 'freq': freq, 'lyric': lyric})
    def write(self):
        self.fh = open('dbs/' + self._name + '.json', 'w')
        self.fh.write(json.dumps([self._name, self._lyrics, self._features]))
        self.fh.close()
    def read(self, filename):
        self.fh = open('dbs/' + filename, 'r')
        self.struct = json.loads(self.fh.read())
        self._name = self.struct['name']
        self._lyrics = self.struct['lyrics']
        self._features = self.struct['features']
    def get_lyric(self, index):
        return self._lyrics[index]
    def get_features(self):
        return self._features
    def get_lyric_by_freq(self, freq):
        for f in self._features:
            if f['freq'] == freq:
                return self.get_lyric(f['lyric'])
