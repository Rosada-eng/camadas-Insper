#
""" 
    Funcionamento: 
        O Cliente será inicializado e enviará uma mensagem para o servidor.
            TX --> msg #% Transmitter: COM4
"""

import numpy as np
import time
from enlaceTx import TX
from interfaceFisica import fisica 

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


from data import b_img
data = b_img
data_as_array = np.asarray(data)
print("-- Preparando para enviar Dados -- ")
client.sendBuffer(data_as_array)

print("=> Dados enviados.")
time.sleep(1)
txStatus = client.getStatus()

print("status:", txStatus, "tamanho:", len(data))


#! Encerra o client
client.threadKill()
fisica.close()