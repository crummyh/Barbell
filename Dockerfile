FROM node:18 as build-stage
WORKDIR /frontend
COPY frontend/ .
RUN npm install
RUN mkdir -p build
RUN npx sass scss/custom.scss build/custom.css

FROM python:3.10-slim
WORKDIR /code
COPY --from=build-stage /frontend/build/custom.css ./app/web/static/css/custom.css
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./app /code/app
EXPOSE 8000

CMD ["fastapi", "run", "app/main.py", "--port", "8000"]
