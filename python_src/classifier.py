from __future__ import division

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

def getAmplitude(windowData):
    accumulator = 0
    for i in range(0, len(windowData)):
        accumulator += abs(windowData[i])
    amplitude = accumulator / len(windowData)
    return amplitude

def readWaveData(waveFile):
    # read wave data
    length = waveFile.getnframes()
    waveDataTemp = waveFile.readframes(length)
    waveData = struct.unpack('<' + ('h' * int(len(waveDataTemp) / 2)), waveDataTemp)
    return (waveData, length)

waveFile = wave.open('chris_tomlin-amazing_grace-training.wav', 'r')

waveData, length = readWaveData(waveFile)
#with open('wavedata.txt', 'w') as f:
#    f.write(str(waveData))

print 'length = ', length

frameRate = waveFile.getframerate()

print 'frame rate = ', frameRate

windowSizeMS = 100

windowSizeFrames = 40000
windowSizeMS = windowSizeFrames / waveFile.getframerate()

print 'windowSizeFrames = ', windowSizeFrames
print 'windowSizeMS = ', windowSizeMS

windowInterval = int(windowSizeFrames / 10)

# A list of 2-tuples of lyric and FFT
ffts = []

# A list of 3-tuples of start time, end time and lyrics text
lyrics = [(0, 0, 15.5, 'Amazing grace how sweet the sound, that saved a wretch like me'),
          (1, 15.5, 31, 'I once was lost, but now am found.  Was blind but now I see.')]
lyric_index = 0
bin_boundaries = ((20, 22), (22, 25), (25, 32), (32, 47), (47, 84), (84, 168), (168, 360), (360, 803), (803, 1821), (1821, 4200))

for i in xrange(0, length - windowSizeFrames, windowInterval):
    window = waveData[i:(i + windowSizeFrames)]

    # FFT each window to get the frequencies
    window_fft = numpy.absolute(numpy.fft.fft(window))

    # Remove anything below 20Hz because humans can't hear that
    window_fft[0:19] = (0,) * 19

    # Remove anything above 20kHz because humans can't hear that and it's just a reflection
    window_fft = window_fft[:5000]

    # Get the lyrics
    if lyrics[lyric_index][2] < i / frameRate:
        print "Moved to lyric {0} at {1}".format(lyric_index + 1, i)
        lyric_index += 1

    # Compute the time we are at in the current lyric, as a ratio of the length of the first lyric
    absolute_time = i / frameRate
    relative_time = absolute_time - lyrics[lyric_index][1]
    relative_time_ratio = relative_time / (lyrics[0][2] - lyrics[0][1])

    # Get the verse of the last window and the last verse we were in
    verses = ((ffts[-1][0][0] if i > 0 else 0) * LYRIC_WEIGHT,
              ((lyric_index - 1)) * LYRIC_WEIGHT,
              relative_time_ratio * TIME_WEIGHT)
    verses = numpy.array(verses)

    window_fft = numpy.concatenate((window_fft, verses))
    if False:
        plt.subplot(121)
        plt.plot(window)
        #ax2 = matplotlib.axes.Axes(fig, ax1.get_position())
        plt.subplot(122)
        plt.plot(fft_bins)
        plt.show()
        plt.savefig('fft_{0}.png'.format(i))
        plt.clf()
        break
    ffts.append((lyrics[lyric_index], window_fft))

pca_data = numpy.array([i[1] for i in ffts])
if False:
    pca_3d = sklearn.decomposition.PCA(n_components=3)
    pca_3d.fit(pca_data)

    lyric_data = [numpy.array([pca_3d.transform(d[1])[0] for i, d in enumerate(ffts) if d[0] == l]) for l in lyrics]
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    def get_component(data, index):
        return numpy.array([d[index] for d in data])

    transposed_lyric_data = [ld.transpose() for ld in lyric_data]
    ax.scatter(transposed_lyric_data[0][0], transposed_lyric_data[0][1], transposed_lyric_data[0][2], c='r')
    ax.scatter(transposed_lyric_data[1][0], transposed_lyric_data[1][1], transposed_lyric_data[1][2], c='b')
    plt.show()
    exit()

pca = sklearn.decomposition.PCA(n_components=20)
gmm_data = pca.fit_transform(pca_data)

lyric_data = [numpy.array([gmm_data[i] for i, d in enumerate(ffts) if d[0] == l]) for l in lyrics]
lyric_means = [ld.mean() for ld in lyric_data]
gmm = sklearn.mixture.GMM(len(lyrics), covariance_type='full')
gmm.means_ = lyric_means
gmm.fit(gmm_data)

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