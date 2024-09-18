import subprocess

def run_protoc_command():
    command = [
        "python",
        "-m", "grpc_tools.protoc",
        "-I", "protos",
        "--python_out=.",
        "--grpc_python_out=.",
        "protos/livraria.proto"
    ]

    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode == 0:
        print("Comando executado com sucesso.")
    else:
        print("Erro ao executar o comando.")
        print("Saída de erro:", result.stderr)

if __name__ == "__main__":
    run_protoc_command()
