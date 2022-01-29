FROM archlinux

RUN pacman -Syu --noconfirm
RUN pacman -S python python-pip git --noconfirm
RUN git clone https://github.com/Qxe5/asca.git
RUN python -m pip install -r requirements.txt

CMD ["python", "bot.py"]
