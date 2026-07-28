# Utilizando a imagem principal de Python 3.11, versão slim, que é um python enxuto (leve)
FROM python:3.12-slim

#Definindo o nosso diretório de trabalho do container

WORKDIR /app

# Otimizando as variáveis de ambiente para otimizar o Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONNUNBUFFERED=1

# Copiando apenas o arquivo de biblioteca de Python
COPY requirements.txt .

#Após de copia o arquivo, é feito a instalação de dependência
RUN pip install --no-cache-dir -r requirements.txt


#Após de fazer a instalação, copiando o resto do código para container
COPY . .

#Comando inicial para iniciar o bot
CMD ["python", "bot.py"]