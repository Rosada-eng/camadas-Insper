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

#! START/END ORDER
from interfaceFisica import START_ORDER, END_ORDER

# Class
class RX(object):
  
    def __init__(self, fisica):
        self.fisica      = fisica
        self.buffer      = bytes(bytearray())
        self.threadStop  = False
        self.threadMutex = True
        self.READLEN     = 1024
        self.HeaderLen   = 6 + 2 + 1 + 13

    def thread(self): 
        while not self.threadStop:
            if(self.threadMutex == True):
                rxTemp, nRx = self.fisica.read(self.READLEN)
                if (nRx > 0):
                    self.buffer += rxTemp  
                time.sleep(0.01)

    def threadStart(self):       
        self.thread = threading.Thread(target=self.thread, args=())
        self.thread.start()

    def threadKill(self):
        self.threadStop = True

    def threadPause(self):
        self.threadMutex = False

    def threadResume(self):
        self.threadMutex = True

    def getIsEmpty(self):
        if(self.getBufferLen() == 0):
            return(True)
        else:
            return(False)

    def getBufferLen(self):
        return(len(self.buffer))

    def getAllBuffer(self, len):
        self.threadPause()
        b = self.buffer[:]
        self.clearBuffer()
        self.threadResume()
        return(b)

    def getBuffer(self, nData):
        #<< EDIT: altera as posições do slice p/ b receber apenas o conteúdo da mensagem

        self.threadPause()
        b           = self.buffer[self.HeaderLen : self.HeaderLen + nData ]
        if self.buffer[self.HeaderLen + nData : self.HeaderLen + nData + 6] == END_ORDER: #@ C2 -- end order
            self.buffer = self.buffer[self.HeaderLen + nData : ] # descarta o conteúdo já lido
            self.threadResume()
            return(b)

        else:
            self.clearBuffer()
            self.threadResume()
            return b""
    
    def checkBuffer(self):
        # Uma mensagem de transmissão deve ter tamanho mínimo de 28 (header + end_message)
        # 6 init + 2 nº bytes Payload + 1 nº ordens + 13 seq. tamanho de ordens + 6 end
        while (self.getBufferLen() < self.HeaderLen + 6):
            time.sleep(0.05)
            print(f" awaiting for orders...")

        if self.buffer.startswith(START_ORDER): #@ C1 -- start order

            print("Start order reconhecida")
            payload_size    = int.from_bytes(self.buffer[6:8], "little")
            N_commands      = int.from_bytes(self.buffer[8:9], "little")
            seq_size_of_orders  = str(int.from_bytes(self.buffer[9: 9 + 13], "little"))
            
            print(f" A mensagem recebida tem {payload_size} bytes com {N_commands} comandos")

            if self.getBufferLen() >= self.HeaderLen + payload_size:

                payload, orders = self.getData(payload_size, seq_size_of_orders)

            else:
                print("Tamanho não é suficiente")
                time.sleep(0.05)

            if len(orders) == N_commands:
                return payload, orders 

            else:
                return b""
        else:
            self.clearBuffer()
            return b""

    # def getNData(self, size):
    #     print("Reading order received!")
        
    #     while(self.getBufferLen() < 6 + 2 + size +6): #! EDIT: adiciona comandos de start/stop
    #         print(f" searching ... {self.getBufferLen()} of {size + 14}")
    #         time.sleep(0.05)                 
    #     return(self.getBuffer(size))

    def getData(self, payload_size, seq_size_of_orders):
        self.threadPause()
        payload = self.buffer[self.HeaderLen : self.HeaderLen + payload_size]
        orders = []

        i=0
        for size in seq_size_of_orders:
            orders.append(payload[i: i + int(size)])
            i += int(size)
            

        self.threadResume()
        print(f"Comandos identificados: {len(orders)}\n")
        return payload, orders

    def clearBuffer(self):
        self.buffer = b""


