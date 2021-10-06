class TimeOutError(Exception):
    message = "Comunicação excedeu os 20 seg"

class ClientDropError(Exception):
    message = "Comunicação com o cliente caiu."

class ServerDropError(Exception):
    message = "Comunicação com o servidor caiu."

class ReadFileError(Exception):
    message = "Não foi possível ler o arquivo solicitado."

class SaveFileError(Exception):
    message = "Não foi possível salvar o arquivo recebido no destino final."

class SendHandshakeError(Exception):
    message = "Não foi possível enviar o Handshake"

class ConvertPackagesError(Exception):
    message = "Não foi converter o arquivo em pacotes de envio."

class WrongServerError(Exception):
    message = "Cliente está tentando conectar com o servidor errado."

class WrongClientError(Exception):
    message = "Pacote atual provém de uma comunicação em paralelo com outro cliente."