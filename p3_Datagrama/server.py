#
""" 
    Funcionamento: 
        1- O Server será inicializado e ficara ouvindo até detectar um pedido de transmissão
        2- O Server responderá se está #$ disponível ou ocupado
        3- Caso esteja disponível --> iniciará-se a comunicação
        4- Recebe pacote por pacote e faz uma série de checagens:
            4.1 - Checa o número do pacote: deve ser i+1, em que i foi o último recebido
            4.2 - Verificar local do EOP (confirma se todos bytes vieram)
            4.3 - Se #$ tudo OK --> Pedir pacote i+2
                  Se #& erro --> Pedir reenvio
        5- Server recebe #@ ÚLTIMO PACOTE: 
            5.1 - Reagrupar todos pacotes e salvar em um único arquivo
            5.2 - Retorna mensagem de COMUNICAÇÃO COM SUCESSO!
"""

from enlaceRx import RX
from enlaceTx import TX
from interfaceFisica import Fisica, int_to_bytes, bytes_to_int
import time

serialName = "COM3"

class Server:
    def __init__(self, serialName):
        # unidades para guardar comunicação:
        self.packages = []
        self.last_package = 0
        self.total_packages = None
        self.busy = False
       
        # cria porta RX e TX do servidor
        self.rx = RX(Fisica(serialName))
        self.tx = TX(Fisica(serialName))

        # dicionário de propriedades da transmissão:
        self.props = {
            'tipo_mensagem':    0,
            'id_sensor':        0,
            'id_servidor':      0,
            'total_pacotes':    0,
            'pacote_atual':     0,
            'conteudo':         0,
            'recomecar':        0,
            'ultimo_recebido':  0,
            'CRC_1':            0,
            'CRC_2':            0
        }

    def check_is_busy(self):
        if self.busy:
            print(" Server is currently busy. Please, try again later.")
        else:
            print(" Server is available")

        return self.busy

    def start_server(self):
        # Abre as portas e limpa as memórias
        self.rx.fisica.open()
        self.rx.fisica.flush()
        self.rx.threadStart()

        self.tx.fisica.open()
        self.tx.fisica.flush()
        self.tx.threadStart()

        self.await_message()
    
    def await_message(self):
        """ 
        Coloca o server em status disponível, aguardando recebimento da mensagem
        """
        self.busy = False
        while(self.rx.getBufferLen() <= self.rx.fisica.HeaderLen + self.rx.fisica.EOPLen):
            if self.last_package == 0:
                print(" [ECHO] awaiting for client to connect...")
            else:
                print(" waiting for the next package...")
            time.sleep(0.05)
        
        #-- checa tipo da mensagem:
            # se de INÍCIO: --> inicia looping de transmissão
            # se de TRANSMISSÃO --> faz checkagens no HEAD e vê se está tudo ok
            #                   se tudo OK: --> Faz recebimento da mensagem.
        self.check_package_type()

    def check_package_type(self):
        """
        #! HEADER: 
        #! h0 \ h1 \ h2 \ h3 \ h4 \ h5 \ h6 \ h7 \ h8 \ h9
        
            #*h0 - tipo de mensagem:
                1: << ECHO client quer estabelecer comunicação
                2: >> (SERVER) resposta de que o servidor está ocioso e pronto p/ trabalhar
                3: << DADOS: contém um bloco de dados para ser transmitido
                4: >> (SERVER) mensagem 3 averiguada e resposta (OK ou NÃO OK)
            #*h3 - número total de pacotes do arquivo

            #*h4 - número do pacote sendo enviado

            #*h5 - se HANDSHAKE: id do arquivo | se DADOS: tamanho do payload (0 a 114)

            h6 - pacote para recomeço, se houver erro
            #*h7 - último pacote recebido com sucesso
            h8 - CRC
            h9 - CRC
        Checar tipo de mensagem: ECHO / DATA / INFO

        #*--tipo da mensagem:
            # se de INÍCIO: --> inicia looping de transmissão de pacotes
            # se de DADOS --> faz checkagens no HEAD e vê se está tudo ok
            #                   se tudo OK: --> Faz recebimento da mensagem.
        """
        
        # reseta o props[tipo_mensagem] p/ evitar interferência da msg anterior
        self.props['tipo_mensagem'] = 0 

        header = self.rx.getAllBuffer()[:10]
        self.props['tipo_mensagem'] = bytes_to_int(header[0])

        if self.props['tipo_mensagem'] == 1:
            print(" Client detected")
            
            # Envia resposta que está pronto, se não estiver ocupado
            self.props['tipo_mensagem'] = 2 if self.busy==False else 0
            self.tx.send_datagram(self.props)

            # PREPARA PARA RECEBER CONTEÚDO:
            self.receive_messages()

            return "ECHO"

        # mensagem de transferência
        elif self.props['tipo_mensagem'] == 3:
            # Chamar função que checa Head, tamanho do payload e devolve a ação necessária
            self.check_package_structure()
            
            print (f" Data received -- Package: #{bytes_to_int(header[4])} | Payload size: {bytes_to_int(header[5])} ")

            return "DATA"

        else:
            return ""  

    def check_package_structure(self):
        """
        Checa a estrutura do Payload, contrastando com as info's do Head.
        Se estiver tudo ok, recebe a mensagem, pede a próxima e aguarda recebimento da próxima.
        """

        return 
    def receive_messages(self):
        self.busy = True
        #! LOOPING P/ RECEBER TODOS OS PACOTES DA TRANSMISSÃO
        # Checa o tipo e direciona para ação
        # envia mensagem de status
        return

    def package_feedback(self, cond1, cond2):
        return

    def clear_props(self, fields=[]):
        # Limpa apenas os campos especificados
        if fields:
            for prop in self.props:
                if prop in fields:
                    self.props[prop] = 0
        else:
            for prop in self.props:
                self.props[prop] = 0
        
    
    def stop_server(self):
        """ Encerra o server """
        self.rx.threadKill()
        self.rx.fisica.close()

if __name__ == "__main__":
    server = Server(serialName)
    server.start_server()
    server.stop_server()
    print("Comunicação encerrada!")