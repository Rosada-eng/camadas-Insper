
import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
from scipy.fftpack import fft
from scipy import signal as window



class signalMeu:
    def __init__(self):
        self.init = 0
        self.DTMF_matrix = {
            '1': [1209, 697],
            '2': [1336, 697],
            '3': [1477, 697],
            'A': [1633, 697],
            '4': [1209, 770],
            '5': [1336, 770],
            '6': [1477, 770],
            'B': [1633, 770],
            '7': [1209, 852],
            '8': [1336, 852],
            '9': [1477, 852],
            'C': [1633, 852],
            'X': [1209, 941],
            '0': [1336, 941],
            '#': [1477, 941],
            'D': [1633, 941],
        }

    def get_matrix_symbol(self, fx,fy):
        """ 
            Recebe um par de frequências e devolve o símbolo que 
            a soma forma
        """
        for signal, frequencies in self.DTMF_matrix.items():
            if [fx, fy] == frequencies:
                return signal

        return "Não houve match"            


    def get_matrix_frequencies(self, symbol):
        """ 
            Recebe um simbolo e devolve as frequências que o compõem
        """
        fx, fy = self.DTMF_matrix[symbol]

        return fx, fy

    def generateSin(self, freq, amplitude, time, fs):
        n = time*fs
        x = np.linspace(0.0, time, n)
        s = amplitude*np.sin(freq*x*2*np.pi)
        return (x, s)

    def calcFFT(self, signal, fs):
        # https://docs.scipy.org/doc/scipy/reference/tutorial/fftpack.html
        N  = len(signal)
        W = window.hamming(N)
        T  = 1/fs
        xf = np.linspace(0.0, 1.0/(2.0*T), N//2)
        yf = fft(signal*W)
        return(xf, np.abs(yf[0:N//2]))

    def plotFFT(self, signal, fs):
        x,y = self.calcFFT(signal, fs)
        plt.figure()
        plt.plot(x, np.abs(y))
        plt.title('Fourier')
