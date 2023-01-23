FROM python:3.10-alpine3.14

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
WORKDIR /social_network
COPY requirements.txt /social_network/requirements.txt
RUN pip install --upgrade pip && apk add --no-cache --virtual .build-deps g++ gcc make \
    libc-dev libffi-dev libevent-dev musl-dev openssl-dev \
    && pip3 install --no-cache-dir --upgrade -r requirements.txt \
    && apk del .build-deps g++ gcc make libc-dev libffi-dev libevent-dev musl-dev openssl-dev
COPY ./ /social_network
EXPOSE 8080
