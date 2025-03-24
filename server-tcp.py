import socket
import threading
import hashlib
import os

SERVER_HOST = "127.0.0.1" 
SERVER_PORT = 5001
BUFFER_SIZE = 4096


def calcular_hash(arquivo):
    """Calcula o hash MD5 de um arquivo."""
    md5_hash = hashlib.md5()  
    with open(arquivo, "rb") as f:
        while chunk := f.read(BUFFER_SIZE):
            md5_hash.update(chunk)
    return md5_hash.hexdigest()

def enviar_arquivo(client_socket, filename):
    
    if os.path.exists(filename):
        filesize = os.path.getsize(filename)
        file_hash = calcular_hash(filename)

        # Envia metadados (nome, tamanho, hash)
        client_socket.send(f"OK {filename} {filesize} {file_hash}".encode())

        # Envia o arquivo em blocos
        with open(filename, "rb") as f:
            while chunk := f.read(BUFFER_SIZE):
                client_socket.send(chunk)
        print(f"Arquivo {filename} enviado para o cliente.")
    else:
        client_socket.send("ERRO Arquivo não encontrado.".encode())

def handle_tcp_client(client_socket, client_address):
    """Lida com as requisições de um cliente."""
    print(f"[TCP] Conexão estabelecida com {client_address[0]}:{client_address[1]}")

    while True:
        
        request = client_socket.recv(BUFFER_SIZE).decode()
        if not request:
            break

        if request == "Sair":
            print(f"Cliente {client_address[0]}:{client_address[1]} solicitou sair.")
            client_socket.send("Sair".encode())
            break

        elif request.startswith("Arquivo"):
            filename = request.split()[1]
            enviar_arquivo(client_socket, filename)

        elif request == "Chat":
            print(f"Iniciando chat com {client_address[0]}:{client_address[1]}")
            while True:
                mensagem = client_socket.recv(BUFFER_SIZE).decode()
                if mensagem == "Sair":
                    break
                print(f"Cliente {client_address[0]}:{client_address[1]}: {mensagem}")
                resposta = input("Servidor: ")
                client_socket.send(resposta.encode())

    client_socket.close()
    print(f"[TCP] Conexão com {client_address[0]}:{client_address[1]} fechada.")

def tcp_server():
    """Inicia o servidor TCP."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((SERVER_HOST, SERVER_PORT))
    server.listen(5)
    print(f"[TCP] Servidor escutando em {SERVER_HOST}:{SERVER_PORT}...")

    while True:
        client_socket, client_address = server.accept()
        print(f"[TCP] Conexão aceita de {client_address[0]}:{client_address[1]}")
        client_thread = threading.Thread(target=handle_tcp_client, args=(client_socket, client_address))
        client_thread.start()

if __name__ == "__main__":
    tcp_server()