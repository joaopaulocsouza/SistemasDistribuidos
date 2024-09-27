import socket
import threading
import time

semaforo = threading.Semaphore(1)

class Middleware:
    def __init__(self, estacao_id, gerente_host, gerente_port, middleware_port):
        self.estacao_id = estacao_id
        self.estacoes = {}  # Informações das estações
        self.gerente_host = gerente_host
        self.gerente_port = gerente_port
        self.middleware_port = middleware_port  # Porta única para cada middleware
        self.vagas_ocupadas = 0        
          
        self.conexoes = []
        
        self.next_middleware = None
        self.next_ativo = False
        self.next_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.next_ping = False
        
    def send_message(self, conn, message):
        """Função para enviar mensagens de forma segura entre threads."""
        semaforo.acquire()
        try:
            conn.send(message.encode('utf-8'))
        except Exception as e:
            print(f"Erro ao enviar mensagem: {e}")
        finally:
            time.sleep(0.5)
            semaforo.release()

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
                
                self.conexoes.append(conn)
                print(f"Nova conexão de {addr} {len(self.conexoes)}")
                message = conn.recv(1024).decode('utf-8')
                print(f"Middleware {self.estacao_id} recebeu: {message}")
                
                if "PING" in message:
                    self.send_message(conn, "PONG")
                    continue
                
                if "PONG" in message:
                    self.next_ping = False
                    continue

                if "ACTIVATE" in message:
                    estacao_id = message.split()[1]
                    self.ativar_estacao(estacao_id)
                    response = f"[{estacao_id}] Ativada com sucesso!"

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
                    print(f"Redirecionando requisição: {message}")
                    response = self.redirecionar_requisicao(message)

                elif "ENTRADA" in message:
                    carro_id = message.split()[2]
                    self.estacoes[self.estacao_id]['vagas_ocupadas'] += 1
                    self.estacoes[self.estacao_id]['carros'].append(carro_id)
                    print(f"Carro {carro_id} entrou na estação {self.estacao_id}. Vagas ocupadas: {self.estacoes[self.estacao_id]['vagas_ocupadas']}.")
                    self.atualizar_gerente_carro('entrada', carro_id)

                if "STATUS" in message:
                    estacao_id = message.split()[1]  # Extrai o ID da estação da mensagem
                    # Verifica se a estação solicitada é ativa ou inativa
                    if estacao_id in self.estacoes and self.estacoes[estacao_id]['ativo']:
                        response = f"Ativa"
                    else:
                        response = f"Inativa"
                    print(f"{response}")

                elif "LIST" in message:
                    # Verifica as estações ativas e retorna a lista diretamente
                    estacoes_ativas = self.verificar_estacoes_ativas()
                    print(f"ESTA:{estacoes_ativas}\n")
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

                self.send_message(conn, response)

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

        # Supondo que temos 10 middlewares e suas portas estão de 9000 até 9009
        for i in range(10):
            estacao_id = f'E{i}'
            middleware_port = 9000 + i

           
            # Se a estação for a própria estação, verifica diretamente
            if estacao_id == self.estacao_id:
                if self.estacoes[self.estacao_id]['ativo']:
                    estacoes_ativas.append(estacao_id)
                    print(f"Verificação: [{estacao_id}] ativa (própria estação).")
            else:
                # Tenta se conectar a outras estações
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                    try:
                        client_socket.connect(('127.0.0.1', middleware_port))
                        client_socket.sendall(f"STATUS {estacao_id}".encode('utf-8'))
                        response = client_socket.recv(1024).decode('utf-8')
                        # print(f"[XX{self.estacao_id}] {response}")
                        if "Ativa" in response:  # Supondo que o middleware responde com 'ativa' ou 'inativa'
                            estacoes_ativas.append(estacao_id)
                            # print(f"Estação [{estacao_id}] está ativa. Resposta: {response}")
                        # else:
                            # print(f"Estação [{estacao_id}] está inativa. Resposta: {response}")
                    except ConnectionRefusedError:
                        print(f"Falha ao conectar ao middleware da estação {estacao_id}.")

        print()
        return estacoes_ativas



    def atualizar_gerente(self, estacao_id):
        estacao = self.estacoes[estacao_id]
        status = "ATIVA" if estacao['ativo'] else "INATIVA"
        carros = str(estacao['carros'])
        mensagem = f"ATUALIZAR {estacao_id} {status} {estacao['vagas']} {estacao['vagas_ocupadas']} {carros} {self.middleware_port}"
       # Criar uma nova conexão socket
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            conn.connect((self.gerente_host, self.gerente_port))
            self.send_message(conn, mensagem)
            # Iniciar uma thread para atualização periódica
            threading.Thread(target=self.atualizar_gerente_periodicamente, args=(estacao_id, conn,)).start()
        except Exception as e:
            print(f"Não foi possível conectar ao Gerente na {self.gerente_host}:{self.gerente_port}")
            return
        
        
    def atualizar_gerente_periodicamente(self, estacao_id, conn):
        while True:
            time.sleep(0.5)

            mensagem = "Olá"
            try:
                self.send_message(conn, mensagem)
                response = conn.recv(1024).decode('utf-8')
                if "NEXT" in response:
                    try:
                        splited = response.split()
                        if len(splited) < 2:
                            print("Não há próxima estação")
                            break
                        port = int(splited[1])
                        
                        
                        if self.next_ativo:
                            self.next_conn.close()
                            self.next_ativo = False
                            self.next_middleware.join()
                            print(f"{self.estacao_id}: Thread anterior foi finalizada.")
                        
                        print(self.next_ativo, self.next_middleware, self.next_conn)
                        self.next_ativo = True
                        self.next_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        self.next_middleware = threading.Thread(target=self.verificar_conexao_periodicamente, args=('127.0.0.1', port, conn))
                        print(self.next_ativo, self.next_middleware, self.next_conn)
                        self.next_middleware.start()
                        
                    except Exception as e:
                        print(f"{self.estacao_id} {e}")
                        pass

            except Exception as e:
                print(f"Não foi possível conectar ao Gerente na {self.gerente_host}:{self.gerente_port} - {e}")
                conn.close()  # Fechar o socket em caso de erro

            time.sleep(0.5)  # Aguardar antes de enviar a próxima mensagem


    def verificar_conexao_periodicamente(self, host, port, conn):      
        """
        Verifica periodicamente a conexão com outro middleware.
        """
        print(f"Conectando ao middleware {host}:{port}...")
        mensagem = f"PING {self.estacao_id}"

        try:
            self.next_conn.connect((host, port))
            
            while True:
                self.next_conn.send(mensagem.encode('utf-8'))
                self.next_ping = True
                time.sleep(3)
                if not self.next_ping:
                    print(f"Conexão com o middleware {host}:{port} perdida.")
                    self.next_ping = False
                    break
                else: 
                    self.send_message(self.next_conn, "ELEICAO")
                    self.next_ping = False
                    print(f"Conexão com o middleware {host}:{port} OK.")
                

            # Iniciar a thread de atualização periódica para o novo middleware
        except Exception as e:
            print(f"Não foi possível conectar ao middleware na {host}:{port} - {e}")
            conn.close()  # Fechar o socket em caso de erro
            return

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
