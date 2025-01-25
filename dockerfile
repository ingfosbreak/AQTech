FROM python:3.11

WORKDIR /app
COPY pyproject.toml poetry.lock  ./
COPY .env.dev .env

RUN apt-get update && apt-get upgrade -y
RUN pip install poetry

RUN poetry install --no-root

EXPOSE 8000