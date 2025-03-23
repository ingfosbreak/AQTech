FROM python:3.11

WORKDIR /app
COPY . .

RUN apt-get update && apt-get upgrade -y
RUN pip install poetry

RUN poetry install --no-root

CMD ["/bin/sh", "-c", "poetry run python manage.py migrate && \
  poetry run python manage.py shell -c 'from api.management.commands.populate_db import populate_database; populate_database()' && \
  poetry run python manage.py runserver 0.0.0.0:8000"]
EXPOSE 8000