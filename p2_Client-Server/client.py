#
""" 
    Funcionamento: 
        O Cliente será inicializado e enviará uma mensagem para o servidor.
            TX --> msg #% Transmitter: COM4
"""

import numpy as np
import time
import random
from enlaceTx import TX
from interfaceFisica import Fisica, START_ORDER, END_ORDER

serialName = "COM4"

def run_client():
    try: 
        # instancia física:
        fisica = Fisica(serialName)
        # cria TX do cliente
        client = TX(fisica)

        # Abre a porta e limpa a memória
        client.fisica.open()
        client.threadStart()
        client.fisica.flush()

        """
            #$ STRATEGY:
            -- Enviar no início uma sequência específica de bytes informando o #@ início da transmissão
            -- Logo em seguida: enviar o tamanho em bytes da mensagem (2 unidades)
            -- Depois: enviar o número de comandos
            -- Depois: enviar uma sequência de "1" e "2" informando o tamanho de cada comando
            -- Fim: #@ byte de fim da transmissão 
            -- Checar se a mensagem recebida tem os tamanhos informado
        """

        commands_list = [b'\x00\xff', b'\x00', b'\x0f', b'\xf0', b'\xff\x00', b'\xff']

        # Número de comandos enviados:
        N_commands = random.randint(10, 30)

        # sequência de comandos a ser transmitida
        payload = random.choices(commands_list, k=N_commands)
        size_of_commands = [len(command) for command in payload]

        # Número de bytes presente na sequência de comandos
        n_bytes = "".join([str(x) for x in payload]).count("\\")
        """
        message = #! START_ORDER (6 bytes) >>
                #% nº de bytes no Payload (2 bytes) >>
                #% N = nº de comandos (1 byte) >> 
                #% [seq. de 1's e 2's informando tamanho de cada ordem] (13 bytes) >>
                
                __mensagem__ >>
                #! END_ORDER (6 bytes)
        """
        """
            #% STRATEGY p/ Sequência:
                => Escrever uma string com uma sequência de 1's e 2's
                    ex.: '12211122122121121212'  (20 dig)
                => converter para um inteiro e, em seguida, para bytes para ser enviada
                --> Para uma sequência de 30 2's, são necessários 13 bytes. 
                => Ao ler o conjunto de bytes, refazer o processo inverso
                => Ler número por número da string e separar os comandos conforme o tamanho dele (1 ou 2).
        """

        message = ( START_ORDER
                    + (n_bytes).to_bytes(2, byteorder='little')
                    + (N_commands).to_bytes(1, byteorder='little')
                    + int("".join([str(size) for size in size_of_commands])).to_bytes(13, "little")
                    
                    )

        for command in payload:
            message += command

        message += END_ORDER

        print("-- Preparando para enviar Dados -- ")
        print("\033[33m" + f"{N_commands} comandos |  | tamanho total da mensagem com protocolo: {len(message)}\n {message}" + "\033[m")

        client.sendBuffer(message)
        print("=> Dados enviados.")

        time.sleep(0.5)
        txStatus = client.getStatus()
        print("status:", txStatus)


        #! Encerra o client
        client.threadKill()
        fisica.close()

    except Exception as erro:
        print("Não foi possível iniciar a comunicação do client")
        print(erro)

if __name__ == "__main__":
    run_client()
