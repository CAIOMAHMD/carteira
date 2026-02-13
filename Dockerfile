FROM python:3.11-slim

# Evita buffering no log
ENV PYTHONUNBUFFERED=1

ENV BRAPI_API_KEY=mw5kpFNazrDmGsqzug4Sdv
ENV PYTHONPATH="/app"


# Cria diretório da aplicação
WORKDIR /app

# Copia requirements
COPY requirements.txt .

# Instala dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o projeto
COPY . .

# Expõe a porta do Flask
EXPOSE 5000

# Comando para rodar a aplicação
CMD ["python", "web/app.py"]
