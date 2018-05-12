APP_NAME = orders
PROJECT_NAME = dummysensi

PROJECT_ROOT_DIR = $(PWD)

DATA_VOLUME_NAME = rabbitmqvolume
DEV_NETWORK = dummysensi-net

# Change thiese values accroding to the make build-tag-push requirement
BRANCH = master
COMMIT = 1111ab

DEPLOY_ENVIRONMENT = production
CI_SERVER = travis
DOCKER = docker 
DOCKER_COMPOSE = docker-compose





.PHONY: travis-setup jenkins-setup

travis-setup:
	bash -c "scripts/travis-setup.sh $(PROJECT_ROOT_DIR)"

jenkins-setup:
	bash -c "scripts/jenkins-setup.sh $(PROJECT_ROOT_DIR)"


.PHONY: clean-pyc clean-build

clean-pyc:
	find . -name '*.pyc' -exec rm --force {} +
	find . -name '*.pyo' -exec rm --force {} +
	find . -name '*~' -exec rm --force  {} +

clean-build:
	rm --force --recursive build/
	rm --force --recursive dist/
	rm --force --recursive *.egg-info


.PHONY: build-network-dev

build-network-dev:
	$(DOCKER) network create -d bridge --attachable $(DEV_NETWORK)


.PHONY: build-volume-dev build-volume-prod remove-volume-prod

build-volume-dev:
	$(DOCKER) volume create $(DATA_VOLUME_NAME)

build-volume-prod:
	$(DOCKER) volume create --driver=rexray --opt=size=4 --opt=volumeType=gp2 $(DATA_VOLUME_NAME)

remove-volume-prod:
	$(DOCKER) volume rm $(DATA_VOLUME_NAME)



.PHONY: build build-dev build-prod

build: build-dev

build-dev:
	bash -c "$(DOCKER_COMPOSE) -p $(PROJECT_NAME) build"

build-prod: build-volume-prod



.PHONY: start start-dev start-prod

start: start-dev

start-dev:
	bash -c "$(DOCKER_COMPOSE) -p $(PROJECT_NAME) up -d"

start-prod:
	bash -c "$(DOCKER) stack deploy --compose-file docker-compose.prod.yml $(PROJECT_NAME)"


.PHONY: stop stop-dev stop-prod stop-all

stop: stop-dev

stop-dev:
	$(DOCKER_COMPOSE) -p $(PROJECT_NAME) stop

stop-prod:
	$(DOCKER) stack rm $(PROJECT_NAME)

stop-all: stop-dev stop-prod



.PHONY: remove remove-dev remove-prod remove-all 

remove: remove-dev

remove-dev:
	$(DOCKER_COMPOSE) -p $(PROJECT_NAME) rm --force -v

remove-prod: stop-prod

remove-all: remove-dev remove-prod


.PHONY: system-prune clean clean-dev clean-prod clean-all

system-prune:
	echo "y" | $(DOCKER) system prune

clean: clean-dev

clean-dev: remove-dev system-prune 

clean-prod: remove-prod system-prune

clean-all: clean-dev clean-prod


.PHONY: build-tag-push deploy

build-tag-push:
	bash -c "build_tag_push.sh $(APP_NAME) $(BRANCH) $(COMMIT)"

deploy-virtualenv:
	bash -c "deploy.sh"


.PHONY: check-logs check-logs-dev check-logs-dev-app check-logs-app check-logs-prod check-logs-prod-app

check-logs: check-logs-dev

check-logs-app: check-logs-dev-app

check-logs-dev-app:
	$(DOCKER_COMPOSE) -p $(PROJECT_NAME) logs --follow --tail=10 $(APP_NAME)

check-logs-dev:
	$(DOCKER_COMPOSE) -p $(PROJECT_NAME) logs --follow --tail=10

check-logs-prod-app:
	$(DOCKER_COMPOSE) -p $(PROJECT_NAME) -f docker-compose.prod.yml logs --follow --tail=10 $(APP_NAME)

check-logs-prod:
	$(DOCKER_COMPOSE) -p $(PROJECT_NAME) -f docker-compose.prod.yml logs --follow --tail=10
