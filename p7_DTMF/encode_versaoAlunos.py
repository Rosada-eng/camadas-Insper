

#importe as bibliotecas
import sys
import numpy as np
import sounddevice as sd
from matplotlib import pyplot as plt
from scipy import signal
from suaBibSignal import signalMeu


def signal_handler(signal, frame):
        print('You pressed Ctrl+C!')
        sys.exit(0)

#converte intensidade em Db, caso queiram ...
def todB(s):
    sdB = 10*np.log10(s)
    return(sdB)

def main():
    print("Inicializando encoder")
    
    #declare um objeto da classe da sua biblioteca de apoio (cedida)   
    mySignal = signalMeu()
    #declare uma variavel com a frequencia de amostragem, sendo 44100
    freq_amostragem = 44100
    # voce importou a bilioteca sounddevice como, por exemplo, sd. entao
    # os seguintes parametros devem ser setados:
    
    #tempo em segundos que ira emitir o sinal acustico 
    duration = 5 #s 
      
    #relativo ao volume. Um ganho alto pode saturar sua placa... comece com .3    
    gainX  = 0.3
    gainY  = 0.3


    print("Gerando Tons base")
    
    #printe a mensagem para o usuario teclar um numero de 0 a 9. 
    #nao aceite outro valor de entrada.
    NUM = ""
    while NUM not in np.array(range(0,10)): 
        NUM = int(input('Dige um numero de 0 a 9:  '))

    #gere duas senoides para cada frequencia da tabela DTMF ! Canal x e canal y 
    print("Gerando Tom referente ao símbolo : {}".format(NUM))
    fx,fy = mySignal.get_matrix_frequencies(str(NUM))

    print(f"As frequências obtidas são: {fx} Hz e {fy} Hz")

    #use para isso sua biblioteca (cedida)
    #obtenha o vetor tempo tb.
    #deixe tudo como array
    t = np.linspace(-duration/2, duration/2, duration*freq_amostragem)

        
    #construa o sunal a ser reproduzido. nao se esqueca de que é a soma das senoides
    tx,yx = mySignal.generateSin(freq=fx, amplitude= 1.0, time=duration, fs=freq_amostragem)
    ty,yy = mySignal.generateSin(freq=fy, amplitude= 1.0, time=duration, fs=freq_amostragem)

    y = yx + yy
    #printe o grafico no tempo do sinal a ser reproduzido

    plt.figure()
    plt.plot(t, y, '.-')
    plt.title(f'Soma de sinais com frequências \nf= {fx} Hz e {fy} Hz')
    plt.xlabel('tempo')
    # Exibe gráficos
    plt.show()
    
    # reproduz o som
    tone = []
    for i in range(len(y)):
        tone.append([tx[i], y[i]])
    sd.play(tone, freq_amostragem)
    # aguarda fim do audio
    sd.wait()

if __name__ == "__main__":
    main()
