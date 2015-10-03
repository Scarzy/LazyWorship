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
    RECORD_SECONDS = 5

    def __init__(self):

        self.p = pyaudio.PyAudio()

        self.stream = self.p.open(format=self.FORMAT,
                        channels=self.CHANNELS,
                        rate=self.RATE,
                        input=True,
                        stream_callback=self.callback)

        self.stream.start_stream()

        self.my_buffer = []

        print("* recording")

    def callback(self, in_data, frame_count, time_info, status):
        print '* frame count = ', frame_count
        data = np.fromstring(in_data, dtype=np.int16)
        self.my_buffer.extend(data)
        print 'length in_data = ', len(self.my_buffer)
        condition.acquire()
        condition.notifyAll()
        condition.release()
        return (in_data, pyaudio.paContinue)

    def getBuffer(self):
        condition.acquire()
        condition.wait()
        condition.release()
        temp_my_buffer = list(self.my_buffer)
        self.my_buffer = []
        return temp_my_buffer

    def close(self):
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()


recorder = AudioRecorder()


for i in range(0,10):
    buff = recorder.getBuffer()
    print 'buff length = ', len(buff)

time.sleep(1)

for i in range(0,10):
    buff = recorder.getBuffer()
    print 'buff length = ', len(buff)

#frames = recorder.readChunks()

recorder.close()