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
        self._name = self.struct[0]
        self._lyrics = self.struct[1]
        self._features = self.struct[2]
    def get_lyric(self, index):
        return self._lyrics[index]
    def get_features(self):
        return self._features
    def get_lyric_by_freq(self, freq):
        for f in self._features:
            if f['freq'] == freq:
                return self.get_lyric(f['lyric'])

if __name__ == "__main__":
    print "Running standalone"
    st = store('amazing_grace')
    if False: #write
        st.add_lyrics("Amazing grace, How sweet the sound\nThat saved a wretch like me.\nI once was lost, but now am found,\nWas blind, but now I see.")
        st.add_lyrics("'Twas grace that taught my heart to fear,\nAnd grace my fears relieved.\nHow precious did that grace appear\nThe hour I first believed.")
        st.add_lyrics("Through many dangers, toils and snares\nI have already come,\n'Tis grace has brought me safe thus far\nAnd grace will lead me home.")
        st.add_lyrics("The Lord has promised good to me\nHis word my hope secures;\nHe will my shield and portion be,\nAs long as life endures.")
        st.add_lyrics("Yea, when this flesh and heart shall fail,\nAnd mortal life shall cease\nI shall possess within the veil,\nA life of joy and peace.")
        st.add_lyrics("When we've been there ten thousand years\nBright shining as the sun,\nWe've no less days to sing God's praise\nThan when we've first begun.")
        import random, math
        for i in range(100):
            st.add_features(random.random()*100, [random.random()*1000 for j in range(10)], math.floor(random.random() * 6))
        st.write()
    else:
        st.read('amazing_grace.json')
        print st._name
        print st.get_lyric(0)
