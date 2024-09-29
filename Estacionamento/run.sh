# Função para liberar portas ocupadas
liberar_porta() {
    porta=$1
    processo=$(lsof -t -i:"$porta")
    if [ ! -z "$processo" ]; then
        echo "Liberando porta $porta (Processo: $processo)..."
        kill -9 $processo
    else
        echo "Porta $porta já está livre."
    fi
}

# Liberar portas 3000-3010 (Apps) e 9000-9010 (Middlewares)
for porta in {3000..3010} {9000..9010} 5000; do
    liberar_porta $porta
done

# Espera um pouco para garantir que as portas foram liberadas
sleep 2

echo "Abrindo gerente.py em um novo terminal..."
gnome-terminal -- bash -c "echo 'Executando gerente.py'; python3 gerente.py; exec bash"
sleep 2

echo "Abrindo middleware.py em um novo terminal..."
gnome-terminal -- bash -c "echo 'Executando middleware.py'; python3 middleware.py; exec bash"
sleep 2

echo "Abrindo app.py em um novo terminal..."
gnome-terminal -- bash -c "echo 'Executando app.py'; python3 app.py; exec bash"
sleep 2

# Executar main.exe em um novo terminal
echo "Abrindo main.exe em um novo terminal..."
gnome-terminal -- bash -c "echo 'Executando main.exe'; cd Controle && ./main; exec bash"

echo "Todos os programas foram iniciados em terminais separados."
