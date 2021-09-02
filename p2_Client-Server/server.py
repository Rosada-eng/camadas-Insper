#
""" 
    Funcionamento: 
        O Server será inicializado e ficara ouvindo até detectar alguma
        mensagem do cliente, ouví-la e interpretá-la corretamente.
                msg --> RX #% receiver: COM3
"""

from enlaceRx import RX
from interfaceFisica import fisica 

serialName = "COM3"

# instancia física:
fisica = fisica(serialName)
# cria RX do servidor
server = RX(fisica)

# Abre a porta e limpa a memória
server.fisica.open()
server.fisica.flush()
server.threadStart()

# Inicia o looping esperando mensagem com o comando de leitura:
reader = server.checkBuffer()

print(f"\033[32m" + "Comunicação efetuada com sucesso!" + "\033[m")
print(reader)

#! Encerra o server
server.threadKill()
fisica.close()