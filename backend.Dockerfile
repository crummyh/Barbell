FROM python:3.11-slim

WORKDIR /code

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app

CMD ["sh", "-c", "if [ \"$DEBUG\" = \"true\" ]; then uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload; else uvicorn app.main:app --host 0.0.0.0 --port 8000; fi"]
