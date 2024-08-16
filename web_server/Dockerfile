FROM python:3.10
WORKDIR /app
COPY web_server.py .

COPY templates ./templates

RUN pip install flask pika 

#flask ve pika yüklüyorum sadece ekstradan requirements.txt oluşturmuyorum

CMD ["python", "web_server.py"]
