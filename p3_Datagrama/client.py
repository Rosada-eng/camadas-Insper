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

serialName = "COM4"


#TODO: - Iniciar comunicação com Server
#TODO: - Gerenciamento da comunicação  

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
        self.last_package           = 0
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

        # Constrói mensagem do tipo 1 (Handshake)
        handshake = self.tx.build_header(temporary_props) + self.tx.build_EOP()
        
        #* Inicia comunicação e aguarda resposta por 5 segundos
        self.tx.sendBuffer(handshake)
        response = self.check_for_handshake()

        for i in range (0, effort): 
            print(" awaiting for server to connect...", i)
            response = self.check_for_handshake()

            if response == True:
                # Inicia a transmissão dos pacotes
                return self.manage_transmition()

            else:
                time.sleep(5 / effort)

        return self.try_handshake_again()

    def check_for_handshake(self):
        """ 
            Analisa se o Buffer contém a mensagem de 
            resposta ao Handshake (tipo_mensagem == 2). 
            Retorna `True`, se houver. `False`, caso contrário.
        """

        if self.rx.getBufferLen() >= self.rx.fisica.HeaderLen + self.rx.fisica.EOPLen:
            buffer = self.rx.getBuffer()
            head = buffer[:self.rx.fisica.HeaderLen]

            if bytes_to_int(head[0]) == 2:
                print(" Server is available. Starting to transmit...")
                return True

            else:
                return False 
        else:
            return False

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
        # while self.last_package < self.total_packages_to_send:
            # fica calibrando envio / mensagens de feedback
        return 

    def await_for_next_package(self):
        return 

    # AUX:
    def read_file_as_bytes(self, filename):
        print(f"Lendo arquivo de: {filename}")
        with open(filename,  "rb") as f:
            file = f.read()
        return file
        
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
    client = Client(serialName)
    client.start_client()
    client.stop_client()
    print("Comunicação encerrada!")
