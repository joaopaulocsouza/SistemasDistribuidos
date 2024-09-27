import socket
import threading
import json

ring = [] 
semaforo = threading.Semaphore(1)

def add_con_ring(conn, port):
    global ring
    semaforo.acquire()
    if len(ring) == 0:
        ring.append([conn, port])
    else:
        ring.append([conn, port])
    print(ring)
    semaforo.release()

def remove_con_ring(conn, port):
    global ring
    semaforo.acquire()
    ring.remove({conn, port})
    semaforo.release()
    
class Gerente:
    global flag, ring
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.estacoes = {}  # Armazena informações de todas as estações
    
    def start_server(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen(10)
        print(f"Gerente está escutando em {self.host}:{self.port}")
        
        while True:
            conn, addr = server_socket.accept()
            print(f"Conexão estabelecida com {addr}")
            threading.Thread(target=self.handle_connection, args=(conn, addr)).start()
    
    def handle_connection(self, conn, addr):
        while True:
            try:
                message = conn.recv(4096).decode('utf-8')
                if not message:
                    break
                print(f"Gerente recebeu: {message}")
                
                if "ATUALIZAR" in message:
                    estacao_id, status, vagas, vagas_ocupadas, carros, middleware_port = message.split()[1:]
                    response = f"Estação {estacao_id} atualizada com sucesso."
                else:
                    response = "Comando desconhecido."
                
                conn.sendall(response.encode('utf-8'))
            except ConnectionResetError:
                print(f"Conexão perdida com {addr}")
                break
            except Exception as e:
                print(f"Erro na conexão com {addr}: {e}")
                break
        conn.send("Oi".encode('utf-8'))
        # Não fechar a conexão para manter a comunicação contínua
        # print(f"Conexão ainda ativa com {addr}")
        # conn.close()  # Remover o fechamento da conexão para manter ativo.

    
if __name__ == "__main__":
    gerente = Gerente('127.0.0.1', 5000)
    threading.Thread(target=gerente.start_server).start()