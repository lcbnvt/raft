import socket
import pickle

def enviar_mensagem(endereco, mensagem):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(endereco)
        sock.sendall(pickle.dumps(mensagem))
        sock.close()
    except ConnectionRefusedError:
        pass

def iniciar_servidor(no):
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind(('localhost', no.id_no))
    servidor.listen(5)
    print(f"Nó {no.id_no} ouvindo na porta {no.id_no}")
    while True:
        conn, addr = servidor.accept()
        dados = conn.recv(4096)
        if dados:
            mensagem = pickle.loads(dados)
            no.tratar_mensagem(mensagem)
        conn.close()
