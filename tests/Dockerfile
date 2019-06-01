FROM intermedia/ipvs

# gcc required for pylint, namely typed-ast
RUN apk add --no-cache gcc musl-dev
RUN pip install pytest \
                pytest-cov \
                pylint \
                ipython \
                pydevd-pycharm
ADD . tests/
WORKDIR tests

CMD ["pytest", "--cov", "ipvssync", "-W", "ignore::DeprecationWarning", "-v"]