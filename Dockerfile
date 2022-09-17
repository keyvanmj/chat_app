FROM python:3.10.1-slim-buster

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get -y install ffmpeg libsm6 libxext6 libgl1 libgmp-dev libmpfr-dev libmpc-dev gcc musl-dev python3-dev libffi-dev libpq-dev bash build-essential

RUN pip install --upgrade pip

COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt


COPY . /app/Chat_App
