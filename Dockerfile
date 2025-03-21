FROM python:3.11

WORKDIR /app
COPY . .

RUN apt-get update && apt-get upgrade -y
RUN pip install poetry

RUN poetry install

RUN poetry run python manage.py makemigrations api

CMD [ "poetry","run","manage.py","migrate","&&","poetry", "run", "python", "manage.py", "runserver", "0.0.0.0:8000" ] 
EXPOSE 8000