import wave, struct
import json

def getAmplitude(windowData):
    accumulator = 0
    for i in range(0, len(windowData)):
        accumulator += abs(windowData[i])
    amplitude = accumulator / len(windowData)
    return amplitude

def readWaveData(waveFile):
    # read wave data
    length = waveFile.getnframes()
    waveData = []
    for i in range(0, length):
        waveDataTemp = waveFile.readframes(1)
        data = struct.unpack("<h", waveDataTemp)
        #print int(data[0])
        waveData.append(int(data[0]))
    return (waveData, length)


waveFile = wave.open('sine.wav', 'r')

waveData, length = readWaveData(waveFile);

print 'length = ', length

frameRate = waveFile.getframerate()

print 'frame rate = ', frameRate

windowSizeMS = 100

windowSizeFrames = int((windowSizeMS * 0.001) * frameRate) + 1

print 'windowSizeFrames = ', windowSizeFrames

windowStart = 0
amplitudeList = []
while windowStart < length:
    window = waveData[windowStart:windowStart+windowSizeFrames]

    amplitudeList.append( getAmplitude(window) )

    windowStart += windowSizeFrames


for i in range(0, len(amplitudeList)):
  print amplitudeList[i]

sample = {'ObjectInterpolator': 1629,  'PointInterpolator': 1675, 'RectangleInterpolator': 2042}

with open('result.json', 'w') as fp:
    json.dump(sample, fp)