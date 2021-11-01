#!/usr/bin/env python3
"""Show a text-mode spectrogram using live microphone data."""

#Importe todas as bibliotecas
from suaBibSignal import *
import time
import peakutils

#funcao para transformas intensidade acustica em dB
def todB(s):
    sdB = 10*np.log10(s)
    return(sdB)


def main():
 
    #declare um objeto da classe da sua biblioteca de apoio (cedida)    
    mySignal = signalMeu()
    #declare uma variavel com a frequencia de amostragem, sendo 44100
    freq_amostragem = 44100
    #voce importou a bilioteca sounddevice como, por exemplo, sd. entao
    # os seguintes parametros devem ser setados:
    
    sd.default.samplerate = freq_amostragem #taxa de amostragem
    sd.default.channels = 2  #voce pode ter que alterar isso dependendo da sua placa
    duration = 5 #s #tempo em segundos que ira aquisitar o sinal acustico captado pelo mic


    # faca um printo na tela dizendo que a captacao comecará em n segundos. e entao 
    print("A Captação de Áudio começará em 2 seg")
    time.sleep(2)
    #use um time.sleep para a espera
   
    #faca um print informando que a gravacao foi inicializada
    print("Iniciando gravação...")
   
    #declare uma variavel "duracao" com a duracao em segundos da gravacao. poucos segundos ... 
    duracao = 5
    #calcule o numero de amostras "numAmostras" que serao feitas (numero de aquisicoes)
    numAmostras = freq_amostragem * duracao
   
    audio = sd.rec(int(numAmostras), freq_amostragem, channels=1)
    sd.wait()
    print("...     FIM")
    
    #analise sua variavel "audio". pode ser um vetor com 1 ou 2 colunas, lista ...
    print(audio)
    #grave uma variavel com apenas a parte que interessa (dados)
    dados = [value[0] for value in audio]

    # use a funcao linspace e crie o vetor tempo. Um instante correspondente a cada amostra!
    inicio = 0
    fim = 5 
    numPontos = numAmostras
    t = np.linspace(inicio,fim,numPontos)

    # plot do gravico  áudio vs tempo!
    plt.figure("Sinal captado ao longo do tempo")
    plt.plot(t, dados)
    plt.grid()
    plt.show()
   
    
    ## Calcula e exibe o Fourier do sinal audio. como saida tem-se a amplitude e as frequencias
    xf, yf = mySignal.calcFFT(dados, freq_amostragem)
    plt.figure("F(y)")
    plt.plot(xf,yf)
    plt.grid()
    plt.title('Fourier audio')
    

    #esta funcao analisa o fourier e encontra os picos
    #voce deve aprender a usa-la. ha como ajustar a sensibilidade, ou seja, o que é um pico?
    #voce deve tambem evitar que dois picos proximos sejam identificados, pois pequenas variacoes na
    #frequencia do sinal podem gerar mais de um pico, e na verdade tempos apenas 1.
   
    index = peakutils.indexes(y=yf,thres=0.5, min_dist =1, thres_abs= False)
    
    #printe os picos encontrados! 
    print(index)
    
    #encontre na tabela duas frequencias proximas às frequencias de pico encontradas e descubra qual foi a tecla
    freq_detectadas = []
    for i in index:
        print(f"-Pico {i}: freq: {int(round(xf[i]))}")
        freq_detectadas.append(int(round(xf[i])))
    
    tecla_detectada = ''
    #print a tecla.
    for tecla, frequencias in mySignal.DTMF_matrix.items():
        if set(freq_detectadas) == set(frequencias):
            print(f"Frequências detectadas {set(freq_detectadas)} correspondem à tecla {tecla}")
            tecla_detectada = tecla
  
    print(f"Tecla detectada: {tecla_detectada}")
    
    ## Exibe gráficos
    plt.show()

if __name__ == "__main__":
    main()
