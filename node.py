import threading
import time
import socket
import random
from message import Mensagem, TipoMensagem
from utils import enviar_mensagem

class No:
    def __init__(self, id_no, pares):
        self.id_no = id_no
        self.estado = 'Seguidor'  # Possíveis estados: Seguidor, Candidato, Líder
        self.termo_atual = 0
        self.votou_para = None
        self.log = []
        self.indice_comprometido = 0
        self.ultimo_aplicado = 0
        self.pares = pares  
        self.id_lider = None
        self.temporizador_eleicao = self.redefinir_temporizador_eleicao()
        self.trava = threading.Lock()
        self.thread_execucao = threading.Thread(target=self.executar)
        self.thread_execucao.start()

    def redefinir_temporizador_eleicao(self):
        return time.time() + random.uniform(5, 10)

    def executar(self):
        while True:
            time.sleep(0.1)
            with self.trava:
                if self.estado == 'Líder':
                    self.enviar_heartbeats()
                if time.time() >= self.temporizador_eleicao:
                    self.iniciar_eleicao()

    def enviar_heartbeats(self):
        for par in self.pares:
            msg = Mensagem(TipoMensagem.AdicionarEntradas, self.id_no, self.termo_atual, {})
            enviar_mensagem(par, msg)

    def iniciar_eleicao(self):
        self.estado = 'Candidato'
        self.termo_atual += 1
        self.votou_para = self.id_no
        votos_recebidos = 1  
        self.temporizador_eleicao = self.redefinir_temporizador_eleicao()
        print(f"Nó {self.id_no} iniciando eleição para o termo {self.termo_atual}")

        for par in self.pares:
            msg = Mensagem(TipoMensagem.SolicitarVoto, self.id_no, self.termo_atual, {})
            enviar_mensagem(par, msg)

        
        if votos_recebidos > len(self.pares) // 2:
            self.tornar_lider()

    def tornar_lider(self):
        self.estado = 'Líder'
        self.id_lider = self.id_no
        print(f"Nó {self.id_no} tornou-se Líder para o termo {self.termo_atual}")

    def tratar_mensagem(self, msg):
        with self.trava:
            if msg.termo > self.termo_atual:
                self.termo_atual = msg.termo
                self.estado = 'Seguidor'
                self.votou_para = None
            if msg.tipo == TipoMensagem.SolicitarVoto:
                self.tratar_solicitacao_voto(msg)
            elif msg.tipo == TipoMensagem.AdicionarEntradas:
                self.tratar_adicionar_entradas(msg)

    def tratar_solicitacao_voto(self, msg):
        if (self.votou_para is None or self.votou_para == msg.id_remetente) and msg.termo >= self.termo_atual:
            self.votou_para = msg.id_remetente
            self.temporizador_eleicao = self.redefinir_temporizador_eleicao()
            resposta = Mensagem(TipoMensagem.RespostaSolicitacaoVoto, self.id_no, self.termo_atual, {'voto_concedido': True})
            enviar_mensagem(('localhost', msg.id_remetente), resposta)

    def tratar_adicionar_entradas(self, msg):
        self.id_lider = msg.id_remetente
        self.temporizador_eleicao = self.redefinir_temporizador_eleicao()

    def simular_falha(self):
        self.estado = 'Falho'
        print(f"Nó {self.id_no} falhou.")

    def recuperar(self):
        self.estado = 'Seguidor'
        self.temporizador_eleicao = self.redefinir_temporizador_eleicao()
        print(f"Nó {self.id_no} se recuperou.")
