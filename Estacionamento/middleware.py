import socket
import threading
import json
import time

class Middleware:
    def __init__(self, estacao_id, gerente_host, gerente_port, middleware_port):
        self.estacao_id = estacao_id
        self.estacoes = {}  # Informações das estações
        self.gerente_host = gerente_host
        self.gerente_port = gerente_port
        self.middleware_port = middleware_port  # Porta única para cada middleware
        self.vagas_ocupadas = 0
        
        # Configurções anel de middleware
        self.port = middleware_port+1000
        self.next_port = None
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.next_conn = None
        self.ativo = False
        self.proxima_ativa = False

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
        
    def send_message(self, conn, message):
        try:
            conn.send(f'{message}'.encode('utf-8'))
        except Exception as e:
            print(f"Erro ao enviar mensagem: {e}")

    def ativar_estacao(self, estacao_id):
        if estacao_id in self.estacoes:
            self.estacoes[estacao_id]['ativo'] = True
            print(f"[{estacao_id}] Ativada!\n")
            self.atualizar_gerente(estacao_id)
            # Thread para receber mensagens da estação anterior
            self.server_thread = threading.Thread(target=self.server_next)
            self.server_thread.start()
            
    
    def desativar_estacao(self, estacao_id):
        if estacao_id in self.estacoes:
            self.estacoes[estacao_id]['ativo'] = False
            print(f"[{estacao_id}] Desativada!\n")
            self.atualizar_gerente(estacao_id)
            self.stop_server_next()
            print(f"{self.estacao_id}: Desativando servidor...")

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
                    response = f"[{estacao_id}] (ATIVADA)"
                
                elif "INATIVATE" in message:
                    estacao_id = message.split()[1]
                    self.desativar_estacao(estacao_id)
                    response = f"[{estacao_id}] (INATIVADA)"
                
                elif "CHECK" in message:
                    carro_id = message.split()[1]
                    # print(f"Carro[{carro_id}] em {self.estacao_id} ?\n")
                    # print(self.estacoes[self.estacao_id]['carros'])
                    if carro_id in self.estacoes[self.estacao_id]['carros']:
                        response = "FOUND"
                    else:
                        response = "NOT FOUND"
                
                elif "REDIRECT" in message:
                    print(f"Redirecionando requisição: {message}")
                    response = self.redirecionar_requisicao(message)

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
                
                elif "VD" in message:
                    response = self.obter_vagas_disponiveis()
                    
                elif "RV" in message or "LV" in message:
                    print(f"MM: {message} ")
                    # Se a estação está ativa, realiza o processo
                    if self.estacoes[self.estacao_id]['ativo']:
                        app_port = self.estacoes[self.estacao_id]['port']
                        response = self.enviar_mensagem_app(message, app_port)
                    else:
                        # Se a estação está inativa, redireciona para uma estação ativa
                        print(f"[{self.estacao_id}] (INATIVA) Redirecionando requisição de {message}\n")
                        response = self.redirecionar_requisicao(message)

                else:
                    print(f"Comando desconhecido ({message})")
                    response = f"Comando desconhecido ({message})\n"

                conn.sendall(response.encode('utf-8'))

            except Exception as e:
                print(f"Erro ao processar a mensagem {message} : {e}")
            finally:
                conn.close()
                

    def obter_vagas_disponiveis(self):
        # Conectando ao gerente para solicitar todas as informações das estações
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                # Conectar ao gerente
                client_socket.connect((self.gerente_host, self.gerente_port))
                
                # Solicita todas as informações das estações ativas ao gerente
                self.send_message(client_socket, "INFO")
                
                # Recebe a resposta do gerente
                data = []
                while True:
                    packet = client_socket.recv(4096).decode('utf-8')
                    if not packet:  # Se não há mais dados para receber, termina o loop
                        break
                    data.append(packet)
                    
                response = ''.join(data)  # Junta todos os pacotes recebidos
                estacoes_info = json.loads(response)  # Converte o JSON para um dicionário

                lista_vagas = []
                for estacao_id, info in estacoes_info.items():
                    if info['status'] == 'ATIVA':
                        total_vagas = info['vagas']
                        vagas_ocupadas = info['vagas_ocupadas']
                        vagas_livres = total_vagas - vagas_ocupadas
                        lista_vagas.append(f"{estacao_id}:{vagas_livres}-{vagas_ocupadas}")
                
                # Retorna a mensagem com o código "AV" e a lista de vagas
                return f"AV {' '.join(lista_vagas)}"
        
        except ConnectionRefusedError:
            return "Erro: Não foi possível conectar ao Gerente."
        except Exception as e:
            return f"Erro: {e}"

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
        print(f"M[{self.estacao_id}] Consultando o gerente para obter a lista de estações ativas...")

        # Conectando ao gerente para solicitar o status das estações
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            try:
                client_socket.connect((self.gerente_host, self.gerente_port))
                self.send_message(client_socket, "STATUS")  # Solicitando status das estações

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
        
        # Transformar a lista de carros em formato JSON válido
        carros = json.dumps(estacao['carros'])
        
        # Montar a mensagem com o campo carros em JSON
        mensagem = f"ATUALIZAR {estacao_id} {status} {estacao['vagas']} {estacao['vagas_ocupadas']} {carros} {self.port}"
        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            try:
                client_socket.connect((self.gerente_host, self.gerente_port))
                self.send_message(client_socket, mensagem)
                response = client_socket.recv(1024).decode('utf-8')
                print(f"Gerente resposta: {response}")
                
                if response.startswith("UPDATE_NEXT"):
                    # Atualiza a próxima estação no anel
                    _, nome_proxima, ip_proxima, porta_proxima = response.split("#")
                    self.ip_proximo = ip_proxima
                    self.porta_proximo = int(porta_proxima)
                    print(f"{self.nome}: Atualizando próxima estação para {nome_proxima} ({ip_proxima}:{porta_proxima})")
                    self.connect_next_station() 
            except ConnectionRefusedError:
                print(f"Não foi possível conectar ao Gerente na {self.gerente_host}:{self.gerente_port}")

    def atualizar_gerente_carro(self, acao, carro_id):
        mensagem = f"{acao.upper()} {self.estacao_id} {carro_id} {self.estacoes[self.estacao_id]['vagas_ocupadas']}"
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            try:
                client_socket.connect((self.gerente_host, self.gerente_port))
                self.send_message(client_socket, mensagem)
                response = client_socket.recv(1024).decode('utf-8')
                print(f"Gerente resposta: {response}")
            except ConnectionRefusedError:
                print(f"Não foi possível conectar ao Gerente na {self.gerente_host}:{self.gerente_port}")

    def verificar_conexao_proxima_estacao(self):
        """Verifica periodicamente se a próxima estação no anel está ativa."""
        while self.ativo:
            if self.sock_client:
                try:
                    # Envia uma mensagem PING para verificar se a próxima estação está ativa
                    self.sock_client.sendall("PING".encode())
                    # Espera por uma resposta
                    self.sock_client.settimeout(5)
                    data = self.sock_client.recv(1024)
                    if data.decode() != "PONG":
                        raise Exception("PONG não recebido")
                    print(f"{self.nome}: Próxima estação respondeu ao PING.")
                    self.proxima_ativa = True
                except (socket.timeout, Exception):
                    # Se o PING falhar, iniciamos uma eleição
                    print(f"{self.nome}: Falha na conexão com a próxima estação, iniciando eleição...")
                    self.proxima_ativa = False
                    self.iniciar_eleicao()
            time.sleep(10)  # Verifica a cada 10 segundos
            
    # Função para iniciar o servidor para receber conexões da estação anterior

    def server_next(self):
        """Inicia o servidor para receber conexões da estação anterior no anel."""
        try:
            if not self.ativo:
                self.ativo = True
                self.server.bind(('127.0.0.1', self.port))
                self.server.listen(5)
                print(f"{self.estacao_id}: Servidor iniciado, esperando conexões...")

                while self.ativo:
                    conn, addr = self.server.accept()
                    print(f"{self.estacao_id}: Conexão recebida de {addr}")
                    # Cria uma thread para tratar essa conexão
                    threading.Thread(target=self.handle_connection, args=(conn,)).start()
        except Exception as e:
            print(f"Erro ao iniciar o servidor: {e}")
            
    def stop_server_next(self):
        """Desfaz a conexão e retorna ao estado inicial."""
        print(f"{self.estacao_id}: Parando servidor...")
        self.ativo = False  # Define a estação como inativa

        # Fechar o servidor
        try:
            self.server.close()
            print(f"{self.estacao_id}: Servidor fechado.")
        except Exception as e:
            print(f"{self.estacao_id}: Erro ao fechar o servidor: {e}")

        # Reiniciar variáveis de estado
        self.next_conn = None
        self.proxima_ativa = False
            
    def connect_next_station(self):
        while self.next_conn is None and self.ativo:
            try:
                self.next_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.next_conn.connect(('127.0.0.1', self.next_port))
                print(f"{self.estacao_id}: Conectado à estação anterior.")
            except ConnectionRefusedError:
                print(f"{self.estacao_id}: Falha ao conectar à estação anterior. Tentando novamente...")
                self.next_conn = None
                time.sleep(1)
                
    def handle_connection(self, conn):
        """Manipula as mensagens recebidas da estação anterior."""
        while self.ativo:
            try:
                data = conn.recv(1024)
                if not data:
                    break
                mensagem = data.decode()
                print(f"{self.estacao_id}: Mensagem recebida: {mensagem}")
                
                if mensagem.startswith("PING"):
                    # Responde ao ping para manter a verificação de conexão
                    self.send_message(conn, "PONG")
                elif mensagem.startswith("ELEICAO"):
                    # Participa da eleição
                    self.participar_eleicao(mensagem)
                else:
                    # Encaminha a mensagem ou processa conforme o protocolo
                    self.send_message(conn, mensagem)
            except Exception as e:
                print(f"Erro na conexão com a estação anterior: {e}")
                break

    def iniciar_eleicao(self):
        """Inicia uma eleição para redistribuir as vagas da estação com falha."""
        mensagem_eleicao = f"ELEICAO {self.estacao_id} {self.port}"
        self.send_message(self.next_conn, mensagem_eleicao)

 
    def participar_eleicao(self, mensagem):
        """Participa de uma eleição, comparando o ID recebido com o próprio."""
        _, id_recebido, porta_recebida = mensagem.split()
        id_recebido = int(id_recebido)
        porta_recebida = int(porta_recebida)

        if id_recebido > self.id_estacao:
            # O ID recebido é maior, continua a eleição repassando o maior ID
            print(f"{self.estacao_id}: Recebido ID maior ({id_recebido}). Repassando...")
            self.enviar_mensagem_proximo(mensagem)
        elif id_recebido < self.id_estacao:
            # O ID da estação atual é maior, envia seu próprio ID e porta
            print(f"{self.estacao_id}: é maior. Enviando meu ID e porta na eleição.")
            self.enviar_mensagem_proximo(f"ELEICAO {self.id_estacao} {self.port}")
        else:
            # O ID retornou à estação inicial, eleição concluída
            print(f"{self.estacao_id}: líder com e porta {self.port}.")
            self.anunciar_eleito(self.id_estacao, self.port)
            
    def anunciar_eleito(self, id_eleito, porta_eleito):
        """Informa a todas as estações que o líder foi escolhido, enviando seu ID e porta."""
        mensagem = f"ELEITO {id_eleito} {porta_eleito}"
        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            try:
                client_socket.connect((self.gerente_host, self.gerente_port))
                self.send_message(client_socket, mensagem)
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