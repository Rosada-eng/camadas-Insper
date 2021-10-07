#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#####################################################
#Carareto
#17/02/2018
####################################################

# Importa pacote de comunicação serial
import serial

# importa pacote para conversão binário ascii
import binascii

#! ====== FUNÇÕES AUXILIARES:
def bytes_to_int(bytes):
    """ Converte o número em bytes para inteiro"""
    return int.from_bytes(bytes, byteorder='little')

def int_to_bytes(numbers, bytes_size=1):
    """ Converte o número inteiro para bytes no tamanho especificado"""
    return numbers.to_bytes(bytes_size, byteorder='little')

#! ======


#################################
# Interface com a camada física #
#################################
class Fisica(object):
    def __init__(self, name):
        self.name        = name
        self.port        = None
        self.baudrate    = 115200
        # self.baudrate    = 9600
        self.bytesize    = serial.EIGHTBITS
        self.parity      = serial.PARITY_NONE
        self.stop        = serial.STOPBITS_ONE
        self.timeout     = 0.1
        self.rxRemain    = b""

        self.HeaderLen   = 10
        self.EOP         = b'\xff\xaa\xff\xaa'
        self.EOPLen      = len(self.EOP)


    def open(self):
        self.port = serial.Serial(self.name,
                                  self.baudrate,
                                  self.bytesize,
                                  self.parity,
                                  self.stop,
                                  self.timeout)

        if not self.port.isOpen():
            self.port.open()


    def close(self):
        self.port.close()

    def flush(self):
        self.port.flushInput()
        self.port.flushOutput()

    def encode(self, data):
        encoded = binascii.hexlify(data)
        return(encoded)

    def decode(self, data):
        """ RX ASCII data after reception
        """
        decoded = binascii.unhexlify(data)
        return(decoded)

    def write(self, txBuffer):
        """ Write data to serial port

        This command takes a buffer and format
        it before transmit. This is necessary
        because the pyserial and arduino uses
        Software flow control between both
        sides of communication.
        """
        nTx = self.port.write(self.encode(txBuffer))
        self.port.flush()
        return(nTx/2)

    def read(self, nBytes):
        """ Read nBytes from the UART com port

        Nem toda a leitura retorna múltiplo de 2
        devemos verificar isso para evitar que a funcao
        self.decode seja chamada com números ímpares.
        """
        rxBuffer = self.port.read(nBytes)
        rxBufferConcat = self.rxRemain + rxBuffer
        nValid = (len(rxBufferConcat)//2)*2
        rxBufferValid = rxBufferConcat[0:nValid]
        self.rxRemain = rxBufferConcat[nValid:]
        try :
            """ As vezes acontece erros na decodificacao
            fora do ambiente linux, isso tenta corrigir
            em parte esses erros. Melhorar futuramente."""
            # "muitas vezes um flush no inicio resolve!"
            rxBufferDecoded = self.decode(rxBufferValid)
            nRx = len(rxBuffer)
            return(rxBufferDecoded, nRx)
        except :
            print("[ERRO] interfaceFisica, read, decode. buffer : {}".format(rxBufferValid))
            return(b"", 0)
