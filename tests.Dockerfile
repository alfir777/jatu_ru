FROM python:3.12.10-slim-bullseye

RUN apt-get update && apt-get upgrade -y && apt-get autoremove && apt-get autoclean

RUN mkdir -p /home/user/web/src

RUN addgroup --system --gid 2000 user && adduser --system --uid 2000 user

ENV HOME=/home/user
ENV USER_HOME=/home/user/web/src
WORKDIR $USER_HOME

COPY ./src/pyproject.toml $USER_HOME/pyproject.toml
COPY ./src/poetry.lock $USER_HOME/poetry.lock

# set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install poetry &&  poetry config virtualenvs.create false && poetry install

RUN chown -R user:user $USER_HOME
RUN chown -R user:user $HOME/.config

RUN find $USER_HOME -type d -exec chmod 755 {} \;

RUN find $USER_HOME -type f -exec chmod 644 {} \;

USER user
