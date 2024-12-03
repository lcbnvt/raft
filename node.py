import threading
import time
import socket
import random
from message import Mensagem, TipoMensagem
from utils import enviar_mensagem

class No:
    def __init__(self, id_no, pares):
        self.id_no = id_no
        self.estado = 'Seguidor'  # Possíveis estados: Seguidor, Candidato, Líder, Falho
        self.termo_atual = 0
        self.votou_para = None
        self.log = []
        self.indice_comprometido = 0
        self.ultimo_aplicado = 0
        self.pares = pares  # Lista de endereços dos nós pares
        self.id_lider = None
        self.temporizador_eleicao = self.redefinir_temporizador_eleicao()
        self.trava = threading.Lock()
        self.thread_execucao = threading.Thread(target=self.executar)
        self.thread_execucao.start()
        self.votos_recebidos = 0  # Contagem de votos recebidos
        self.ativo = True  # Indica se o nó está ativo ou falho

    def redefinir_temporizador_eleicao(self):
        return time.time() + random.uniform(5, 10)

    def executar(self):
        while True:
            time.sleep(0.1)
            with self.trava:
                tempo_atual = time.time()
                if self.estado != 'Falho':
                    if not hasattr(self, 'tempo_falha'):
                        # Definir o próximo tempo de falha
                        self.tempo_falha = tempo_atual + random.uniform(20, 30)
                    elif tempo_atual >= self.tempo_falha:
                        # Definir o próximo tempo de recuperação
                        self.tempo_recuperacao = tempo_atual + random.uniform(10, 15)
                        self.simular_falha()
                        continue
                    if self.estado == 'Líder':
                        self.enviar_heartbeats()
                    if tempo_atual >= self.temporizador_eleicao:
                        self.iniciar_eleicao()
                else:
                    if tempo_atual >= self.tempo_recuperacao:
                        self.recuperar()
                        # Remover tempos para que sejam redefinidos
                        del self.tempo_falha
                        del self.tempo_recuperacao

    def enviar_heartbeats(self):
        for par in self.pares:
            msg = Mensagem(TipoMensagem.AdicionarEntradas, self.id_no, self.termo_atual, {})
            enviar_mensagem(par, msg)

    def iniciar_eleicao(self):
        self.estado = 'Candidato'
        self.termo_atual += 1
        self.votou_para = self.id_no
        self.votos_recebidos = 1  # Vota em si mesmo
        self.temporizador_eleicao = self.redefinir_temporizador_eleicao()
        print(f"Nó {self.id_no} iniciando eleição para o termo {self.termo_atual}")

        for par in self.pares:
            msg = Mensagem(TipoMensagem.SolicitarVoto, self.id_no, self.termo_atual, {})
            enviar_mensagem(par, msg)

    def tornar_lider(self):
        self.estado = 'Líder'
        self.id_lider = self.id_no
        print(f"Nó {self.id_no} tornou-se Líder para o termo {self.termo_atual}")

    def tratar_mensagem(self, msg):
        if not self.ativo:
            return  # Ignora mensagens se o nó está falho
        with self.trava:
            if msg.termo > self.termo_atual:
                self.termo_atual = msg.termo
                self.estado = 'Seguidor'
                self.votou_para = None
            if msg.tipo == TipoMensagem.SolicitarVoto:
                self.tratar_solicitacao_voto(msg)
            elif msg.tipo == TipoMensagem.RespostaSolicitacaoVoto:
                self.tratar_resposta_solicitacao_voto(msg)
            elif msg.tipo == TipoMensagem.AdicionarEntradas:
                self.tratar_adicionar_entradas(msg)

    def tratar_solicitacao_voto(self, msg):
        if (self.votou_para is None or self.votou_para == msg.id_remetente) and msg.termo >= self.termo_atual:
            self.votou_para = msg.id_remetente
            self.temporizador_eleicao = self.redefinir_temporizador_eleicao()
            resposta = Mensagem(TipoMensagem.RespostaSolicitacaoVoto, self.id_no, self.termo_atual, {'voto_concedido': True})
            print(f"Nó {self.id_no} votou em {msg.id_remetente} para o termo {msg.termo}")
        else:
            resposta = Mensagem(TipoMensagem.RespostaSolicitacaoVoto, self.id_no, self.termo_atual, {'voto_concedido': False})
            print(f"Nó {self.id_no} negou voto a {msg.id_remetente} para o termo {msg.termo}")
        enviar_mensagem(('localhost', msg.id_remetente), resposta)

    def tratar_resposta_solicitacao_voto(self, msg):
        if self.estado != 'Candidato':
            return
        if msg.dados.get('voto_concedido'):
            self.votos_recebidos += 1
            print(f"Nó {self.id_no} recebeu voto de {msg.id_remetente}. Total de votos: {self.votos_recebidos}")
            if self.votos_recebidos > len(self.pares) // 2:
                self.tornar_lider()

    def tratar_adicionar_entradas(self, msg):
        if msg.termo >= self.termo_atual:
            self.estado = 'Seguidor'
            self.id_lider = msg.id_remetente
            self.temporizador_eleicao = self.redefinir_temporizador_eleicao()
            print(f"Nó {self.id_no} recebeu heartbeat do líder {msg.id_remetente} para o termo {msg.termo}")
        else:
            # Ignora mensagens com termos menores
            pass

    def simular_falha(self):
        self.estado = 'Falho'
        self.ativo = False
        print(f"Nó {self.id_no} falhou no tempo {time.time():.2f}. Próxima recuperação em {self.tempo_recuperacao - time.time():.2f} segundos.")

    def recuperar(self):
        self.estado = 'Seguidor'
        self.temporizador_eleicao = self.redefinir_temporizador_eleicao()
        self.ativo = True
        print(f"Nó {self.id_no} se recuperou no tempo {time.time():.2f}.")
