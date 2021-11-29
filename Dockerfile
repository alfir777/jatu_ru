FROM python:3.9

RUN apt-get update && apt-get upgrade -y && apt-get autoremove && apt-get autoclean

RUN mkdir -p /home/app/web/config

RUN addgroup --system app && adduser --system --group app

ENV HOME=/home/app
ENV APP_HOME=/home/app/web/config
WORKDIR $APP_HOME

COPY ./requirements.txt $HOME

# set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
RUN pip install -r $HOME/requirements.txt

RUN chown -R app:app $APP_HOME

USER app
