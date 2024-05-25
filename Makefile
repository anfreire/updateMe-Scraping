# make a simple makefile with docker commands

# Variables
IMAGE_NAME=update-me-img
CONTAINER_NAME=update-me
SCRIPT_VOLUME=update-me-scripts
APPS_VOLUME=update-me-apps
SSH_VOLUME=update-me-ssh

create-volumes:
	docker volume create $(SCRIPT_VOLUME)
	docker volume create $(APPS_VOLUME)
	docker volume create $(SSH_VOLUME)

build:
	docker build -t $(IMAGE_NAME) .

run:
	docker run -d --name $(CONTAINER_NAME) \
		-v $(SCRIPT_VOLUME):/home/anfreire/script \
		-v $(APPS_VOLUME):/home/anfreire/apps \
		-v $(SSH_VOLUME):/root/.ssh \
		$(IMAGE_NAME)

stop:
	-docker stop $(CONTAINER_NAME)

rm:
	-docker rm $(CONTAINER_NAME)
	-docker rmi $(IMAGE_NAME)
	-docker volume rm $(SCRIPT_VOLUME)
	-docker volume rm $(APPS_VOLUME)
	-docker volume rm $(SSH_VOLUME)

purge: stop rm
	-docker system prune -a

all: create-volumes build run