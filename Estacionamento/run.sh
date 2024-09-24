
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
