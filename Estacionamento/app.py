import socket
import threading
import random  # Para escolher uma estação ativa aleatoriamente

class MiddlewareApp:
    def __init__(self, estacao_id, vagas, host, port, middleware_host, middleware_port):
        self.estacao_id = estacao_id
        self.vagas = vagas
        self.vagas_ocupadas = 0
        self.carros_estacionados = []  # Lista para armazenar os IDs dos carros que ocupam vagas
        self.host = host
        self.port = port
        self.middleware_host = middleware_host
        self.middleware_port = middleware_port
        self.ativo = False  # Todas as estações começam inativas

    def start_server(self):
        # Inicia o servidor para se comunicar com o carro
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        print(f"App {self.estacao_id} aguardando conexões do carro na porta {self.port}...")

        while True:
            conn, addr = server_socket.accept()
            message = conn.recv(1024).decode('utf-8')
            print(f"App {self.estacao_id} recebeu: {message} do carro")

            if "AE" in message:
                # Ativa a própria estação ao receber "AE"
                self.ativar_estacao()
                response = f"Estação {self.estacao_id} ativada e pronta para trabalhar com outras estações."
                self.comunicar_middleware_ativacao()
            elif "STATUS" in message:
                response = f"Estação {self.estacao_id} está {'ativa' if self.ativo else 'inativa'}."
            elif not self.ativo:
                # Se a estação está inativa, redireciona para a estação ativa mais próxima
                response = self.redirecionar_requisicao()
            else:
                if "RV" in message:
                    id_message = message.split(".")[1]  # Extrai o ID do carro da mensagem (formato RV.id)
                    response = self.requisitar_vaga(id_message)
                    # Após a requisição da vaga, imprime as estações ativas que o middleware retornou
                    estacoes_ativas = self.obter_estacoes_ativas()
                    print(f"Carro {id_message} inserido. Estações ativas: {estacoes_ativas}\n")
                
                elif "LV" in message:
                    id_message = message.split(".")[1]  # Extrai o ID do carro da mensagem (formato LV.id)
                    response = self.liberar_vaga(id_message)

            conn.sendall(response.encode('utf-8'))
            conn.close()

    def ativar_estacao(self):
        self.ativo = True
        print(f"Estação {self.estacao_id} foi ativada.")

    def requisitar_vaga(self, carro_id):
        if self.vagas_ocupadas < self.vagas:
            self.vagas_ocupadas += 1
            self.carros_estacionados.append(carro_id)  # Adiciona o ID do carro à lista de carros estacionados
            return f"Vaga ocupada pelo carro {carro_id}. Total ocupadas: {self.vagas_ocupadas}."
        else:
            return "Sem vagas disponíveis."

    def liberar_vaga(self, carro_id):
        # Verifica se o carro está na própria estação
        if carro_id in self.carros_estacionados:
            # Remove o carro e libera a vaga na estação atual
            self.vagas_ocupadas -= 1
            self.carros_estacionados.remove(carro_id)  # Remove o ID do carro da lista
            return f"Vaga liberada pelo carro {carro_id}. Total ocupadas: {self.vagas_ocupadas}."

        # Caso o carro não esteja na estação, verificar nas outras estações
        else:
            print(f"Carro {carro_id} não encontrado na estação {self.estacao_id}. Verificando outras estações...")
            estacao_encontrada = self.buscar_carro_em_outras_estacoes(carro_id)
            if estacao_encontrada:
                return f"Carro {carro_id} removido da estação {estacao_encontrada}."
            else:
                return f"Carro {carro_id} não encontrado em nenhuma estação."

    def buscar_carro_em_outras_estacoes(self, carro_id):
        # Verifica em outras estações se o carro está estacionado
        for i in range(10):  # Supondo que há 10 estações
            if f"E{i}" == self.estacao_id:
                continue  # Pula a estação atual

            middleware_port = 9000 + i  # Porta do middleware da estação
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                try:
                    client_socket.connect(('127.0.0.1', middleware_port))
                    client_socket.sendall(f"CHECK {carro_id}".encode('utf-8'))
                    response = client_socket.recv(1024).decode('utf-8')

                    if "FOUND" in response:
                        # Carro encontrado, solicitar remoção
                        client_socket.sendall(f"REMOVE {carro_id}".encode('utf-8'))
                        print(f"Carro {carro_id} removido da estação E{i}")
                        return f"E{i}"  # Retorna a estação onde o carro foi encontrado
                except ConnectionRefusedError:
                    print(f"Falha ao conectar ao middleware da estação E{i}")

        return None  # Carro não encontrado em nenhuma estação

    def comunicar_middleware_ativacao(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((self.middleware_host, self.middleware_port))
            client_socket.sendall(f"ACTIVATE {self.estacao_id}".encode('utf-8'))
            response = client_socket.recv(1024).decode('utf-8')
            print(f"Middleware resposta: {response}")

    def redirecionar_requisicao(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((self.middleware_host, self.middleware_port))
            client_socket.sendall(f"REDIRECT {self.estacao_id}".encode('utf-8'))
            response = client_socket.recv(1024).decode('utf-8')
            return response

    def obter_estacoes_ativas(self):
        # Consulta o middleware para obter a lista de estações ativas
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((self.middleware_host, self.middleware_port))
            client_socket.sendall(f"LIST".encode('utf-8'))
            response = client_socket.recv(1024).decode('utf-8')
            return response


# Inicializando 10 estações em threads diferentes
def inicializar_estacao(estacao_id, app_port, middleware_port):
    middleware_app = MiddlewareApp(estacao_id, 10, '127.0.0.1', app_port, '127.0.0.1', middleware_port)
    threading.Thread(target=middleware_app.start_server).start()
    if estacao_id == 'E0':
        # Ativando automaticamente a primeira estação (E0) ao iniciar
        middleware_app.ativar_estacao()
        middleware_app.comunicar_middleware_ativacao()


for i in range(0, 10):
    estacao_id = f'E{i}'
    app_port = 3000 + i  # Porta para o App
    middleware_port = 9000 + i  # Porta única para cada middleware
    inicializar_estacao(estacao_id, app_port, middleware_port)
