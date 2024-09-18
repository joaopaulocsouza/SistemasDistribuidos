import threading
import socket

host = "localhost"

def iniciar_app(port):
    try:
        tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp.connect((host, int(port)))

        print("Conectado", 3010 + (port - 3000))        
        while(1):
            print(3010 + (port - 3000))
            serv.bind((host, 3010 + (port - 3000)))
            serv.listen(1)
            con, addr = serv.accept()

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