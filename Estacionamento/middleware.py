import socket
import threading

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
        print(f"Estação adicionada: {estacao_id}")  # Log de verificação
        # Ao adicionar a estação, envia as informações para o gerente.
        self.atualizar_gerente(estacao_id)

    def ativar_estacao(self, estacao_id):
        if estacao_id in self.estacoes:
            self.estacoes[estacao_id]['ativo'] = True
            print(f"Estação {estacao_id} ativada.")  # Log de ativação
            # Atualiza o gerente sobre o status da estação
            self.atualizar_gerente(estacao_id)

    def redirecionar_requisicao(self, original_message):
        print("Redirecionar requisição chamada")  # Log inicial
        # Encontra a primeira estação ativa para redirecionar a requisição
        for eid, info in self.estacoes.items():
            if info['ativo']:
                middleware_port = info['port']
                print(f"Redirecionando para estação ativa {eid} na porta {middleware_port}")  # Log de redirecionamento
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                    try:
                        client_socket.connect(('127.0.0.1', middleware_port))
                        client_socket.sendall(original_message.encode('utf-8'))
                        response = client_socket.recv(1024).decode('utf-8')
                        print(f"Resposta da estação ativa {eid}: {response}")  # Log de resposta
                        return response
                    except ConnectionRefusedError:
                        print(f"Falha ao conectar à estação ativa {eid}")
        return "Nenhuma estação ativa disponível."

    def start_server(self):
        print(f"Iniciando servidor middleware na porta {self.middleware_port}")  # Log de início
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            server_socket.bind(('127.0.0.1', self.middleware_port))
        except OSError as e:
            print(f"Erro ao vincular middleware da estação {self.estacao_id} à porta {self.middleware_port}: {e}")
            return
        server_socket.listen(5)
        print(f"Middleware da estação {self.estacao_id} escutando na porta {self.middleware_port}...")

        if self.estacao_id == 'E1':  # Ativação automática para teste
            self.ativar_estacao('E1')

        while True:
            conn, addr = server_socket.accept()
            try:
                message = conn.recv(1024).decode('utf-8')
                print(f"M[{self.estacao_id}] recebeu: {message}")  # Log de recebimento

                if "ACTIVATE" in message:
                    estacao_id = message.split()[1]
                    self.ativar_estacao(estacao_id)
                    response = f"Estação {estacao_id} ativada com sucesso."

                elif "CHECK" in message:
                    carro_id = message.split()[1]
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
                    print(f"Redirecionando requisição: {message}")  # Log para debug de redirecionamento
                    response = self.redirecionar_requisicao(message)

                elif "ENTRADA" in message:
                    carro_id = message.split()[2]
                    self.estacoes[self.estacao_id]['vagas_ocupadas'] += 1
                    self.estacoes[self.estacao_id]['carros'].append(carro_id)
                    print(f"Carro {carro_id} entrou na estação {self.estacao_id}. Vagas ocupadas: {self.estacoes[self.estacao_id]['vagas_ocupadas']}.")
                    self.atualizar_gerente_carro('entrada', carro_id)

                elif "LIST" in message:
                    self.verificar_estacoes_ativas()
                    estacoes_ativas = [eid for eid, info in self.estacoes.items() if info['ativo']]
                    response = f"Estações ativas: {', '.join(estacoes_ativas)}" if estacoes_ativas else "Nenhuma estação ativa"

                elif "RV" in message or "LV" in message:
                    # Envia a mensagem para o app correspondente
                    app_port = self.estacoes[self.estacao_id]['port']
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as app_socket:
                        try:
                            app_socket.connect(('127.0.0.1', app_port))
                            app_socket.sendall(message.encode('utf-8'))
                            response = app_socket.recv(1024).decode('utf-8')
                            print(f"Resposta do app: {response}")
                        except ConnectionRefusedError:
                            print(f"Falha ao conectar ao app da estação {self.estacao_id}")

                else:
                    response = f"Comando desconhecido ({message})\n"

                conn.sendall(response.encode('utf-8'))

            except Exception as e:
                print(f"Erro ao processar a mensagem: {e}")
            finally:
                conn.close()

    def verificar_estacoes_ativas(self):
        for estacao_id, info in self.estacoes.items():
            if not info['ativo']:
                print(f"Verificação: Estação {estacao_id} está inativa.")
            else:
                print(f"Verificação: Estação {estacao_id} está ativa.")

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
        middleware_instance.adicionar_estacao(estacao_id, '127.0.0.1', 3000 + i, 10, False)
        threading.Thread(target=middleware_instance.start_server).start()

# Chama a função para iniciar os middlewares
inicializar_estacoes()
