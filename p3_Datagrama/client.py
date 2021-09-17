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

from binascii import Error
import numpy as np
import time
import random
from enlaceTx import TX
from enlaceRx import RX
from interfaceFisica import Fisica, bytes_to_int, int_to_bytes
import time
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
        self.fisica = Fisica(serialName)
        self.rx = RX(self.fisica)
        self.tx = TX(self.fisica)

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
        self.fisica.open()
        self.fisica.flush()

        self.rx.fisica.flush()
        self.rx.threadStart()

        self.tx.fisica.flush()
        self.tx.threadStart()

        self.open_communication()

    def open_communication(self, effort=10):
        """ Tenta estabelecer comunicação com o servidor. """
        self.send_handshake()
        self.wait_for_handshake_answer()

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
            print(f" \n >> HANDSHAKE ({len(handshake)}) -- {handshake}")

        except:
            print(" Client was not able to send handshake")

    def wait_for_handshake_answer(self, effort = 10):
        for i in range(0, effort):
            print("."*(i+1))
            if self.rx.getBufferLen() >= self.rx.fisica.HeaderLen + self.rx.fisica.EOPLen:
                result = self.check_package_type()

                if result == "2":
                    return self.manage_transmition()

            time.sleep(5 / effort)

        return self.try_handshake_again()

    def try_handshake_again(self):
        r = input("Servidor inativo. Tentar novamente? S/N  ")

        if r.upper() == "S":
            self.open_communication()
        else:
            return

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
            packages=[]
            for i in range(0, self.total_packages_to_send):
                content = (self.file[i*self.payload_size: (i+1)*self.payload_size])
                # Constrói o package de cada parcela da mensagem
                temporary_props = {
                    'tipo_mensagem':    3,                              # mensagem do tipo DADOS
                    'id_sensor':        self.id,     
                    'id_servidor':      self.server_id,
                    'total_pacotes':    self.total_packages_to_send,
                    'pacote_atual':     i,                              # de 0 a total -1
                    'tamanho_conteudo': len(content),                   # tamanho do payload
                    'recomecar':        0 if i == 0 else i-1,
                    'ultimo_recebido':  0 if i == 0 else i-1,
                    'CRC_1':            0,
                    'CRC_2':            0
                }

                package = self.tx.build_header(temporary_props) + content + self.tx.build_EOP()
                packages.append(package)

            return packages
        except:
            #TODO: trocar print's para o Inglês
            print(" Erro na conversão do arquivo. Confira o caminho e o tamanho do arquivo")
         
    def manage_transmition(self):
        # Envia o pacote 0
        print(f" ENVIA PACOTE #{self.current_package}")
        self.tx.sendBuffer(self.packages_to_send[self.current_package])

        #! LOOPING P/ ENVIAR TODOS OS PACOTES DA TRANSMISSÃO
        while self.current_package < self.total_packages_to_send:
            self.await_for_answer()

        print(" TODOS PACOTES ENVIADOS COM SUCESSO!")
        #TODO: CHECAR MENSAGEM DE SUCESSO DE ENVIO DO PACOTE
        return 

        
    def await_for_answer(self):
        while(self.rx.getBufferLen() < self.rx.fisica.HeaderLen + self.rx.fisica.EOPLen):
            print(f" Waiting for the answer #{self.current_package} ...")
            time.sleep(0.1)

        return self.check_package_type()

    def check_package_type(self):
        buffer = self.rx.getAllBuffer()
        header = self.convert_header_to_list(buffer[:self.rx.fisica.HeaderLen])

        if header:
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
    
    def send_package(self, message_type):
        # Esvazia o buffer antigo antes de receber o próximo
        self.rx.buffer = b""
        self.tx.buffer = b""

        # Envia o próximo pacote, se receber mensagem de sucesso
        if message_type == 4:
            self.current_package += 1      #! controla o Looping principal
        
        if self.current_package != self.total_packages_to_send:
            # Repete a última, caso contrário
            print(f"--> Enviar o pacote {self.current_package}")
            self.tx.sendBuffer(self.packages_to_send[self.current_package])
        
    # AUX:
    def read_file_as_bytes(self, filename):
        print(f"Lendo arquivo de: {filename}")
        try: 
            with open(filename,  "rb") as f:
                file = f.read()
                print(" Arquivo lido com sucesso!")
            return file

        except:
            print(" Falha ao ler o arquivo")
            raise Error

    def convert_header_to_list(self, header):
        if header:
            return [byte for byte in header]

        else:
            return Error
    
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
