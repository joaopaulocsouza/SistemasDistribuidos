import socket
import threading
import json
import time

ring = [] 
semaforo = threading.Semaphore(1)
semaforo_message = threading.Semaphore(1)    


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
        global ring
        semaforo.acquire()
        try:
            print(f"Adicionando conexão ao anel {port}\n")
            if [conn, port] in ring:
                print("Conexão já existe no anel\n")
                semaforo.release()
                return
            if len(ring) == 0:
                ring.append([conn, port])
            else:
                self.send_message(ring[len(ring)-1][0], f"NEXT {port}")
                self.send_message(conn, f"NEXT {ring[0][1]}")
                print(f"Enviando NEXT {ring[0][1]} para {port}\n")
                print(f"Enviando NEXT {port} para {ring[len(ring)-1][1]}\n")
                ring.append([conn, port])
        except Exception as e:
                print(e)
        semaforo.release()

    def remove_con_ring(self, port):
        global ring
        semaforo.acquire()
        if(len(ring) == 1):
            ring.pop()
        else:
            for i in range(len(ring)):
                # if ring[i][1] == port:
                #     if i == 0:
                #         self.send_message(ring[len(ring)-1][1], f"NEXT {[1][1]}")
                #     elif i == len(ring)-1:
                #         self.send_message(ring[len(ring)-2][0], f"NEXT {ring[0][1]}")
                #     else:
                #         self.send_message(ring[i+1][0], f"NEXT {ring[i-1][1]}")
                #     ring.pop(i)
                    break
        semaforo.release()

    def obter_status_estacoes(self):
        return json.dumps(self.estacoes, indent=4)

    def send_message(self, conn, message):
        """Função para enviar mensagens de forma segura entre threads."""
        semaforo_message.acquire()
        try:
            conn.send(f'{message}\n'.encode('utf-8'))
        except Exception as e:
            print(f"Erro ao enviar mensagem: {e}")
        finally:
            semaforo_message.release()

    def start_server(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen(10)  # Aumenta o número de conexões simultâneas
        print(f"Gerente escutando em {self.host}:{self.port}...")

        while True:
            conn, addr = server_socket.accept()
            threading.Thread(target=self.handle_connection, args=(conn,)).start()
            
    def obter_todas_informacoes_estacoes(self):
        """Função que retorna todas as informações das estações no formato de dicionário."""
        return self.estacoes  # Retorna o dicionário completo das estações
        
    def handle_connection(self, conn):
        try:
            data = b''
            while True:
                buffer = conn.recv(1024)
                if not buffer:
                    continue
                data += buffer
                while b'\n' in data:
                    message, data = data.split(b'\n', 1)  # Divide os dados em duas partes
                    message = message.decode('utf-8').strip() 
                    print(f"Gerente recebeu: {message}")
                    
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

                    elif "INFO" in message:
                        # Retorna todas as informações das estações
                        estacoes_info = self.obter_todas_informacoes_estacoes()
                        response = json.dumps(estacoes_info, indent=4)
                    elif "ELECTION" in message:
                        print("Election")
                    else:
                        continue
                        response = "Comando desconhecido."
                        
                    self.send_message(conn, response)
        except Exception as e:
            print(f"Erro ao processar conexão: {e}")
        finally:
            conn.close()

def obter_status_estacoes(self):
        return json.dumps(self.estacoes, indent=4)
        
# Iniciando o Gerente
if __name__ == "__main__":
    gerente = Gerente('127.0.0.1', 5000)
    threading.Thread(target=gerente.start_server).start()
