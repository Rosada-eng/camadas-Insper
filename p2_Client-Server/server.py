#
""" 
    Funcionamento: 
        O Server será inicializado e ficara ouvindo até detectar alguma
        mensagem do cliente, ouví-la e interpretá-la corretamente.
                msg --> RX #% receiver: COM3
"""

from enlaceRx import RX
from interfaceFisica import Fisica 

serialName = "COM3"
def run_server():
    try:
        # instancia física:
        fisica = Fisica(serialName)
        # cria RX do servidor
        server = RX(fisica)

        # Abre a porta e limpa a memória
        server.fisica.open()
        server.fisica.flush()
        server.threadStart()

        # Inicia o looping esperando mensagem com o comando de leitura:
        readed, orders = server.checkBuffer()

        print(f"\033[32m" + "Comunicação efetuada com sucesso!" + "\033[m" + "\n")
        print(f"\033[34m" + f" - Pacote recebido ({(len(orders))} comandos):\n{readed}" + "\033[33m" +  f"\n\n - Comandos identificads: \n{orders}" + "\033[m")

        #! Encerra o server
        server.threadKill()
        fisica.close()

    except Exception as erro:
        print("Não foi possível iniciar a comunicação do server")
        print(erro)

if __name__ == "__main__":
    run_server()