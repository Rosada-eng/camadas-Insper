import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
from scipy.fftpack import fft
from scipy import signal as window
import soundfile as sf


class signalMeu:
    def generateSin(self, freq, amplitude, time, fs):
        n = time * fs
        x = np.linspace(0.0, time, n)
        s = amplitude * np.sin(freq * x * 2 * np.pi)
        return (x, s)

    def calcFFT(self, signal, fs):
        # https://docs.scipy.org/doc/scipy/reference/tutorial/fftpack.html
        N = len(signal)
        W = window.hamming(N)
        T = 1 / fs
        xf = np.linspace(0.0, 1.0 / (2.0 * T), N // 2)
        yf = fft(signal * W)
        return (xf, np.abs(yf[0 : N // 2]))

    def plotFFT(self, signal, fs, plot_title):
        x, y = self.calcFFT(signal, fs)
        plt.plot(x, np.abs(y))
        plt.xlabel("frequency")
        plt.ylabel("intensity")
        plt.title(plot_title)

    def read_sound_file(self, filename):
        # leituara do arquivo audio
        fs = 44100  # taxqa de amostagem (sample rate)
        sd.default.samplerate = fs
        sd.default.channels = 1
        audio, samplerate = sf.read(filename)
        # sd.play(audio)
        # sd.wait()

        return audio
