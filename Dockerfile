FROM python:3-alpine

WORKDIR /asca/

RUN apk update && apk add git && \
    git clone https://github.com/Qxe5/asca . && \
    pip install --no-cache-dir -r requirements.txt

ENTRYPOINT [ "python", "./bot.py" ]
