#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#####################################################
# Camada Física da Computação
#Carareto
#17/02/2018
#  Camada de Enlace
####################################################

# Importa pacote de tempo
import time

# Threads
import threading
from typing import Dict
from interfaceFisica import int_to_bytes

# Class
class TX(object):
 
    def __init__(self, fisica):
        self.fisica      = fisica
        self.buffer      = bytes(bytearray())
        self.transLen    = 0
        self.empty       = True
        self.threadMutex = False
        self.threadStop  = False


    def thread(self):
        while not self.threadStop:
            if(self.threadMutex):
                self.transLen    = self.fisica.write(self.buffer)
                self.threadMutex = False

    def threadStart(self):
        self.thread = threading.Thread(target=self.thread, args=())
        self.thread.start()

    def threadKill(self):
        self.threadStop = True

    def threadPause(self):
        self.threadMutex = False

    def threadResume(self):
        self.threadMutex = True

    def sendBuffer(self, data):
        self.transLen   = 0
        self.buffer = data
        self.threadMutex  = True

    def getBufferLen(self):
        return(len(self.buffer))

    def getStatus(self):
        return(self.transLen)
        
    def getIsBussy(self):
        return(self.threadMutex)

    def build_header(self, props:dict):
        h0 = int_to_bytes(props['tipo_mensagem'])       # tipo de Mensagem
        h1 = int_to_bytes(props['id_sensor'])           # id do Sensor
        h2 = int_to_bytes(props['id_servidor'])         # id do Servidor
        h3 = int_to_bytes(props['total_pacotes'])       # Número Total de Pacotes
        h4 = int_to_bytes(props['pacote_atual'])        # Número do Pacote Atual
        h5 = int_to_bytes(props['tamanho_conteudo'])    # id do arquivo / tamanho do payload
        h6 = int_to_bytes(props['recomecar'])           # Pacote p/ recomeçar, caso tenha Erro
        h7 = int_to_bytes(props['ultimo_recebido'])     # último pacote recebido com sucesso
        h8 = int_to_bytes(props['CRC_1'])               # CRC
        h9 = int_to_bytes(props['CRC_2'])               # CRC
        #* valores padrão - 0

        header = h0 + h1 + h2 + h3 + h4 + h5 + h6 + h7 + h8 + h9
        return header

    def build_EOP(self):
        EOP = b'\xff\xaa\xff\xaa'
        return EOP

    def send_datagram(self, props:dict, payload=b''):
        datagram = self.build_header(props) + payload + self.build_EOP()
        
        self.sendBuffer(datagram)