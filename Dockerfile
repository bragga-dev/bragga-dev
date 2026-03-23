# Imagem mais estável que alpine
FROM python:3.12-slim

# Variáveis Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /code

# Dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copia dependências primeiro (melhor cache)
COPY requirements.txt .

# Instala dependências
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copia projeto
COPY . .

# Copia o entrypoint
COPY entrypoint.sh /entrypoint.sh

# Dá permissão de execução
RUN chmod +x /entrypoint.sh

# Variável de ambiente
ARG DJANGO_ENV=dev
ENV DJANGO_ENV=${DJANGO_ENV}

# Cria usuário não-root
RUN adduser --disabled-password --gecos "" django

# Ajusta permissões da aplicação
RUN chown -R django:django /code

# Usa usuário não-root
USER django

# Porta do container
EXPOSE 8000

# Script de inicialização
ENTRYPOINT ["/entrypoint.sh"]

# Comando padrão (produção)
CMD ["gunicorn", "bragga.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]