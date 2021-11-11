from suaBibSignal import signalMeu
import numpy as np
import matplotlib.pyplot as plt
from funcoes_LPF import LPF
import sounddevice as sd
import soundfile as sf

mySignal = signalMeu()
audio = mySignal.read_sound_file("./p8_modulacao_AM/voz.wav")

yAudio = audio[:, 1]
samplesAudio = len(yAudio)

yMax = np.max(list(map(lambda x: abs(x), yAudio)))
print(f"Intesidade máxima: {yMax}")

yAudioNormalizado = list(map(lambda x: x / yMax, yAudio))

#! PLOTS:
# @ -- tempo
plt.figure(figsize=(10, 6))
plt.subplot(3, 1, 1)
plt.plot(yAudio)
plt.title("Sinal de áudio original")
plt.ylabel("intensidade")

plt.subplot(3, 1, 2)
plt.plot(yAudioNormalizado)
plt.title("Sinal de áudio original (normalizado)")
plt.ylabel("intensidade")

plt.subplot(3, 1, 3)
mySignal.plotFFT(yAudio, 44100, "Fourrier do sinal original")
plt.axis([-1, 6000, -20, 600])

plt.subplots_adjust(hspace=0.5)
plt.show()

# * Filtrar frequências acima de 4 Khz
print("filtrando áudio...")
yAudioFiltrado = LPF(yAudio, 4000, 44100)
# @ -- fourier
plt.figure(figsize=(10, 6))
plt.subplot(3, 1, 1)
plt.plot(yAudioNormalizado)
plt.title("Sinal de áudio original (normalizado)")

plt.subplot(3, 1, 2)
plt.plot(yAudioFiltrado)
plt.title("Sinal do áudio filtrado (no domínio do tempo)")

plt.subplot(3, 1, 3)
mySignal.plotFFT(yAudioFiltrado, 44100, "Fourier de áudio filtrado")
plt.axis([-1, 6000, -20, 600])

plt.subplots_adjust(hspace=0.5)
plt.show()

#! Reproduzir o áudio filtrado
sd.play(yAudioFiltrado, samplerate=44100)
sd.wait()

#! Modulação AM
# * Gerar o sinal de portadora
xp = np.linspace(0.0, len(yAudioFiltrado) / 44100, len(yAudioFiltrado))
yp = 1 * np.sin(14000 * xp * 2 * np.pi)

# $ y_modulado = (1 + yAudio)*yp
y_modulado = [(1 + yAudioNormalizado[i]) * yp[i] for i in range(len(yAudio))]
plt.figure(figsize=(10, 6))
plt.plot(y_modulado)
plt.title("Sinal de áudio modulado (domínio do tempo)")
plt.show()

# * Ouvir sinal modulado
sd.play(y_modulado, samplerate=44100)
sd.wait()

sf.write("p8_modulacao_AM/modulado.wav", y_modulado, samplerate=44100)
