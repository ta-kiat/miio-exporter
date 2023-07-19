FROM python:3.9.9-slim

WORKDIR /app

RUN useradd -m -r containeruser

RUN apt-get update \
    && apt-get install git -y\
    && apt-get install gcc -y \
    && apt-get clean

COPY ./requirements.txt /app/requirements.txt

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && rm requirements.txt

COPY ./scripts scripts
COPY ./app app

EXPOSE 80

USER containeruser

CMD ["sh", "scripts/start.sh"]
