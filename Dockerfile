FROM python:3.7-alpine
LABEL maintainer="Alexey Miasoedov <alexey.miasoedov@gmail.com>"

ENV PYTHONUNBUFFERED=1
# ipvsadm for troubleshooting
RUN apk add --no-cache ipvsadm
RUN pip install https://github.com/akamac/gnlpy/archive/develop.zip
ADD ipvssync.py /usr/local/lib/python3.7/site-packages/
ADD ipvs.json /config/

CMD ["python", "-m", "ipvssync"]
