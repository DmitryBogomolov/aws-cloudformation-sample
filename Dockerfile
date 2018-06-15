FROM python:3.6.5-alpine

WORKDIR /src

COPY .aws /root/.aws
COPY . .

RUN apk --update add --no-cache make && \
    make install && \
    apk del make
