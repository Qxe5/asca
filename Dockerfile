FROM archlinux

COPY . .

RUN pacman -Syu --noconfirm
RUN pacman -S python python-pip git --noconfirm
RUN python -m pip install -r requirements.txt

CMD ["python", "bot.py"]
