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
        # Ao adicionar a estação, envia as informações para o gerente.
        self.atualizar_gerente(estacao_id)

    def ativar_estacao(self, estacao_id):
        if estacao_id in self.estacoes:
            self.estacoes[estacao_id]['ativo'] = True
            print(f"Estação {estacao_id} ativada.")
            # Atualiza o gerente sobre o status da estação
            self.atualizar_gerente(estacao_id)

    def redirecionar_requisicao(self, estacao_id):
        # Encontra a primeira estação ativa para redirecionar a requisição
        for eid, info in self.estacoes.items():
            if info['ativo']:
                return f"Redirecionado para estação ativa {eid}."
        return "Nenhuma estação ativa disponível."

    def start_server(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            server_socket.bind(('127.0.0.1', self.middleware_port))
        except OSError as e:
            print(f"Erro ao vincular middleware da estação {self.estacao_id} à porta {self.middleware_port}: {e}")
            return
        server_socket.listen(5)
        print(f"Middleware da estação {self.estacao_id} escutando na porta {self.middleware_port}...")
        
        # Ativa a estação E1 automaticamente ao iniciar o middleware
        if self.estacao_id == 'E1':
            self.ativar_estacao('E1')

        while True:
            conn, addr = server_socket.accept()
            message = conn.recv(1024).decode('utf-8')
            print(f"Middleware {self.estacao_id} recebeu: {message}")

            if "ACTIVATE" in message:
                estacao_id = message.split()[1]
                self.ativar_estacao(estacao_id)
                response = f"Estação {estacao_id} ativada com sucesso."
            
            elif "REDIRECT" in message:
                estacao_id = message.split()[1]
                response = self.redirecionar_requisicao(estacao_id)

            elif "ENTRADA" in message:
                carro_id = message.split()[2]
                self.estacoes[self.estacao_id]['vagas_ocupadas'] += 1
                self.estacoes[self.estacao_id]['carros'].append(carro_id)
                print(f"Carro {carro_id} entrou na estação {self.estacao_id}. Vagas ocupadas: {self.estacoes[self.estacao_id]['vagas_ocupadas']}.")
                self.atualizar_gerente_carro('entrada', carro_id)

            elif "LIST" in message:
                # Gera a lista de estações ativas
                estacoes_ativas = [eid for eid, info in self.estacoes.items() if info['ativo']]
                response = f"Estações ativas: {', '.join(estacoes_ativas)}" if estacoes_ativas else "Nenhuma estação ativa"
            
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

            else:
                response = "Comando desconhecido."

            conn.sendall(response.encode('utf-8'))
            conn.close()

    def atualizar_gerente(self, estacao_id):
        estacao = self.estacoes[estacao_id]
        status = "ATIVA" if estacao['ativo'] else "INATIVA"
        carros = str(estacao['carros'])
        mensagem = f"ATUALIZAR {estacao_id} {status} {estacao['vagas']} {estacao['vagas_ocupadas']} {carros}"
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            try:
                client_socket.connect((self.gerente_host, self.gerente_port))
                print(f"Middleware da estação {estacao_id} conectou-se ao Gerente.")  # Mensagem informando a conexão
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
