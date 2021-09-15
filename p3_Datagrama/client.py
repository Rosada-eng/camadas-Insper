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
from interfaceFisica import Fisica

serialName = "COM4"

class Client:
    def __init__(self, serialName, file_route, server_id, client_id=0,):
        self.id         = client_id
        self.server_id  = server_id
        # unidades para guardar comunicação:
        self.packages_to_send = []              # armazena a informação dividida em pacotes
        self.payload_size = 114
        self.last_package = 0
        self.total_packages_to_send = None

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

    def start_client(self):
        # Abre as portas e limpa as memórias
        self.rx.fisica.open()
        self.rx.fisica.flush()
        self.rx.threadStart()

        self.tx.fisica.open()
        self.tx.fisica.flush()
        self.tx.threadStart()

        self.open_communication()

    def read_file_as_bytes(self, filename):
        print(f"Lendo arquivo de: {filename}")
        with open(filename,  "rb") as f:
            file = f.read()
        return file

    def create_packages_to_transmit(self):
        """ 
            Cria todos os pacotes a serem enviados para o servidor, 
            contendo o tamanho correto para cada payload e seguindo 
            o protocolo adotado.
            Armazena a lista no atributo `packages_to_send`
        """
        try: 
            self.file = self.read_file_as_bytes(self.route)
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
            print(" Erro na conversão do arquivo. Confira o caminho e o tamanho do arquivo")
            return False
         

    def open_communication(self):
        """ Tenta estabelecer comunicação com o servidor. """
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
        
    
    def stop_client(self):
        """ Encerra o client """
        self.rx.threadKill()
        self.rx.fisica.close()

if __name__ == "__main__":
    client = Client(serialName)
    client.start_client()
    client.stop_client()
    print("Comunicação encerrada!")
