FROM docker:dind

#coreutils for extra date options, iproute2 for interface limit
RUN apk add --no-cache bash \
	py-pip \
	python-dev \
	libffi-dev \
	openssl-dev \
	gcc \
	libc-dev \
	git \
	musl-dev\
	nano \
	tshark \
	make \
	go \
	curl \
	tar \
	openrc \
	coreutils \
	iproute2 \
	&& apk update \
	&& pip install docker-compose

COPY content/ /

ENTRYPOINT dockerd --host=unix:///var/run/docker.sock --host=tcp://0.0.0.0:2375
CMD dockerd --host=unix:///var/run/docker.sock --host=tcp://0.0.0.0:2375
