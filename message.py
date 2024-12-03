from enum import Enum

class TipoMensagem(Enum):
    SolicitarVoto = 1
    RespostaSolicitacaoVoto = 2
    AdicionarEntradas = 3
    RespostaAdicionarEntradas = 4

class Mensagem:
    def __init__(self, tipo_msg, id_remetente, termo, dados):
        self.tipo = tipo_msg
        self.id_remetente = id_remetente
        self.termo = termo
        self.dados = dados
