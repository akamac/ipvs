FROM python:3.7-alpine
LABEL maintainer="Alexey Miasoedov <alexey.miasoedov@gmail.com>"

RUN pip install six git+https://github.com/akamac/gnlpy.git@develop
ADD sync_ipvs.py /

CMD ["/usr/local/bin/python", "/sync_ipvs.py"]
