import socket
import threading
import json
import time

ring = [] 
semaforo = threading.Semaphore(1)


class Gerente:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.estacoes = {}  # Armazena informações de todas as estações

    def atualizar_estacao(self, estacao_id, status, vagas, vagas_ocupadas, carros, conn, port):
        self.estacoes[estacao_id] = {
            'status': status,
            'vagas': vagas,
            'vagas_ocupadas': vagas_ocupadas,
            'carros': carros
        }
        self.add_con_ring(conn, port)
        print(f"Gerente: Estação {estacao_id} atualizada.")
    
    def add_con_ring(self, conn, port):
        print(f"Adicionando conexão ao anel {port}\n")
        global ring
        semaforo.acquire()
        if [conn, port] in ring:
            semaforo.release()
            return
        if len(ring) == 0:
            self.send_message(conn, "NEXT ")
            ring.append([conn, port])
            time.sleep(0.5)
        else:
            try:
                self.send_message(conn, f"NEXT {ring[0][1]}")
                time.sleep(0.5)
                self.send_message(ring[len(ring)-1][0], f"NEXT {port}")
                time.sleep(0.5)
                ring.append([conn, port])
            except Exception as e:
                print(e)
        semaforo.release()

    def remove_con_ring(self, conn, port):
        global ring
        semaforo.acquire()
        ring.remove({conn, port})
        semaforo.release()

    def obter_status_estacoes(self):
        return json.dumps(self.estacoes, indent=4)

    def send_message(self, conn, message):
        """Função para enviar mensagens de forma segura entre threads."""
        semaforo.acquire()
        try:
            conn.send(message.encode('utf-8'))
        except Exception as e:
            print(f"Erro ao enviar mensagem: {e}")
        finally:
            semaforo.release()

    def start_server(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen(10)  # Aumenta o número de conexões simultâneas
        print(f"Gerente escutando em {self.host}:{self.port}...")

        while True:
            conn, addr = server_socket.accept()
            threading.Thread(target=self.handle_connection, args=(conn,)).start()

    def handle_connection(self, conn):
        try:
            while True:
                time.sleep(0.5)
                message = conn.recv(4096).decode('utf-8')
                print(f"Gerente recebeu: {message}")
                
                if not message:
                    continue
                
                if "ATUALIZAR" in message:
                    # Ajusta o split para considerar espaços em dados com listas
                    dados = message.split(' ', 6)
                    estacao_id = dados[1]
                    status = dados[2]
                    vagas = int(dados[3])
                    vagas_ocupadas = int(dados[4])
                    carros_str = dados[5]
                    port = dados[6]
                    carros = json.loads(carros_str)  # Usa json para carregar a lista de carros
                    self.atualizar_estacao(estacao_id, status, vagas, vagas_ocupadas, carros, conn, port)
                    continue
                
                elif "STATUS" in message:
                    response = self.obter_status_estacoes()
                elif "ELECTION" in message:
                    print("Election")
                else:
                    response = "Comando desconhecido."

                time.sleep(0.5)
                self.send_message(conn, response)
        except Exception as e:
            print(f"Erro ao processar conexão: {e}")
        finally:
            conn.close()

# Iniciando o Gerente
if __name__ == "__main__":
    gerente = Gerente('127.0.0.1', 5000)
    threading.Thread(target=gerente.start_server).start()
