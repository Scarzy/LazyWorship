"""PyAudio example: Record a few seconds of audio and save to a WAVE file."""

import pyaudio
import wave
import time
import threading
import struct
import numpy as np

condition = threading.Condition()


class AudioRecorder:

    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100

    def __init__(self):

        self.p = pyaudio.PyAudio()

        self.stream = self.p.open(format=self.FORMAT,
                        channels=self.CHANNELS,
                        rate=self.RATE,
                        input=True,
                        stream_callback=self.callback)

        self.stream.start_stream()

        self.windowStepSizeSecs = 0.1
        self.windowSizeSecs = 1

        self.windowStepSize = int(self.windowStepSizeSecs * self.RATE)
        self.windowSize = int(self.windowSizeSecs * self.RATE)

        self.windowBuffer = []

        #print("* recording")

    def callback(self, in_data, frame_count, time_info, status):
        #print '* frame count = ', frame_count
        data = np.fromstring(in_data, dtype=np.int16)
        condition.acquire()
        self.windowBuffer.extend(data)
        #print 'length windowBuffer = ', len(self.windowBuffer)
        condition.notifyAll()
        condition.release()
        return (in_data, pyaudio.paContinue)

    def setWindowStepSizeSecs(self, value):
        self.windowStepSizeSecs = value
        self.windowStepSize = int(self.windowStepSizeSecs * self.RATE)

    def setWindowSizeSecs(self, value):
        self.windowSizeSecs = value
        self.windowSize = int(self.windowSizeSecs * self.RATE)

    def getWindowBuffer(self):
        condition.acquire()
        condition.wait()
        condition.release()
        if(len(self.windowBuffer) >= self.windowSize):
            temp_my_buffer = list(self.windowBuffer[0:self.windowSize])
            discardSize = self.windowStepSize
            self.windowBuffer[0:discardSize] = []
            return temp_my_buffer
        else:
            return []

    def close(self):
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

if __name__ == "__main__":
    recorder = AudioRecorder()

    for i in range(0,100):
        buff = recorder.getWindowBuffer()
        print 'buff length = ', len(buff)

#    time.sleep(1)

#    for i in range(0,10):
 #       buff = recorder.getWindowBuffer()
  #      print 'buff length = ', len(buff)

    recorder.close()
