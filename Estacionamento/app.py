import socket
import threading

class MiddlewareApp:
    def __init__(self, estacao_id, vagas, host, port, middleware_host, middleware_port):
        self.estacao_id = estacao_id
        self.vagas = vagas
        self.vagas_ocupadas = 0
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
                numero = message.split()[1]
                if numero == self.estacao_id:
                    self.ativar_estacao()
                    response = f"Estação {self.estacao_id} ativada e pronta para trabalhar com outras estações."
                    self.comunicar_middleware_ativacao()
                else:
                    response = f"Estação {self.estacao_id} não ativada."
            elif "STATUS" in message:
                response = f"Estação {self.estacao_id} está {'ativa' if self.ativo else 'inativa'}."
            elif not self.ativo:
                # Se a estação está inativa, redireciona para a estação ativa mais próxima
                response = self.redirecionar_requisicao()
            else:
                if "RV" in message:
                    response = self.requisitar_vaga()
                elif "LV" in message:
                    response = self.liberar_vaga()

            conn.sendall(response.encode('utf-8'))
            conn.close()

    def ativar_estacao(self):
        self.ativo = True
        print(f"Estação {self.estacao_id} foi ativada.")

    def requisitar_vaga(self):
        if self.vagas_ocupadas < self.vagas:
            self.vagas_ocupadas += 1
            return f"Vaga ocupada. Total ocupadas: {self.vagas_ocupadas}."
        else:
            return "Sem vagas disponíveis."

    def liberar_vaga(self):
        if self.vagas_ocupadas > 0:
            self.vagas_ocupadas -= 1
            return f"Vaga liberada. Total ocupadas: {self.vagas_ocupadas}."
        else:
            return "Não há vagas ocupadas para liberar."

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