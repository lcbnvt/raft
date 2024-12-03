from node import No
from utils import iniciar_servidor
import threading

def main():
    id_no = int(input("Insira o ID do nó (número da porta): "))
    entrada_pares = input("Insira os IDs dos nós pares, separados por vírgulas: ")
    pares = [('localhost', int(pid.strip())) for pid in entrada_pares.split(',') if pid.strip()]
    no = No(id_no, pares)
    thread_servidor = threading.Thread(target=iniciar_servidor, args=(no,))
    thread_servidor.start()

if __name__ == "__main__":
    main()
