import threading
import socket

host = "localhost"
tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def iniciar_app(port):
    try:
        tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp.bind((host, port))
        tcp.listen(1)
        con, addr = tcp.accept()
        print("Conexão aceita")
        con.close()

        while(1):
            pass

    except Exception as e:
        print(e) 
        return


threads = []

for i in range(0,10):
    thread = threading.Thread(target=iniciar_app, args=(3000+i, ) )
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()