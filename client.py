import socket
import hashlib

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5001
BUFFER_SIZE = 4096

def calcular_hash(arquivo):
    """Calcula o hash MD5 de um arquivo."""
    md5_hash = hashlib.md5()  # Usando MD5
    with open(arquivo, "rb") as f:
        while chunk := f.read(BUFFER_SIZE):
            md5_hash.update(chunk)
    return md5_hash.hexdigest()

def baixar_arquivo(client_socket, filename):
    """Recebe um arquivo do servidor e verifica sua integridade."""
    metadata = client_socket.recv(BUFFER_SIZE).decode()
    if metadata.startswith("OK"):
        _, filename, filesize, server_hash = metadata.split()
        filesize = int(filesize)
        with open(filename, "wb") as f:
            recebido = 0
            while recebido < filesize:
                chunk = client_socket.recv(BUFFER_SIZE)
                f.write(chunk)
                recebido += len(chunk)
        local_hash = calcular_hash(filename)
        if local_hash == server_hash:
            print(f"✅ Arquivo {filename} recebido com sucesso! (Checksum OK)")
        else:
            print(f"❌ Erro: Checksum não bate! Arquivo pode estar corrompido.")
    else:
        print("❌ Arquivo não encontrado no servidor.")

def chat(client_socket):
    """Inicia um chat com o servidor."""
    while True:
        mensagem = input("Você: ")
        client_socket.send(mensagem.encode())
        if mensagem.lower() == "sair":
            break
        resposta = client_socket.recv(BUFFER_SIZE).decode()
        print(f"Servidor: {resposta}")

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_HOST, SERVER_PORT))
    while True:
        print("\n📌 Opções:")
        print("1 - Baixar arquivo")
        print("2 - Chat")
        print("3 - Sair")
        escolha = input("Escolha uma opção: ")
        if escolha == "1":
            filename = input("Nome do arquivo: ")
            client_socket.send(f"Arquivo {filename}".encode())
            baixar_arquivo(client_socket, filename)
        elif escolha == "2":
            chat(client_socket)
        elif escolha == "3":
            client_socket.send("Sair".encode())
            break
        else:
            print("❌ Opção inválida!")
    client_socket.close()

if __name__ == "__main__":
    main()