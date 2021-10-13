FROM python:3.10-alpine
WORKDIR /opt
COPY requirements.txt /opt
RUN pip install -r requirements.txt
COPY radioNowPlaying.py /opt
ENTRYPOINT /opt/radioNowPlaying.py
