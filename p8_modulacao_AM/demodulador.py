from suaBibSignal import signalMeu
import numpy as np
import matplotlib.pyplot as plt
from funcoes_LPF import LPF
import sounddevice as sd
import soundfile as sf

mySignal = signalMeu()
yAudio_modulado = mySignal.read_sound_file("./p8_modulacao_AM/modulado.wav")

#! Verificando as frequências do modulado (Fourrier)
plt.figure(figsize=(10, 6))
plt.subplot(2, 1, 1)
mySignal.plotFFT(yAudio_modulado, fs=44100, plot_title="Fourrier do sinal modulado")

plt.subplot(2, 1, 2)
mySignal.plotFFT(
    yAudio_modulado, fs=44100, plot_title="Fourrier do sinal modulado (zoom)"
)
plt.axis([10000, 18000, 0, 500])

plt.subplots_adjust(hspace=0.5)
plt.show()

#! Demodular
xp = np.linspace(0.0, len(yAudio_modulado) / 44100, len(yAudio_modulado))
yp = 1 * np.sin(14000 * xp * 2 * np.pi)
# $ y_demo = y_modulado * y_portadora
y_demodulado = [yAudio_modulado[i] * yp[i] for i in range(len(yAudio_modulado))]

print("filtrando audio demodulado...")
print("Aumente o volume para ouvir o audio demodulado!")
y_filtrado_demodulado = LPF(y_demodulado, 4000, 44100)
sd.play(y_filtrado_demodulado, samplerate=44100)
sd.wait()


#! Print dos sinais demodulados
plt.figure(figsize=(10, 6))

plt.subplot(2, 1, 1)
mySignal.plotFFT(y_demodulado, 44100, "Fourier do sinal demodulado")

plt.subplot(2, 1, 2)
mySignal.plotFFT(
    y_filtrado_demodulado, 44100, "Fourier do sinal demodulado (filtrado e c/ zoom)"
)
plt.axis([0, 6000, 0, 400])

plt.subplots_adjust(hspace=0.5)
plt.show()
