FROM python:3.7-alpine
LABEL maintainer="Alexey Miasoedov <alexey.miasoedov@gmail.com>"

# ipvsadm for troubleshooting
RUN apk add --no-cache ipvsadm
RUN pip install https://github.com/akamac/gnlpy/archive/develop.zip
ADD sync_ipvs.py /

CMD ["/usr/local/bin/python", "/sync_ipvs.py"]
