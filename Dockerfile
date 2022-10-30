FROM python:3.10-alpine

WORKDIR /asca/

RUN apk add git --no-cache && \
    git clone https://github.com/Qxe5/asca.git . && \
    python -m pip install -r requirements.txt --no-cache-dir

ENTRYPOINT python bot.py
