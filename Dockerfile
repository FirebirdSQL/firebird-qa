FROM ubuntu:22.04

RUN \
	apt-get update && \
	\
	DEBIAN_FRONTEND=noninteractive apt-get -y install \
		libicu70 \
		libncurses5 \
		libtommath1 \
		python3 \
		python3-pip \
		sudo && \
	\
	rm -rf /var/lib/apt/lists/* && \
	\
	ln -s /usr/lib/x86_64-linux-gnu/libtommath.so.1 /usr/lib/x86_64-linux-gnu/libtommath.so.0

ARG UID=1000

COPY setup.cfg pyproject.toml /qa-run/

RUN \
	useradd -u $UID user -G sudo && \
	groupadd firebird && \
	useradd --non-unique -M -b /opt -s /sbin/nologin -g firebird -u $UID firebird && \
	usermod -G sudo firebird && \
	echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers && \
	\
	mkdir /qa-out && \
	chown -R user:user /qa-out && \
	chown -R firebird:firebird /qa-run && \
	cd /qa-run && \
	pip install -e . && \
	pip install pytest-md-report pytest-timeout

USER user

ENV PATH=/opt/firebird/bin:$PATH
ENV TERMINFO_DIRS=/lib/terminfo
ENV LD_LIBRARY_PATH=/opt/firebird/lib

CMD /qa/docker/run.sh
