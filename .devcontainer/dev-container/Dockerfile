FROM python:3.9.9-slim


RUN apt-get update && apt-get install -y git

RUN useradd -m -r vscode

RUN pip install --upgrade pip
COPY ./requirements.txt /
RUN python -m pip install -r /requirements.txt

ENV SHELL /bin/bash