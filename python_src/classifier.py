from __future__ import division

import collections
import itertools
import json
import matplotlib.axes
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d
import numpy
import numpy.fft
import sklearn.decomposition
import sklearn.mixture
import struct
import wave

LYRIC_WEIGHT = 250000000
TIME_WEIGHT = 1000000000

# Represents a Lyric Section
#  index is the index number in the collection
#  time_indicies is a tuple of 2-tuples of start and end time of the lyric section in the song
#  text is the text to display on the screen
LyricSection = collections.namedtuple('LyricSection', ('index', 'time_indicies', 'text'))

# Represents a DataPoint in our feature space (i.e. a window of the audio we've heard)
DataPoint = collections.namedtuple('DataPoint', ('fft', 'last_window_lyric_index', 'last_actual_lyric_index', 'relative_time_ratio'))

class SongClassifier(object):
    def __init__(self, lyrics):
        self.lyrics = lyrics
        self.last_actual_lyric = -1
        self.last_window_lyric = -1
        self.first_segment_length = -1
        self.current_segment_start = 0
        self.pca = None
        self.gmm = None

    def fit(self, training_data):
        lyric_feature_coordinates = {l: list(_data_point_to_feature_coordinates(dp) for dp in data) for l, data in training_data.iteritems()}
        pca_data = list(itertools.chain(*lyric_feature_coordinates.values()))

        self.pca = sklearn.decomposition.PCA(n_components=20)
        self.pca.fit(pca_data)

        lyric_gmm_data = {l: self.pca.transform(d) for l, d in lyric_feature_coordinates.iteritems()}
        lyric_means = [ld.mean() for ld in lyric_gmm_data.values()]

        self.gmm = sklearn.mixture.GMM(len(lyrics), covariance_type='full')
        self.gmm.means_ = lyric_means
        gmm_data = numpy.array([itertools.chain(list(v) for v in lyric_gmm_data.values())])

        self.gmm.fit(gmm_data)

    def predict(self, window, start_time):
        predict_last_window_lyric = (self.last_window_lyric * LYRIC_WEIGHT)
        predict_last_actual_lyric = self.last_actual_lyric * LYRIC_WEIGHT

        predict_relative_time = start_time - self.current_segment_start
        predict_relative_time_ratio = predict_relative_time / (self.first_segment_length if self.first_segment_length != -1 else self.lyrics[0].time_indicies[0][1]) * TIME_WEIGHT

        fft = numpy.fft.fft(window)
        predict_dp = DataPoint(fft, predict_last_window_lyric, predict_last_actual_lyric, predict_relative_time)
        predict_feature_coordinate = _data_point_to_feature_coordinates(predict_dp)

        gmm_data = self.pca.transform(predict_feature_coordinate)
        lyric_index = self.gmm.predict(gmm_data)

        if lyric_index != self.last_window_lyric and self.last_window_lyric != -1:
            self.last_actual_lyric = self.last_window_lyric
            if self.first_segment_length == -1:
                self.first_segment_length = absolute_time
        self.last_window_lyric = lyric_index

        return lyric_index

# A list of 3-tuples of start time, end time and lyrics text
    
def generate_training_data(wav_file_path, lyrics, generate_fft_images=False, generate_pca_image=False):
    window_size_frames = 40000
    window_interval = int(window_size_frames / 10)

    frame_rate, windows = _load_wav_file(wav_file_path, window_size_frames, window_interval)

    window_size_ms = window_size_frames / frame_rate
    
    # Dictionary of lyric to list of data points
    lyric_data = {l: [] for l in lyrics}
    last_data_point_lyric = None

    for absolute_time, window in windows:
        # FFT each window to get the frequencies
        window_fft = numpy.absolute(numpy.fft.fft(window))

        # Remove anything below 20Hz because humans can't hear that
        window_fft[0:19] = (0,) * 19

        # Remove anything above 5kHz because intruments don't go that high
        window_fft = window_fft[:5000]

        if generate_fft_images:
            plt.subplot(121)
            plt.plot(window)
            plt.subplot(122)
            plt.plot(window_fft)
            plt.show()
            plt.savefig('fft_{0}.png'.format(i))
            plt.clf()

        # Get the lyrics
        lyric, lyric_start_time, lyric_end_time = _find_lyric(lyrics, absolute_time)

        # Compute the time we are at in the current lyric, as a ratio of the length of the first lyric
        relative_time = absolute_time - lyric_start_time
        relative_time_ratio = relative_time / (lyric_end_time - lyric_start_time)

        # Get the verse of the last window and the last verse we were in
        verses = ((last_data_point_lyric.index if last_data_point_lyric is not None else 0),
                  ((lyric.index - 1)))
        verses = numpy.array(verses)
        data_point = DataPoint(window_fft, verses[0], verses[1], relative_time_ratio)
            
        lyric_data[lyric].append(data_point)
        last_data_point_lyric = lyric

    if generate_pca_image:
        # Use Principle Component Analysis to get the 3 dimensions with the greatest variance
        lyric_feature_coordinates = {l: list(_data_point_to_feature_coordinates(dp) for dp in data) for l, data in lyric_data.iteritems()}
        pca_data = list(itertools.chain(*lyric_feature_coordinates.values()))
        pca_3d = sklearn.decomposition.PCA(n_components=3)
        pca_3d.fit(pca_data)

        # Now graph them
        transformed_lyric_data = {l: pca_3d.transform(data).transpose() for l, data in lyric_feature_coordinates.iteritems()}
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        for (l, data), color in zip(transformed_lyric_data.iteritems(), 'cb'):
            ax.scatter(*data, c=color)
        plt.savefig('pca_3d.png')

    return lyric_data

    pca = sklearn.decomposition.PCA(n_components=20)
    pca.fit(pca_data)

    lyric_gmm_data = {l: pca.transform(d) for l, d in lyric_data.iteritems()}
    lyric_means = [ld.mean() for ld in lyric_gmm_data.values()]
    return lyric_means, list(itertools.chain(*lyric_gmm_data.values()))


    gmm = sklearn.mixture.GMM(len(lyrics), covariance_type='full')
    gmm.means_ = lyric_means
    gmm.fit(itertools.chain(lyric_gmm_data.values()))

    last_actual_lyric = -1
    last_window_lyric = -1
    first_segment_length = -1
    current_segment_start = 0
    errors = 0
    for i, (lyric, fft) in enumerate(ffts):
        fft[-3] = (last_window_lyric * LYRIC_WEIGHT)
        fft[-2] = last_actual_lyric * LYRIC_WEIGHT

        absolute_time = i * windowSizeFrames / frameRate
        relative_time = absolute_time - current_segment_start
        relative_time_ratio = relative_time / (first_segment_length if first_segment_length != -1 else lyrics[0][2])

        fft[-1] = relative_time_ratio * TIME_WEIGHT

        gmm_data = pca.transform(fft)
        lyric_index = gmm.predict(gmm_data)
        if lyrics[lyric_index] != lyric:
            print 'Failed to predict {0} (chose {1} instead of {2})'.format(i, lyric_index, lyric[0])
            errors += 1

        if lyric_index != last_window_lyric and last_window_lyric != -1:
            last_actual_lyric = last_window_lyric
            if first_segment_length == -1:
                first_segment_length = absolute_time
        last_window_lyric = lyric_index

    print 'Made {0} errors'.format(errors)


def _find_lyric(lyrics, time):
    for l in lyrics:
        for start, end in l.time_indicies:
            if time >= start and time < end:
                return l, start, end
    else:
        raise KeyError('Couldn\'t find a lyric at {0}'.format(time))


def _data_point_to_feature_coordinates(dp):
    return numpy.concatenate((dp.fft, numpy.array([dp.last_window_lyric_index * LYRIC_WEIGHT, dp.last_actual_lyric_index * LYRIC_WEIGHT, dp.relative_time_ratio * TIME_WEIGHT])))


def _load_wav_file(wav_file_path, window_size_frames, window_interval):
    wave_file = wave.open(wav_file_path, 'r')
    try:
        length = wave_file.getnframes()
        wave_data = wave_file.readframes(length)
        wave_data = struct.unpack('<' + ('h' * int(len(wave_data) / 2)), wave_data)
    finally:
        wave_file.close()

    def window_generator():
        for i in xrange(0, length - window_size_frames, window_interval):
            yield i / frame_rate, wave_data[i:(i + window_size_frames)]

    frame_rate = wave_file.getframerate()

    return frame_rate, window_generator()

if __name__ == '__main__':
    training_file = 'chris_tomlin-amazing_grace-training.wav'
    lyrics = [LyricSection(0, ((0, 15.5),), 'Amazing grace how sweet the sound, that saved a wretch like me'),
              LyricSection(1, ((15.5, 31),), 'I once was lost, but now am found.  Was blind but now I see.')]
    td = generate_training_data(training_file, lyrics, generate_pca_image=True)

    classifier = SongClassifier(lyrics)
    classifier.fit(td)

    window_size_frames = 40000
    window_interval = int(window_size_frames / 10)

    frame_rate, windows = _load_wav_file(training_file, window_size_frames, window_interval)
    errors = 0
    for i, (absolute_time, w) in enumerate(windows):
        correct_lyric, _, _ = _find_lyric(lyrics, absolute_time)
        predicted_lyric = classifier.predict(w, absolute_time)

        if correct_lyric.index != predicted_lyric:
            errors += 1
            print 'Failed to correctly predict {0] (guessed {1}, expected {2})'.format(i, predicted_lyric, correct_lyric)

    print 'Made {0} errors'.format(errors)