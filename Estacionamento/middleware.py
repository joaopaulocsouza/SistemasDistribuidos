import socket
import threading

class Middleware:
    def __init__(self, estacao_id, gerente_host, gerente_port, middleware_port):
        self.estacao_id = estacao_id
        self.estacoes = {}  # Informações das estações
        self.gerente_host = gerente_host
        self.gerente_port = gerente_port
        self.middleware_port = middleware_port  # Porta única para cada middleware

    def adicionar_estacao(self, estacao_id, host, port, vagas, ativo):
        self.estacoes[estacao_id] = {
            'host': host,
            'port': port,
            'vagas': vagas,
            'vagas_ocupadas': 0,
            'ativo': ativo,
            'carros': []
        }
        self.atualizar_gerente(estacao_id)

    def ativar_estacao(self, estacao_id):
        if estacao_id in self.estacoes:
            self.estacoes[estacao_id]['ativo'] = True
            print(f"Estação {estacao_id} ativada.")
            self.atualizar_gerente(estacao_id)

    def redirecionar_requisicao(self, estacao_id):
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
        
        # Ativa a estação 1 automaticamente
        self.ativar_estacao('E1')

        while True:
            conn, addr = server_socket.accept()
            message = conn.recv(1024).decode('utf-8')
            print(f"Middleware recebeu: {message}")

            if "ACTIVATE" in message:
                estacao_id = message.split()[1]
                self.ativar_estacao(estacao_id)
                response = f"Estação {estacao_id} ativada com sucesso."
            elif "REDIRECT" in message:
                estacao_id = message.split()[1]
                response = self.redirecionar_requisicao(estacao_id)
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
            client_socket.connect((self.gerente_host, self.gerente_port))
            print(f"Middleware da estação {estacao_id} conectou-se ao Gerente.")  # Mensagem informando a conexão
            client_socket.sendall(mensagem.encode('utf-8'))
            response = client_socket.recv(1024).decode('utf-8')
            print(f"Gerente resposta: {response}")
            
# Adicionando 10 estações inativas
for i in range(0, 10):
    middleware_instance = Middleware(f'E{i}', '127.0.0.1', 5000, 9000 + i)  # Usando porta única para cada middleware
    middleware_instance.adicionar_estacao(f'E{i}', '127.0.0.1', 3000 + i, 10, False)
    threading.Thread(target=middleware_instance.start_server).start()