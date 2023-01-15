FROM python:3.11
LABEL org.opencontainers.image.source https://github.com/chramb/forum

COPY . /app

WORKDIR /app

VOLUME /app/config

EXPOSE 8000

WORKDIR /app/src

RUN pip install -r ../requirements.lock

CMD ["python", "/app/src/main.py"]
