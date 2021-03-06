FROM python:3.6-alpine3.7

RUN addgroup -S dummyorders && adduser -S -g dummyorders dummyorders

WORKDIR /project

COPY requirements.txt /project/
COPY requirements-dev.txt /project/

RUN set -e && \
	apk add --no-cache --virtual .build-deps \
		alpine-sdk \
	&& \
	pip install -r requirements.txt && \
	pip install -r requirements-dev.txt && \
	apk del .build-deps

COPY setup.py /project/
COPY setup.cfg /project/
COPY README.rst /project/
COPY docker-entrypoint.sh /usr/local/bin/

COPY orders /project/orders

EXPOSE 9001

CMD ["docker-entrypoint.sh"]