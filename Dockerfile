FROM python:3.8.3-slim-buster as poetry

ADD https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py .
RUN POETRY_PREVIEW=1 python get-poetry.py --version 1.0.0

WORKDIR /app
ADD . /app
RUN ~/.poetry/bin/poetry install -n

EXPOSE 3000

CMD  PYTHONPATH=. ~/.poetry/bin/poetry run python _root/main.py --config=polls.yaml run
