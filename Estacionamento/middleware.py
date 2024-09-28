import socket
import threading
import json

class Middleware:
    def __init__(self, estacao_id, gerente_host, gerente_port, middleware_port):
        self.estacao_id = estacao_id
        self.estacoes = {}  # Informações das estações
        self.gerente_host = gerente_host
        self.gerente_port = gerente_port
        self.middleware_port = middleware_port  # Porta única para cada middleware
        self.vagas_ocupadas = 0

    def adicionar_estacao(self, estacao_id, host, port, vagas, ativo):
        self.estacoes[estacao_id] = {
            'host': host,
            'port': port,
            'vagas': vagas,
            'vagas_ocupadas': 0,
            'ativo': ativo,
            'carros': []
        }
        print(f"Estação adicionada: {estacao_id}")
        self.atualizar_gerente(estacao_id)

    def ativar_estacao(self, estacao_id):
        if estacao_id in self.estacoes:
            self.estacoes[estacao_id]['ativo'] = True
            print(f"[{estacao_id}] Ativada!\n")
            self.atualizar_gerente(estacao_id)

    def redirecionar_requisicao(self, original_message):
        print("Redirecionar requisição chamada")
        # Encontra a primeira estação ativa para redirecionar a requisição
        for eid, info in self.estacoes.items():
            if info['ativo']:
                middleware_port = info['port']
                print(f"Redirecionando para estação ativa {eid} na porta {middleware_port}")
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                    try:
                        client_socket.connect(('127.0.0.1', middleware_port))
                        client_socket.sendall(original_message.encode('utf-8'))
                        response = client_socket.recv(1024).decode('utf-8')
                        print(f"Resposta da estação ativa {eid}: {response}")
                        return response
                    except ConnectionRefusedError:
                        print(f"Falha ao conectar à estação ativa {eid}")
        return "Nenhuma estação ativa disponível."

    def start_server(self):
        print(f"Iniciando servidor middleware na porta {self.middleware_port}")
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            server_socket.bind(('127.0.0.1', self.middleware_port))
        except OSError as e:
            print(f"Erro ao vincular middleware da estação {self.estacao_id} à porta {self.middleware_port}: {e}")
            return
        server_socket.listen(5)
        print(f"Middleware da estação {self.estacao_id} escutando na porta {self.middleware_port}...")

        if self.estacao_id == 'E1':
            self.ativar_estacao('E1')

        while True:
            conn, addr = server_socket.accept()
            try:
                message = conn.recv(1024).decode('utf-8')
                print(f"M[{self.estacao_id}] recebeu: {message}")

                if "ACTIVATE" in message:
                    estacao_id = message.split()[1]
                    self.ativar_estacao(estacao_id)
                    response = f"[{estacao_id}] Ativada com sucesso!"

                elif "CHECK" in message:
                    carro_id = message.split()[1]
                    # print(f"Carro[{carro_id}] em {self.estacao_id} ?\n")
                    # print(self.estacoes[self.estacao_id]['carros'])
                    if carro_id in self.estacoes[self.estacao_id]['carros']:
                        response = "FOUND"
                    else:
                        response = "NOT FOUND"
                
                elif "REMOVE" in message:
                    carro_id = message.split()[1]
                    if carro_id in self.estacoes[self.estacao_id]['carros']:
                        self.estacoes[self.estacao_id]['vagas_ocupadas'] -= 1
                        self.estacoes[self.estacao_id]['carros'].remove(carro_id)
                        print(f"Carro {carro_id} removido da estação {self.estacao_id}. Vagas ocupadas: {self.estacoes[self.estacao_id]['vagas_ocupadas']}.")
                        self.atualizar_gerente_carro('saida', carro_id)
                        response = f"Carro {carro_id} removido da estação {self.estacao_id}."
                    else:
                        response = f"Carro {carro_id} não encontrado na estação {self.estacao_id}."

                elif "REDIRECT" in message:
                    print(f"Redirecionando requisição: {message}")
                    response = self.redirecionar_requisicao(message)

                elif "ENTRADA" in message:
                    carro_id = message.split()[2]
                    self.estacoes[self.estacao_id]['vagas_ocupadas'] += 1
                    self.estacoes[self.estacao_id]['carros'].append(carro_id)
                
                    print(f"Carro {carro_id} entrou na estação {self.estacao_id}. Vagas ocupadas: {self.estacoes[self.estacao_id]['vagas_ocupadas']}.")
                    # print(self.estacoes[self.estacao_id]['carros'])
                    self.atualizar_gerente_carro('entrada', carro_id)
                    response = f"Carro {carro_id} registrado na estação {self.estacao_id}. Vagas ocupadas: {self.estacoes[self.estacao_id]['vagas_ocupadas']}."

                elif "STATUS" in message:
                    estacao_id = message.split()[1]  # Extrai o ID da estação da mensagem
                    # Verifica se a estação solicitada é ativa ou inativa
                    if estacao_id in self.estacoes and self.estacoes[estacao_id]['ativo']:
                        response = "Ativa"
                    else:
                        response = "Inativa"

                    print(f"{response}")

                elif "LIST" in message:
                    # Verifica as estações ativas e retorna a lista diretamente
                    estacoes_ativas = self.verificar_estacoes_ativas()
                    print(f"LIST Estações Ativas: [{estacoes_ativas}]\n")
                    response = f"Estações ativas: {', '.join(estacoes_ativas)}" if estacoes_ativas else "Nenhuma estação ativa"

                elif "RV" in message or "LV" in message:
                    print(f"MM: {message} ")
                    # Se a estação está ativa, realiza o processo
                    if self.estacoes[self.estacao_id]['ativo']:
                        app_port = self.estacoes[self.estacao_id]['port']
                        response = self.enviar_mensagem_app(message, app_port)
                    else:
                        # Se a estação está inativa, redireciona para uma estação ativa
                        print(f"[{self.estacao_id}] INATIVA! Redirecionando requisição de {message}\n")
                        response = self.redirecionar_requisicao(message)

                else:
                    response = f"Comando desconhecido ({message})\n"

                conn.sendall(response.encode('utf-8'))

            except Exception as e:
                print(f"Erro ao processar a mensagem: {e}")
            finally:
                conn.close()

    def enviar_mensagem_app(self, mensagem, app_port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as app_socket:
                app_socket.connect(('127.0.0.1', app_port))
                app_socket.sendall(mensagem.encode('utf-8'))
                response = app_socket.recv(1024).decode('utf-8')
                print(f"Resposta do app: {response}")
                return response
        except ConnectionRefusedError:
            print(f"Falha ao conectar ao app da estação {self.estacao_id}")
            return "Erro: Falha ao conectar ao app da estação"

    def verificar_estacoes_ativas(self):
        estacoes_ativas = []
        print(f"[{self.estacao_id}] Consultando o gerente para obter a lista de estações ativas...")

        # Conectando ao gerente para solicitar o status das estações
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            try:
                client_socket.connect((self.gerente_host, self.gerente_port))
                client_socket.sendall(f"STATUS".encode('utf-8'))  # Solicitando status das estações

                response = client_socket.recv(4096).decode('utf-8')
                estacoes_info = json.loads(response)  # Decodifica o JSON recebido

                # Filtra as estações ativas
                for estacao_id, info in estacoes_info.items():
                    if info['status'] == "ATIVA":
                        estacoes_ativas.append(estacao_id)

                print(f"Estações ativas: {estacoes_ativas}")

            except ConnectionRefusedError:
                print(f"Falha ao conectar ao gerente no endereço {self.gerente_host}:{self.gerente_port}")
            except json.JSONDecodeError:
                print(f"Erro ao decodificar a resposta do gerente: {response}")

        return estacoes_ativas
    
    def atualizar_gerente(self, estacao_id):
        estacao = self.estacoes[estacao_id]
        status = "ATIVA" if estacao['ativo'] else "INATIVA"
        carros = str(estacao['carros'])
        mensagem = f"ATUALIZAR {estacao_id} {status} {estacao['vagas']} {estacao['vagas_ocupadas']} {carros}"
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            try:
                client_socket.connect((self.gerente_host, self.gerente_port))
                client_socket.sendall(mensagem.encode('utf-8'))
                response = client_socket.recv(1024).decode('utf-8')
                print(f"Gerente resposta: {response}")
            except ConnectionRefusedError:
                print(f"Não foi possível conectar ao Gerente na {self.gerente_host}:{self.gerente_port}")

    def atualizar_gerente_carro(self, acao, carro_id):
        mensagem = f"{acao.upper()} {self.estacao_id} {carro_id} {self.estacoes[self.estacao_id]['vagas_ocupadas']}"
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            try:
                client_socket.connect((self.gerente_host, self.gerente_port))
                client_socket.sendall(mensagem.encode('utf-8'))
                response = client_socket.recv(1024).decode('utf-8')
                print(f"Gerente resposta: {response}")
            except ConnectionRefusedError:
                print(f"Não foi possível conectar ao Gerente na {self.gerente_host}:{self.gerente_port}")

# Função para inicializar middlewares em threads separadas
def inicializar_estacoes():
    gerente_host = '127.0.0.1'  # Host do gerente
    gerente_port = 5000          # Porta do gerente

    for i in range(0, 10):
        estacao_id = f'E{i}'
        middleware_port = 9000 + i  # Porta única para cada middleware
        middleware_instance = Middleware(estacao_id, gerente_host, gerente_port, middleware_port)

        # Adicionando a estação como inativa
        middleware_instance.adicionar_estacao(estacao_id, '127.0.0.1', 3000 + i, 10, False)

        # Inicia o middleware em uma thread separada
        threading.Thread(target=middleware_instance.start_server).start()

# Chama a função para iniciar os middlewares
inicializar_estacoes()
