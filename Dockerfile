FROM python:3.9

WORKDIR /app

COPY src/main.py /app
COPY requirements.txt /app
COPY .env /app

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]