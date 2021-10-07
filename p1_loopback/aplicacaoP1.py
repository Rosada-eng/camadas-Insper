#####################################################
# Camada Física da Computação
#Carareto
#11/08/2020
#Aplicação
####################################################


#esta é a camada superior, de aplicação do seu software de comunicação serial UART.
#para acompanhar a execução e identificar erros, construa prints ao longo do código! 


from serial import serial_for_url
from enlace import *
import time
import numpy as np

# voce deverá descomentar e configurar a porta com através da qual ira fazer comunicaçao
#   para saber a sua porta, execute no terminal :
#$   python -m serial.tools.list_ports
# se estiver usando windows, o gerenciador de dispositivos informa a porta

#use uma das 3 opcoes para atribuir à variável a porta usada
#serialName = "/dev/ttyACM0"           # Ubuntu (variacao de)
#serialName = "/dev/tty.usbmodem1411" # Mac    (variacao de)

#! ========= CONFIG ===========
serialName = "COM4"       
file_name = "apple"
file_format = "png"

def open_image_as_bytes(path):
    with open (path, "rb") as f:
        return f.read()

def save_bytes_as_image(bytes_file, file_name, file_format):
    try: 
        with open(f"p1_loopback/{file_name}-answer.{file_format}", "wb") as output:
            output.write(bytes_file)

            return True

    except:
        return False

def main():
    try:
        #declaramos um objeto do tipo enlace com o nome "com". Essa é a camada inferior à aplicação. Observe que um parametro
        #para declarar esse objeto é o nome da porta.
        com1 = enlace(serialName)
        
    
        # Ativa comunicacao. Inicia os threads e a comunicação serial 
        com1.enable()
        com1.fisica.flush() #% Limpa a memória
        #Se chegamos até aqui, a comunicação foi aberta com sucesso. Faça um print para informar.
        
        print("\033[32mComunicação iniciada!" + "\033[m")
        print("-------------------------")

        #! aqui você deverá gerar os dados a serem transmitidos. 
        # seus dados a serem transmitidos são uma lista de bytes a serem transmitidos. 
        # Gere esta lista com o nome de txBuffer.
        # Ela sempre irá armazenar os dados a serem enviados.
        
        txBuffer = open_image_as_bytes(f"p1_loopback/{file_name}.{file_format}")
        print (txBuffer)

        #faça aqui uma conferência do tamanho do seu txBuffer, ou seja, quantos bytes serão enviados.
        print(f"O Buffer a ser enviado tem tamanho: {len(txBuffer)}")     

        #! finalmente vamos transmitir os dados.
        # Para isso usamos a funçao sendData que é um método da camada enlace.
        # faça um print para avisar que a transmissão vai começar.
        # tente entender como o método send funciona!
        print("iniciando transmissão ...")

        # Cuidado! Apenas trasmitimos arrays de bytes! Nao listas!
        com1.sendData(np.asarray(txBuffer))
       
        # A camada enlace possui uma camada inferior, 
        # TX possui um método para conhecermos o status da transmissão
        # Tente entender como esse método funciona e o que ele retorna
        time.sleep(1)
        txStatus = com1.tx.getStatus()
        print("status:", txStatus)

        #! Agora vamos iniciar a recepção dos dados.
        # Se algo chegou ao RX, deve estar automaticamente guardado
        # Observe o que faz a rotina dentro do thread RX
        # print um aviso de que a recepção vai começar.
        print("iniciando recepção ...")
        
        #Será que todos os bytes enviados estão realmente guardadas? Será que conseguimos verificar?
        #Veja o que faz a funcao do enlaceRX  getBufferLen
        # rxBufferLen = com1.rx.getBufferLen()
        #acesso aos bytes recebidos
        txLen = len(txBuffer)
        print(txLen)
        # rxBuffer = com1.getData(txLen)
        rxBuffer, nRx = com1.getData(txLen)  #@ data, len(data)
        result = save_bytes_as_image(rxBuffer, file_name, file_format)
        print(f"Documento salvo com sucesso?: {result}")
        # print("recebeu {}" .format(rxBuffer))
            
    
        # Encerra comunicação
        print("-------------------------")
        print(f"\033[{32 if result== True else 31}m" + "Comunicação encerrada!" + "\033[m")
        print("-------------------------")
        com1.disable()
        
    except Exception as erro:
        print("ops! :-\\")
        print(erro)
        com1.disable()
        

    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()
