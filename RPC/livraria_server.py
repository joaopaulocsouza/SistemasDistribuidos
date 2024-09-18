from concurrent import futures
import time
import random
import string
import json
import grpc
import livraria_pb2
import livraria_pb2_grpc

usuarios = []
livros = []
pedidos = []

def gerar_token(tamanho=10):
    caracteres = string.ascii_letters + string.digits  # Inclui letras maiúsculas, minúsculas e dígitos
    return ''.join(random.choice(caracteres) for _ in range(tamanho))

class LivrariaServicer(livraria_pb2_grpc.LivrariaServicer):
    def Iniciar(self, request, context):
        global livros, usuarios, pedidos
        f = open('dados.json')
        data = json.load(f)
        livros = data['livros']
        usuarios = data['usuarios']
        pedidos = data['pedidos']
        f.close()

        resposta = livraria_pb2.Resposta()
        resposta.message = "Dados carregados"
        return resposta

    def Cadastrar(self, request, context):
        global usuarios
        print("Dados usuraio:")
        print(request)
        resposta = livraria_pb2.Resposta()
        for user in usuarios:
            if user['login'] == request.login:
                resposta.message = f"Usuário já cadastrado"
                return resposta
            
        request.token = gerar_token()

        with open("dados.json", 'r') as f:
                data = json.load(f)

        obj = {}

        obj['login'] = request.login
        obj['senha'] = request.senha
        obj['token'] = request.token
        data['usuarios'].append(obj)
        f.close()

        with open('dados.json', 'w') as file:
            json.dump(data, file, indent=4)
        file.close()

        usuarios.append(obj)
        resposta.message = f"Usuário {request.login} cadastrado com sucesso"
        return resposta

    def Login(self, request, context):
        print("Dados usuraio:")
        print(request)
        resposta = livraria_pb2.Resposta()
        for user in usuarios:
            if user['login'] == request.login:
                if user['senha'] == request.senha:
                    resposta.message = f"{user['token']}"
                    return resposta
                else:
                    break
        resposta.message = f"Erro"
        return resposta
    
    def Listar(self, request, context):
        global livros
        resposta = livraria_pb2.Livro()
        if request.index < len(livros):
            resposta.titulo = livros[request.index]['titulo']
            resposta.autor = livros[request.index]['autor']
            resposta.ano = livros[request.index]['ano']
            resposta.qtd = livros[request.index]['qtd']
            resposta.valor = livros[request.index]['valor']
            return resposta
        else: 
            resposta.titulo = f"NULL"
        return resposta
    
    def Pedir(self, request, context):
        global pedidos
        resposta = livraria_pb2.Resposta()
        for livro in livros:
            if livro['titulo'] == request.titulo:
                if livro['qtd'] >= request.qtd:
                    request.id = len(pedidos)+1
                    request.total = livro['valor'] * request.qtd
                    livro['qtd'] = livro['qtd'] - request.qtd

                    with open("dados.json", 'r') as f:
                        data = json.load(f)

                    obj = {}
                    obj['id'] = request.id
                    obj['titulo'] = request.titulo
                    obj['token'] = request.token
                    obj['qtd'] = request.qtd
                    obj['total'] = request.total
                    data['pedidos'].append(obj)
                    data['livros'] = livros
                    print(obj)
                    f.close()

                    with open('dados.json', 'w') as file:
                        json.dump(data, file, indent=4)
                    file.close()

                    pedidos.append(obj)
                    resposta.message = f"Compra efetuada com sucesso"
                    return resposta
                else:
                    resposta.message = f"Não existem livros suficientes para a quantidade solicitada"
                    return resposta
        else: 
            resposta.message = f"Livro não encontrado"
            return resposta
    def Pedidos(self, request, context):
        global pedidos
        resposta = livraria_pb2.Pedido()
        if request.index < len(pedidos):
            if request.token == pedidos[request.index]['token']:
                resposta.id = pedidos[request.index]['id']
                resposta.titulo = pedidos[request.index]['titulo']
                resposta.qtd = pedidos[request.index]['qtd']
                resposta.total = pedidos[request.index]['total']
                return resposta
            else:
                resposta.titulo = f"IGNORE"
        else: 
            resposta.titulo = f"NULL"
        return resposta

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    livraria_pb2_grpc.add_LivrariaServicer_to_server(LivrariaServicer(), server)
    server.add_insecure_port("localhost:50051")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()