from os import error
from client import *
from enlaceTx import *
from interfaceFisica import *

# tx = TX(Fisica("bla"))
# payload_size = 114
# def read_file_as_bytes(filename):
#     with open(f"p3_Datagrama/{filename}", "rb") as f:
#         file = f.read()
#     return file

# def create_packages_to_transmit():
#     """ 
#         Cria todos os pacotes a serem enviados para o servidor, 
#         contendo o tamanho correto para cada payload e seguindo 
#         o protocolo adotado.
#         Armazena a lista no atributo `packages_to_send`
#     """
#     packages_to_send = []
#     try: 
#         file = read_file_as_bytes("apple.png")

#         # Calcula número de pacotes necessários para enviar toda a mensagem
#         import math
#         total_packages_to_send = math.ceil(len(file) / payload_size)

#         payloads = []
#         # Divide a mensagem no número de pacotes necessários
#         for i in range(0, total_packages_to_send):
#             content = (file[i*payload_size: (i+1)*payload_size])
#             payloads.append(content)

#             # Constrói o package de cada parcela da mensagem
#             temporary_props = {
#                 'tipo_mensagem':    3,                              # mensagem do tipo DADOS
#                 'id_sensor':        1,     
#                 'id_servidor':      1,
#                 'total_pacotes':    114,
#                 'pacote_atual':     i,
#                 'tamanho_conteudo': len(content),                   # tamanho do payload
#                 'recomecar':        0 if i == 0 else i-1,
#                 'ultimo_recebido':  0 if i == 0 else i-1,
#                 'CRC_1':            0,
#                 'CRC_2':            0
#             }

#             package = tx.build_header(temporary_props) + content + tx.build_EOP()
#             packages_to_send.append(package)
#         return packages_to_send

#     except:
#         print(" Erro na conversão do arquivo. Confira o caminho e o tamanho do arquivo")
#         return False

# pckg = create_packages_to_transmit()
# print(pckg)

client = Client("COM4", "p3_Datagrama/apple.png", 2, 3)

x = client.create_packages_to_transmit()

print(x)
print(client.packages_to_send)