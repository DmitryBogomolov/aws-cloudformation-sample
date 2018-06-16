FROM python:3.6.5-alpine

COPY .aws /root/.aws
COPY . /src

RUN cd /src && \
    apk --update add --no-cache make && \
    make install && \
    apk del make && \
    cp -r /src/examples /examples && rm -rf /src

WORKDIR /examples
