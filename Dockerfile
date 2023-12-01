FROM python:3.11-alpine

WORKDIR /asca/

ARG tmp='gcc musl-dev git'

RUN apk add $tmp --no-cache && \
    git clone https://github.com/Qxe5/asca.git . && \
    python -m pip install -r requirements.txt --no-cache-dir && \
    apk del $tmp

ENTRYPOINT python bot.py
