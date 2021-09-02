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
        b           = self.buffer[8 : nData+8]
        if self.buffer[nData+8: nData+15] == END_ORDER: #@ C2 -- end order
            self.buffer = self.buffer[nData+14 : ] # descarta o conteúdo já lido
            self.threadResume()
            return(b)

        else:
            self.clearBuffer()
            self.threadResume()
            return b""
    
    def checkBuffer(self):
        while (self.getBufferLen() < 15):
            time.sleep(0.05)
            print(f" awaiting for orders...")

        if self.buffer.startswith(START_ORDER): #@ C1 -- start order
            message_size = int.from_bytes(self.buffer[6:8], "little")
            print(f" A mensagem recebida tem {message_size} bytes")
            return self.getNData(message_size)
        else:
            self.clearBuffer()
            return b""

    def getNData(self, size):
        print("Reading order received!")
        
        while(self.getBufferLen() < 6 + 2 + size +6): #! EDIT: adiciona comandos de start/stop
            print(f" searching ... {self.getBufferLen()} of {size + 14}")
            time.sleep(0.05)                 
        return(self.getBuffer(size))

    def clearBuffer(self):
        self.buffer = b""


