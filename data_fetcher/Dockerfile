FROM python:3.10

WORKDIR /app

COPY . /app

RUN pip install -r requirements-fetcher.txt


CMD ["python3", "fetch_data.py"]
