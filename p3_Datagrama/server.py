#
""" 
    Funcionamento: 
        1- O Server será inicializado e ficará ouvindo até detectar um pedido de transmissão
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
from interfaceFisica import Fisica, bytes_to_int
import time

serialName = "COM4"

class Server:
    def __init__(self, serialName, server_id):
        self.id                         = server_id
        self.client_id                  = None
        self.file_id                    = None

        self.payloads_received          = []              # armazena os pacotes recebidos até o momento
        self.current_package            = 0
        self.total_packages_to_receive  = 0
        self.busy                       = False
       
        # cria porta RX e TX do servidor
        self.fisica = Fisica(serialName)
        self.rx = RX(self.fisica)
        self.tx = TX(self.fisica)

        # dicionário de propriedades (p/ ENVIAR) da transmissão:
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

    def start_server(self):
        # Abre as portas e limpa as memórias
        self.fisica.open()
        self.fisica.flush()

        self.rx.fisica.flush()
        self.rx.threadStart()

        self.tx.fisica.flush()
        self.tx.threadStart()

        self.busy = False
        self.await_message()
    
    def await_message(self):
        """ 
        Coloca o server em espera, aguardando recebimento da mensagem
        """
        while(self.rx.getBufferLen() < self.rx.fisica.HeaderLen + self.rx.fisica.EOPLen):
            if self.current_package == 0 and not self.busy:
                print(f"[ECHO] awaiting for client to connect ({self.rx.getBufferLen()})...")
            else:
                print(f" waiting for the package #{self.current_package}...")
            time.sleep(0.1)
        
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

            # se de INÍCIO: --> inicia looping de transmissão de pacotes
            # se de DADOS --> faz checkagens no HEAD e vê se está tudo ok
            #                   se tudo OK: --> Faz recebimento da mensagem.
        """

        buffer = self.rx.getAllBuffer()
        header = self.convert_header_to_list(buffer[:self.rx.fisica.HeaderLen])
        if buffer:
            # checa se mensagem é destinada ao Servidor correto
            if header[2] == self.id: 
                #* mensagem do tipo 1 (ECHO)
                if header[0] == 1:
                    print("\033[1;32;47m"
                            +"Client detected -- Valid communication. "
                            +"\033[0;0m")
                    self.clear_props()

                    #* Guarda informações pertinentes à comunicação
                    self.client_id                  = header[1]
                    self.file_id                    = header[5]
                    self.total_packages_to_receive  = header[3]
                    
                    # Envia resposta se está disponível ou não
                    self.props['tipo_mensagem']  = 2 if self.busy==False else 0
                    self.props['id_sensor']      = self.client_id
                    self.props['id_servidor']    = self.id
                    self.props['total_pacotes']  = self.total_packages_to_receive

                    message = self.tx.build_header(self.props) + self.tx.build_EOP()
                    self.tx.sendBuffer(message)

                    # Inicia Looping para receber todo conteúdo, se estiver disponível:
                    if self.props['tipo_mensagem'] == 2:
                        self.manage_receiving()       

                
                #* mensagem do tipo 3 (DADOS)
                elif header[0] == 3:
                    # checa se veio do sensor correto:
                    if header[1] == self.client_id:
                        # checa último pacote recebido h(7) e pacote atual h(4)
                        print(f" ultimo recebido: {header[7]} -- atual: {header[4]}")
                        if (header[7] == self.current_package -1 or header[7] == 0) and (header[4] == self.current_package or header[4] == 0):
                            if len(buffer) < self.rx.fisica.HeaderLen + self.rx.fisica.EOPLen + header[5]:
                                time.sleep(0.2)
                            
                            payload = self.extract_payload(buffer, header[5])

                            if payload:
                                self.payloads_received.append(payload)
                                self.ask_for_next_package()
                            else:
                                self.ask_to_repeat()
                        
                        else:
                            print("\033[4;31;40m" 
                                + f"This package was not expected. Please, send package #{self.current_package}"
                                + "\033[0;0m")
                            self.ask_to_repeat()


                    else:
                        print(" This package came from another client. Please, start communication again")
                        raise Exception
                
            else:
                print(" Wrong server. Please, try again later")
                raise Exception

    def extract_payload(self, buffer, size):
        payload = buffer[self.tx.fisica.HeaderLen : self.tx.fisica.HeaderLen + size]

        check_EOP = self.check_EOP(buffer[-self.tx.fisica.EOPLen : ])
        if check_EOP:
            return payload
        else:
            return False

    def check_EOP(self, EOP):
        if EOP == self.tx.fisica.EOP:
            return True
        else:
            print("\033[1;31m"
                +"Payload size is not correct. Please, send package again."
                +"\033[0;0m")
            return False
               
    def manage_receiving(self):
        """
            1- Checa a estrutura de cada pacote. Se condizer com as condições, recebe os dados e agrupa 
            2- Solicitar o envio de um novo pacote ao client e aguardar recebimento
        """

        self.busy = True
        try: 
            #! LOOPING P/ RECEBER TODOS OS PACOTES DA TRANSMISSÃO
            while self.current_package < self.total_packages_to_receive:
                self.await_message()
            
            #* Salvar arquivo .PNG recebido
            #<> HARDCODED: Arquivo de saída será um png!
            full_file = b""
            for payload in self.payloads_received:
                full_file += payload
            print(f" ARQUIVO RECEBIDO: \n{full_file}")
            result = self.save_to_file("p3_Datagrama/output.png", full_file)
            
            if result:
                print("\033[1;32;47m" 
                        + "Salvo com sucesso!"
                        + "\033[0;0m")
                # send success transfer
                self.tx.buffer = b""
                self.rx.buffer = b""
                self.props['tipo_mensagem'] = 8     # mensagem de 'Transferência Completa'
                message = self.tx.build_header(self.props) + self.tx.build_EOP()
                self.tx.sendBuffer(message)
                time.sleep(0.5)

            else:
                # send error. Start from the begining
                self.tx.buffer = b""
                self.rx.buffer = b""
                self.props['tipo_mensagem'] = 6     # mensagem de 'Erro na Transferência --> Recomeçar'
                self.props['recomecar'] = 0
                message = self.tx.build_header(self.props) + self.tx.build_EOP()
                self.tx.sendBuffer(message)

        
        except:
            print("Ocorreu algum erro")
            return

    def ask_for_next_package(self):
        """ 
            Envia a mensagem para RECEBER o próximo pacote.
            Atualiza o último recebido e por qual pacote recomecar em caso de erro.
        """
        print("\033[1;32m" 
                + f"Package #{self.current_package} of #{self.total_packages_to_receive -1} received successfully "
                + "\033[0;0m")
        # Esvazia o buffer antigo antes de receber o próximo
        self.rx.buffer = b""
        self.tx.buffer = b""

        self.current_package += 1              # Controla o looping principal
        
        # Props para comunicação
        self.props['ultimo_recebido'] += 1
        self.props['recomecar'] += 1
        self.props['pacote_atual'] += 1
        self.props['tipo_mensagem'] = 4     # Mensagem de 'pacote recebido com sucesso'

        message = self.tx.build_header(self.props) + self.tx.build_EOP()
        # print(self.props)
        self.tx.sendBuffer(message)
        #! FECHA CICLO DO LOOPING PRINCIPAL

    def ask_to_repeat(self):
        """ 
            Envia a mensagem para REPETIR o último pacote.
        """
        # Esvazia o buffer antigo antes de receber o próximo
        self.rx.buffer = b""
        self.tx.buffer = b""

        self.props['tipo_mensagem'] = 6     # Mensagem de 'erro no último pacote recebido'
        self.props['recomecar'] = self.current_package
       
        message = self.tx.build_header(self.props) + self.tx.build_EOP()
        # print(self.props)
        self.tx.sendBuffer(message)

        print("\033[1;33m"
                + f"Failed to receive package #{self.current_package}. Please, send again. "
                + "\033[0;0m")
        return
        #! FECHA CICLO DO LOOPING PRINCIPAL
    #AUX:
    def clear_props(self, fields=[]):
        # Limpa apenas os campos especificados
        if fields:
            for prop in self.props:
                if prop in fields:
                    self.props[prop] = 0
        else:
            for prop in self.props:
                self.props[prop] = 0
        
    def convert_header_to_list(self, header):
        return [byte for byte in header]
    
    def save_to_file(self, filename, bytes):
        try: 
            with open(filename, "wb") as output:
                output.write(bytes)
                time.sleep(1)

            return True

        except:
            return False

    def stop_server(self):
        """ Encerra o server """
        self.rx.threadKill()
        self.tx.threadKill()
        self.rx.fisica.close()
        self.tx.fisica.close()

if __name__ == "__main__":
    server = Server(serialName, server_id=1)
    server.start_server()
    server.stop_server()
    print("Comunicação encerrada!")