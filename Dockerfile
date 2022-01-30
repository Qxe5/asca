FROM archlinux

WORKDIR /asca/

RUN pacman -Syu python python-pip git --noconfirm && \
    git clone https://github.com/Qxe5/asca.git . && \
    python -m pip install -r requirements.txt --no-cache-dir

ENTRYPOINT python bot.py
