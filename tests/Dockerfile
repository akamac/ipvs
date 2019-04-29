FROM intermedia/ipvs

#RUN apk add --no-cache ipvsadm
RUN pip install pytest ipython pydevd-pycharm
ADD . /tests

CMD ["pytest", "/tests/", "-W", "ignore::DeprecationWarning"]