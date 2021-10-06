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

    TESTES:
        Tanto Server quanto Client têm alguns atributos para se realizar
        os testes pedidos pelos professores. Abaixo, altere para `True` os 
        testes que se deseja realizar.

"""

from binascii import Error
import time
from enlaceTx import TX
from enlaceRx import RX
from interfaceFisica import Fisica
import time
from personalized_exceptions import *
import datetime

serialName = "COM3"


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

        
        self.handshake_attempt = 1
        self.connected = False
        
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

        # string para registrar os logs
        self.logs = ""

        #<> Configuração de Testes
        self.teste_erro_ordem_incorreta = False

    def start_client(self):
        # Abre as portas e limpa as memórias
        self.fisica.open()
        self.fisica.flush()

        self.rx.fisica.flush()
        self.rx.threadStart()

        self.tx.fisica.flush()
        self.tx.threadStart()

        self.open_communication()

    def open_communication(self):
        """ Tenta estabelecer comunicação com o servidor. """
        if self.handshake_attempt == 4:
            self.send_timeout_message()
        else:
            self.send_handshake()
            self.wait_for_handshake_answer() # aguarda a resposta por 5 segundos

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

            #@ log -> S
            self.add_log('sent', self.props['tipo_mensagem'], len(handshake))

            print(f" \n >> HANDSHAKE ({len(handshake)}) -- {handshake}")

        except:
            print(" Client was not able to send handshake")
            raise SendHandshakeError()
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
        self.handshake_attempt += 1
        self.open_communication()

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
            raise ConvertPackagesError()
         
    def manage_transmition(self):
        # Envia o pacote 0
        # try:
        print(f" ENVIA PACOTE #{self.current_package}")
        self.tx.sendBuffer(self.packages_to_send[self.current_package])

        #@ log -> S
        self.add_log('sent', 3, len(self.packages_to_send[self.current_package]))

        #! LOOPING P/ ENVIAR TODOS OS PACOTES DA TRANSMISSÃO
        while self.current_package <= self.total_packages_to_send:
            self.await_for_answer()

        self.connected = False
        if self.current_package == self.total_packages_to_send:
            print("TODOS PACOTES ENVIADOS COM SUCESSO!")
        return 

        
    def await_for_answer(self):
        attempt = 0
        while(self.rx.getBufferLen() < self.rx.fisica.HeaderLen + self.rx.fisica.EOPLen) and attempt < 20:
            print(f" Waiting for the answer #{self.current_package} ... ({attempt})")
            
            if attempt % 5 == 0 and attempt > 0:
                print(f"--> Reenviar o pacote {self.current_package}")
                self.tx.sendBuffer(self.packages_to_send[self.current_package])

                #@ log -> S
                self.add_log('sent', 3, len(self.packages_to_send[self.current_package]))
            
            time.sleep(1)
            attempt += 1

        if attempt == 20:
            self.send_timeout_message()
        else: 
            attempt = 0
            return self.check_package_type()

    def check_package_type(self):
        buffer = self.rx.getAllBuffer()
        header = self.convert_header_to_list(buffer[:self.rx.fisica.HeaderLen])

        if header:
            #@ log <- R
            self.add_log('received', header[0], len(buffer))

            # checa se mensagem é destinada ao Client correto
            # checa se mensagem veio do Servidor que está sendo feita a comunicação
            if header[1] == self.id and header[2] == self.server_id:
                #* mensagem do tipo HANDSHAKE 
                if header[0] == 2:
                    print("\033[1;32;47m"
                            + "Server is available. Starting to transmit..."
                            + "\033[0;0m")
                    self.connected = True
                    return "2"

                #* mensagem do tipo SUCCESS (DADOS)
                elif header[0] == 4:
                    print ("\033[1;32m"
                            + "Package received. Sending next one..."
                            + "\033[0;0m")
                    self.send_package(header)
                    return "4"

                #* mensagem do tipo TIMEOUT 
                elif header[0] == 5:
                    print("\033[4;31m" 
                        + "Servidor encerrou a comunicação devido ao tempo excessivo de espera."
                        + "\033[0;0m")
                    raise ServerDropError()

                #* mensagem do tipo ERROR (DADOS)
                elif header[0] == 6:
                    print("\033[1;33m" 
                            + "Failed to deliver last package. Trying again..."
                            + "\033[0;0m")
                    
                    self.send_package(header)
                    return "6"
                #* mensagem do tipo COMPLETED
                elif header[0] == 8:
                    print("\033[1;32;47m"
                            + " File transfered with success!!"
                            + "\033[0;0m")
                    self.current_package += 1
                    #! QUEBRA O LOOPING PRINCIPAL DA TRANSFERÊNCIA
                    return "8"

            else:
                print(" This package was not addressed to this communication. Try again.")
    
    def send_package(self, header):
        # Esvazia o buffer antigo antes de receber o próximo
        self.rx.buffer = b""
        self.tx.buffer = b""

        #<> CÓDIGO PARA SIMULAR ERRO NA ORDEM DA TRANSMISSÃO
        if self.current_package == 15 and self.teste_erro_ordem_incorreta:
            self.current_package = 17
            self.forcar_erro = False

        # Envia o próximo pacote, se receber mensagem de sucesso
        if header[0] == 4:
            self.current_package += 1      #! controla o Looping principal
        
        elif header[0] == 6:
            self.current_package = header[6]    # reenvia o pacote em 'recomecar'
        
        if self.current_package != self.total_packages_to_send:
            print(f"--> Enviar o pacote {self.current_package}")
            self.tx.sendBuffer(self.packages_to_send[self.current_package])

            #@ log -> S
            self.add_log('sent', 3, len(self.packages_to_send[self.current_package]))
            
    def send_timeout_message(self):
        print("\033[4;31m"
                + "No answers received from client. Closing communication..."
                + "\033[0;0m")
        
        temporary_props = {
                    'tipo_mensagem':    5,                              # erro de 'TimeOut'
                    'id_sensor':        self.id,     
                    'id_servidor':      self.server_id,
                    'total_pacotes':    0,
                    'pacote_atual':     0,
                    'tamanho_conteudo': 0,                   
                    'recomecar':        0,
                    'ultimo_recebido':  0,
                    'CRC_1':            0,
                    'CRC_2':            0
                }
        if self.connected:
            message = self.tx.build_header(temporary_props) + self.tx.build_EOP()
            time.sleep(2)  
            self.tx.sendBuffer(message)  

            #@ log -> S
            self.add_log('sent', 5, len(message))
            
        raise TimeOutError()

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
            raise ReadFileError()

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

    def add_log(self, received_or_sent, message_type, total_bytes_size):
        if received_or_sent == 'received':
            self.logs +=f"{datetime.datetime.now()} | received | {message_type} | {total_bytes_size}\n"
        elif received_or_sent == 'sent':
            self.logs +=f"{datetime.datetime.now()} | sent     | {message_type} | {total_bytes_size} | {self.current_package} | {self.total_packages_to_send}\n" 
    
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
    try:
        client.start_client()
        client.stop_client()

    except Exception as e:
        print("Ocorreu alguma exceção ＞﹏＜\n-->", e.message)
        client.stop_client()

    finally:
        print(client.logs)
        with open('p4_Protocolo-UART/Client-test.txt', 'w') as output:
            output.write(client.logs)

    print("Comunicação encerrada!")
