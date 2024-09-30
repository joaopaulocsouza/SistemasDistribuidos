import socket
import threading
import json

class Gerente:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.estacoes = {}  # Armazena informações de todas as estações
        
        self.estacoes_ativas = []  # Armazena as estações ativas

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
            
    def obter_todas_informacoes_estacoes(self):
        """Função que retorna todas as informações das estações no formato de dicionário."""
        return self.estacoes  # Retorna o dicionário completo das estações
    
    def atualizar_carros(self, estacao_id, acao, carro_id):
        """Atualiza a lista de carros e o número de vagas ocupadas de uma estação."""
        estacao = self.estacoes.get(estacao_id)
        if not estacao:
            print(f"Estação {estacao_id} não encontrada no Gerente.")
            return f"Estação {estacao_id} não encontrada."

        if acao == "ENTRADA":
            if carro_id not in estacao['carros']:
                estacao['carros'].append(carro_id)
                estacao['vagas_ocupadas'] += 1
                print(f"Carro {carro_id} entrou na estação {estacao_id}. Vagas ocupadas: {estacao['vagas_ocupadas']}.")
            else:
                print(f"Carro {carro_id} já está registrado na estação {estacao_id}.")
                return f"Carro {carro_id} já registrado."

        elif acao == "SAIDA":
            if carro_id in estacao['carros']:
                estacao['carros'].remove(carro_id)
                estacao['vagas_ocupadas'] -= 1
                print(f"Carro {carro_id} saiu da estação {estacao_id}. Vagas ocupadas: {estacao['vagas_ocupadas']}.")
            else:
                print(f"Carro {carro_id} não encontrado na estação {estacao_id}.")
                return f"Carro {carro_id} não encontrado."

        return f"Estação {estacao_id} atualizada com o carro {carro_id}."


    def handle_connection(self, conn):
        try:
            message = conn.recv(4096).decode('utf-8')
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
                self.atualizar_estacao(estacao_id, status, vagas, vagas_ocupadas, carros)
                print(f"ATT: {estacao_id} {status} {vagas} {vagas_ocupadas} {carros}")
                
                if status == "ATIVA":
                    nova_estacao = (estacao_id, port)
                    if nova_estacao not in self.estacoes_ativas:
                        self.estacoes_ativas.append(nova_estacao)
                        print(f"Estação {estacao_id} adicionada à lista de ativas.")
                
                        self.notificar_estacoes_ativas()
                
                response = f"Estação {estacao_id} atualizada."
            
            elif "STATUS" in message:
                response = self.obter_status_estacoes()

            elif "INFO" in message:
                # Retorna todas as informações das estações
                estacoes_info = self.obter_todas_informacoes_estacoes()
                response = json.dumps(estacoes_info, indent=4)
            
            elif "ENTRADA" in message or "SAIDA" in message:
                # Atualizar a lista de carros em uma estação
                dados = message.split()
                acao = dados[0].lower()
                estacao_id = dados[1]
                carro_id = dados[2]
                response = self.atualizar_carros(estacao_id, acao.upper(), carro_id)

            else:
                response = "Comando desconhecido."

            conn.sendall(response.encode('utf-8'))
        except Exception as e:
            print(f"Erro ao processar conexão: {e}")
        finally:
            conn.close()
            
            
    def notificar_estacoes_ativas(self):
        """Notifica todas as estações ativas sobre a nova configuração do anel."""
        num_estacoes = len(self.estacoes_ativas)
        for i in range(num_estacoes):
            estacao_atual = self.estacoes_ativas[i]
            estacao_proxima = self.estacoes_ativas[(i + 1) % num_estacoes]

            # Envia mensagem para a estação atual informando a próxima estação
            self.enviar_informacao_proxima_estacao(estacao_atual, estacao_proxima)
    
    def enviar_informacao_proxima_estacao(self, estacao_atual, estacao_proxima):
        """Envia a nova configuração de próxima estação para a estação atual."""
        nome_atual, porta_atual = estacao_atual
        nome_proxima, porta_proxima = estacao_proxima

        mensagem = f"UPDATE_NEXT {nome_proxima} {porta_proxima}"
        try:
            # Envia a mensagem para a estação atual
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(('127.0.0.1', int(porta_atual)))
            sock.sendall(mensagem.encode())
            print(f"Notificado {nome_atual} para conectar-se a {nome_proxima}")
            sock.close()
        except Exception as e:
            print(f"Erro ao enviar atualização para {nome_atual}: {e}")

def obter_status_estacoes(self):
        return json.dumps(self.estacoes, indent=4)
        
# Iniciando o Gerente
if __name__ == "__main__":
    gerente = Gerente('127.0.0.1', 5000)
    threading.Thread(target=gerente.start_server).start()