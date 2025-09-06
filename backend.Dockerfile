FROM python:3.11-slim

WORKDIR /code

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app
COPY setup.sh setup.sh
COPY docker-entrypoint.sh /entrypoint.sh

RUN chmod +x setup.sh
RUN ./setup.sh

ENTRYPOINT ["/entrypoint.sh"]
