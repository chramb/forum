FROM python:3.11


COPY . /app

WORKDIR /app

VOLUME /app/config
EXPOSE 8000

WORKDIR /app/src

RUN pip install -r ../requirements.lock

CMD ["python", "/app/src/main.py"]
