import livraria_pb2
import livraria_pb2_grpc
import time
import grpc
import json


def run():
    token = 'NULL'
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = livraria_pb2_grpc.LivrariaStub(channel)

        void = livraria_pb2.Index(index = 1)
        res = stub.Iniciar(void)

        while(1):
            print("1. Cadastrar")
            print("2. Entrar")
            rpc_call = input("Selecionar opção: ")

            if rpc_call == "1":
                login = input("Insira o nome de usuário: ")
                senha = input("Insira a senha: ")
                if len(senha) == 0 or len(login) == 0:
                    print("Dados inválidos")
                else:
                    cadastro = livraria_pb2.Usuario(login = login, senha = senha)
                    res = stub.Cadastrar(cadastro)
                    print(res)
            if rpc_call == "2":
                login = input("Insira o nome de usuário: ")
                senha = input("Insira a senha: ")
                if len(senha) == 0 or len(login) == 0:
                    print("Dados inválidos")
                else:
                    dados = livraria_pb2.Usuario(login = login, senha = senha)
                    res = stub.Login(dados)
                    if "Erro" not in res.message:
                        token = res.message
                        print('Login concluído com sucesso')
                    else:
                        print("Erro no login")
            
            while(token != 'NULL'):
                print("1. Listar")
                print("2. Efetuar pedido")
                print("3. Pedidos")
                print("0. Sair")
                rpc_call = input("Selecionar opção: ")

                if rpc_call == "0":
                    token = 'NULL'
                elif rpc_call == "1":
                    i = 0
                    while(1):
                        index = livraria_pb2.Index(index = i)
                        res = stub.Listar(index)
                        if res.titulo == 'NULL':
                            break
                        else:
                            print(res)
                            i = i+1
                elif rpc_call == "2":
                    titulo = input("Insira o titulo do livro: ")
                    qtd = input("Insira a quantidade: ")
                    if len(titulo) == 0 or int(qtd) <= 0:
                        print("dados inválidos")
                    else:
                        pedido = livraria_pb2.Pedido(titulo = titulo, qtd = int(qtd), token = token)
                        res = stub.Pedir(pedido)
                        print(res.message)
                elif rpc_call == "3":
                    i = 0
                    while(1):
                        dados = livraria_pb2.PedidoUsuario(index = i, token = token)
                        res = stub.Pedidos(dados)
                        if res.titulo == 'NULL':
                            break
                        else:
                            print(res)
                            i = i+1


if __name__ == "__main__":
    run()