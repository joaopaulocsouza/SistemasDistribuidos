import socket
import threading

class App:
    def __init__(self, host, port, middleware_port):
        self.host = host
        self.port = port
        self.connections = []

    # def handle_message(self, data, conn, addr):

    
    def handle_client(self, conn, addr):
        print((conn, addr))
        print(f"Nova conexão de {addr}")
        while True:
            try:
                data = conn.recv(1024).decode('utf-8')
                if not data:
                    break
                print(f"Mensagem recebida de {addr}: {data}")

                if data.startswith()
                
                response = f"Mensagem recebida: {data}"
                conn.sendall(response.encode('utf-8'))

            except ConnectionResetError:
                print(f"Conexão perdida com {addr}")
                break

        print(f"Conexão encerrada com {addr}")
        conn.close()
    
    def start_server(self):
        """Inicia o servidor e aceita duas conexões."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.ip, self.port))
            s.listen(2)  # O servidor irá escutar até 2 conexões
            print(f"Servidor ativo em {self.ip}:{self.port}")

            while len(self.connections) < 2:
                # Aceita uma nova conexão
                conn, addr = s.accept()
                self.connections.append((conn, addr))
                print(f"Cliente {len(self.connections)} conectado: {addr}")

                # Inicia uma thread para lidar com o cliente
                client_thread = threading.Thread(target=self.handle_client, args=(conn, addr))
                client_thread.start()

        print("Servidor terminou de aceitar conexões.")