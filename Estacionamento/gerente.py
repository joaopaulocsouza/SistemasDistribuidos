import socket
import threading
import json

class Gerente:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.estacoes = {}  # Armazena informações de todas as estações

    def atualizar_estacao(self, estacao_id, status, vagas, vagas_ocupadas, carros):
        self.estacoes[estacao_id] = {
            'status': status,
            'vagas': vagas,
            'vagas_ocupadas': vagas_ocupadas,
            'carros': carros
        }
        print(f"Gerente: Estação {estacao_id} atualizada.")

    def obter_status_estacoes(self):
        return json.dumps(self.estacoes, indent=4)

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
            message = conn.recv(4096).decode('utf-8')
            print(f"Gerente recebeu: {message}")

            if "ATUALIZAR" in message:
                # Ajusta o split para considerar espaços em dados com listas
                dados = message.split(' ', 5)
                estacao_id = dados[1]
                status = dados[2]
                vagas = int(dados[3])
                vagas_ocupadas = int(dados[4])
                carros_str = dados[5]
                carros = json.loads(carros_str)  # Usa json para carregar a lista de carros
                self.atualizar_estacao(estacao_id, status, vagas, vagas_ocupadas, carros)
                response = f"Estação {estacao_id} atualizada."
            elif "STATUS" in message:
                response = self.obter_status_estacoes()
            else:
                response = "Comando desconhecido."

            conn.sendall(response.encode('utf-8'))
        except Exception as e:
            print(f"Erro ao processar conexão: {e}")
        finally:
            conn.close()

# Iniciando o Gerente
if __name__ == "__main__":
    gerente = Gerente('127.0.0.1', 5000)
    threading.Thread(target=gerente.start_server).start()
