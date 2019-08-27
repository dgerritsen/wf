FROM python:3.7-alpine
ENV PYTHONUNBUFFERED 1
ENV C_FORCE_ROOT true

RUN mkdir /src
WORKDIR /src

# install psycopg2
RUN apk update \
    && apk add --virtual build-deps gcc libffi-dev python3-dev musl-dev \
    && apk add postgresql-dev git \
    && pip install psycopg2 \
    && apk del build-deps

ADD . /src
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
#CMD python manage.py collectstatic --no-input;python manage.py migrate;gunicorn morgan2.wsgi -b 0.0.0.0:8000 & celery -A morgan2.celery worker