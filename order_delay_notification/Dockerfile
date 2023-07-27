FROM python:3
ENV PYTHONUNBUFFERED 1
ENV DJANGO_ENV dev
ENV DOCKER_CONTAINER 1


RUN mkdir /app
WORKDIR /app

EXPOSE 8000

COPY requirements.txt .
RUN pip install -U pip && pip install -r requirements.txt


COPY manage.py .
COPY order_delay_notification order_delay_notification
COPY vendor vendor

RUN python manage.py migrate
# RUN python manage.py runserver

