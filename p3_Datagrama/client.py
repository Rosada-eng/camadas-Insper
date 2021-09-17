#
""" 
    Funcionamento: 
        1- O Cliente iniciará o canal de comunicação, procurando pelo server disponível
            1.1 - Envia uma mensagem p/ o Servidor perguntando pelo status
            1.2 - Se não receber dentro de 5seg, perguntar se #% Tentar Novamente?
        2- Ao receber a resposta de OK do Servidor, incia a transmissão em pacotes
        3- Transmissão em pacotes (Datagrama): #@ Datagrama < 128 bytes
                - HEADER:
                - PAYLOAD:
                - EOP (End of Payload): 
            3.1 - Envia pacote i -> #% Aguarda confirmação de Sucesso do Server
            3.2 - Se Sucesso: Envia próximo pacote
                  Se falha: Reenviar o último pacote

"""

import numpy as np
import time
import random
from enlaceTx import TX
from enlaceRx import RX
from interfaceFisica import Fisica, bytes_to_int, int_to_bytes

serialName = "COM3"


#>> DONE: - Iniciar comunicação com Server
#>> - Gerenciamento da comunicação 
#>> -- Enviar PRÓXIMO pacote ou REENVIAR 
#TODO: Mensagem final de sucesso

class Client:
    def __init__(self, serialName, file_route, server_id, client_id=0,):
        self.id         = client_id
        self.server_id  = server_id

        # parâmetros para guardar rota e o arquivo transformado em bytes
        self.route = file_route
        self.file  = b''
       
        # cria porta RX e TX do client
        self.rx = RX(Fisica(serialName))
        self.tx = TX(Fisica(serialName))

        # dicionário de propriedades da transmissão:
        self.props = {
            'tipo_mensagem':    0,
            'id_sensor':        0,
            'id_servidor':      0,
            'total_pacotes':    0,
            'pacote_atual':     0,
            'tamanho_conteudo': 0,
            'recomecar':        0,
            'ultimo_recebido':  0,
            'CRC_1':            0,
            'CRC_2':            0
        }

        # unidades para guardar comunicação:
        self.payload_size           = 114 
        self.current_package        = 0
        self.total_packages_to_send = 0
        self.packages_to_send       = self.create_packages_to_transmit(self.route) 

    def start_client(self):
        # Abre as portas e limpa as memórias
        self.rx.fisica.open()
        self.rx.fisica.flush()
        self.rx.threadStart()

        self.tx.fisica.open()
        self.tx.fisica.flush()
        self.tx.threadStart()

        self.open_communication()

    def open_communication(self, effort=10):
        """ Tenta estabelecer comunicação com o servidor. """
        self.send_handshake()

        # Checa resposta do handshake por 5 segundos
        for i in range (0, effort): 
            print(" awaiting for server to connect...", i)
            response = self.check_package_type()

            if response == "2":
                # Inicia a transmissão dos pacotes
                return self.manage_transmition()

            else:
                time.sleep(5 / effort)

        return self.try_handshake_again()

    def send_handshake(self):
        try:
            temporary_props = {
                'tipo_mensagem':    1,                              #0 - mensagem do tipo HANDSHAKE
                'id_sensor':        self.id,                        #1 
                'id_servidor':      self.server_id,                 #2
                'total_pacotes':    self.total_packages_to_send,    #3
                'pacote_atual':     0,                              #4
                'tamanho_conteudo': 22,                             #5 #! id do arquivo
                'recomecar':        0,                              #6
                'ultimo_recebido':  0,                              #7
                'CRC_1':            0,                              #8
                'CRC_2':            0                               #9
            }

            handshake = self.tx.build_header(temporary_props) + self.tx.build_EOP()        
            self.tx.sendBuffer(handshake)
            print(" Looking for server to connect to")

        except:
            print(" Client was not able to send handshake")

    def try_handshake_again(self):
        r = input("Servidor inativo. Tentar novamente? S/N")

        if r.upper() == "S":
            self.open_communication()
        else:
            pass

    def create_packages_to_transmit(self, filename):
        """ 
            Cria todos os pacotes a serem enviados para o servidor, 
            contendo o tamanho correto para cada payload e seguindo 
            o protocolo adotado.
            Armazena a lista no atributo `packages_to_send`
        """
        try: 
            self.file = self.read_file_as_bytes(filename)
            # Calcula número de pacotes necessários para enviar toda a mensagem
            import math
            self.total_packages_to_send = math.ceil(len(self.file) / self.payload_size)
            # Divide a mensagem no número de pacotes necessários
            for i in range(0, self.total_packages_to_send):
                content = (self.file[i*self.payload_size: (i+1)*self.payload_size])

                # Constrói o package de cada parcela da mensagem
                temporary_props = {
                    'tipo_mensagem':    3,                              # mensagem do tipo DADOS
                    'id_sensor':        self.id,     
                    'id_servidor':      self.server_id,
                    'total_pacotes':    self.total_packages_to_send,
                    'pacote_atual':     i,
                    'tamanho_conteudo': len(content),                   # tamanho do payload
                    'recomecar':        0 if i == 0 else i-1,
                    'ultimo_recebido':  0 if i == 0 else i-1,
                    'CRC_1':            0,
                    'CRC_2':            0
                }

                package = self.tx.build_header(temporary_props) + content + self.tx.build_EOP()
                self.packages_to_send.append(package)

            return True

        except:
            #TODO: trocar print's para o Inglês
            print(" Erro na conversão do arquivo. Confira o caminho e o tamanho do arquivo")
            return False
         
    def manage_transmition(self):
        # Envia o pacote 0
        self.tx.sendBuffer(self.packages_to_send[self.current_package])

        #! LOOPING P/ ENVIAR TODOS OS PACOTES DA TRANSMISSÃO
        while self.current_package <= self.total_packages_to_send:
            self.await_for_answer()

        #TODO: CHECAR MENSAGEM DE SUCESSO DE ENVIO DO PACOTE
        return 

    def await_for_answer(self):
        while(self.rx.getBufferLen() <= self.rx.fisica.HeaderLen + self.rx.fisica.EOPLen):
                print(" waiting for the next package...")
                time.sleep(0.05)

        self.check_package_type()

    def check_package_type(self):
        buffer = self.rx.getAllBuffer()
        header = self.convert_header_to_list(buffer[:self.rx.fisica.HeaderLen])

        # checa se mensagem é destinada ao Client correto
        # checa se mensagem veio do Servidor que está sendo feita a comunicação
        if header[1] == self.id and header[2] == self.server_id:
            #* mensagem do tipo HANDSHAKE 
            if header[0] == 2:
                print(" Server is available. Starting to transmit...")
                return "2"

            #* mensagem do tipo SUCCESS (DADOS)
            elif header[0] == 4:
                print (" Package received. Sending next one...")
                self.send_package(message_type=header[0])
                return "4"

            #* mensagem do tipo ERROR (DADOS)
            elif header[0] == 6:
                print(" Failed to deliver last package. Trying again...")
                self.send_package(message_type=header[0])
                return "6"

        else:
            print(" This package was not addressed to this communication. Try again.")
            raise Exception
    
    def send_package(self, message_type):
        # Envia o próximo pacote, se receber mensagem de sucesso
        if message_type == "4":
            self.current_package += 1      #! controla o Looping principal
        
        # Repete a última, caso contrário
        self.tx.sendBuffer(self.packages_to_send[self.current_package])
       
    # AUX:
    def read_file_as_bytes(self, filename):
        print(f"Lendo arquivo de: {filename}")
        with open(filename,  "rb") as f:
            file = f.read()
        return file

    def convert_header_to_list(self, header):
        return [bytes_to_int(byte) for byte in header]
    
    def clear_props(self, fields=[]):
        # Limpa apenas os campos especificados
        if fields:
            for prop in self.props:
                if prop in fields:
                    self.props[prop] = 0
        else:
            for prop in self.props:
                self.props[prop] = 0
        
    def stop_client(self):
        """ Encerra o client """
        self.rx.threadKill()
        self.tx.threadKill()
        self.rx.fisica.close()
        self.tx.fisica.close()

if __name__ == "__main__":
    client = Client(serialName,
                    server_id=1,
                    client_id=2,
                    file_route="p3_Datagrama/apple.png")
    client.start_client()
    client.stop_client()
    print("Comunicação encerrada!")
