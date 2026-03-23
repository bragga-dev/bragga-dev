#!/bin/sh

echo "========================================="
echo "Iniciando entrypoint.sh - Ambiente: $DJANGO_ENV"
echo "========================================="

# Função simples para verificar conexão
wait_for_host() {
    host=$1
    port=$2
    echo "Aguardando $host:$port..."
    
    # Usando timeout do bash com redirecionamento
    timeout 1 bash -c "echo > /dev/tcp/$host/$port" 2>/dev/null
    
    while [ $? -ne 0 ]; do
        sleep 1
        echo "Ainda aguardando $host:$port..."
        timeout 1 bash -c "echo > /dev/tcp/$host/$port" 2>/dev/null
    done
    
    echo "$host:$port disponível!"
}

# Aguardar banco de dados
wait_for_host $DB_HOST $DB_PORT

# Executar migrações
echo "Executando migrações..."
python manage.py migrate --noinput

# Criar superusuário (opcional)
if [ "$CREATE_SUPERUSER" = "true" ]; then
    echo "Criando superusuário..."
    python manage.py createsuperuser --noinput --username admin --email admin@example.com 2>/dev/null || true
fi

echo "========================================="
echo "Inicialização concluída!"
echo "========================================="

# Executar o comando (runserver)
exec "$@"