FROM python:3.10

USER root

WORKDIR /home/anfreire

RUN mkdir -p /home/anfreire/Downloads

RUN cd /home/anfreire

COPY .ssh /root/.ssh
RUN chmod 700 /root/.ssh
RUN chmod 600 /root/.ssh/*

COPY script script

RUN pip install --trusted-host pypi.python.org -r script/requirements.txt

RUN apt-get update && apt-get install -y \
	wget \
	unzip \
	git \
	openssh-server \
	gh \
	chromium-driver && \
	apt-get clean

CMD ["python3", "script"]
