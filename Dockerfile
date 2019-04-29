FROM python:3.7-alpine
LABEL maintainer="Alexey Miasoedov <alexey.miasoedov@gmail.com>"

# ipvsadm for troubleshooting
RUN apk add --no-cache ipvsadm
ADD ipvssync.py /usr/local/lib/python3.7/site-packages/
RUN pip install https://github.com/akamac/gnlpy/archive/develop.zip
ADD ipvs.json /

CMD ["python", "-m", "ipvssync"]
