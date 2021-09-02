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
from interfaceFisica import fisica, START_ORDER, END_ORDER

serialName = "COM4"

# instancia física:
fisica = fisica(serialName)
# cria TX do cliente
client = TX(fisica)

# Abre a porta e limpa a memória
client.fisica.open()
client.fisica.flush()
client.threadStart()

# Envia a primeira mensagem para o servidor:
# sendData (array (bytes(data))) --> tx.sendBuffer(data)

"""
    #$ STRATEGY:
    -- Enviar no início uma sequência específica de bytes: --> Início de transmissão
    -- próximo byte: Tamanho da transmissão
    -- Após passar o Tamanho informado, checar último byte --> Fim de Transmissão
    -- Se coincidir Byte de Fim com o Tamanho de bytes lidos, considera a leitura feita
    -- Se não coincidir, apenas descarta a leitura e volta a ouvir pelo #@ byte de Início.
"""

commands = [b'\x00\xff', b'\x00', b'\x0f', b'\xf0', b'\xff\x00', b'\xff']
n_commands = random.randint(10, 30)

orders = random.choices(commands, k=n_commands)

# Número de bytes presente na sequência de comandos
orders_size = "".join([str(x) for x in orders]).count("\\")
# Mesmo número, em formato de bytes
n_bytes =  (orders_size).to_bytes(2, byteorder='little')

message = START_ORDER + n_bytes
for order in orders:
    message += order

message += END_ORDER
print("-- Preparando para enviar Dados -- ")
print("\033[33m" + f"{n_commands} comandos | size: {orders_size}\n {message}" + "\033[m")

client.sendBuffer(message)
print("=> Dados enviados.")

time.sleep(0.5)
txStatus = client.getStatus()
print("status:", txStatus)


#! Encerra o client
client.threadKill()
fisica.close()