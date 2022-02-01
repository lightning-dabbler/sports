.DEFAULT_GOAL := help

format: # sort imports, format and lint .py files
	isort --settings pyproject.toml sports/ tests/
	black --config pyproject.toml sports/ tests/
	flake8 --config .flake8 sports/ tests/

lock: # Creates poetry.lock file
	poetry cache clear --all . -n
	poetry lock --no-update -vvv

update: # Updates poetry.lock file with up-to-date dependencies
	poetry cache clear --all . -n
	poetry update -vvv

install-deps: # install python dependencies and remove dependencies not in poetry.lock from environment
	poetry install --remove-untracked -vv

init: # Install pre-commit default
	pre-commit install

help: # generate make help
	@grep -E '^[a-zA-Z_-]+:.*?#+.*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?#+"}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

validate:  # run pre-commit validation
	pre-commit run --all-files

ci-test: # runs containerized Continuous Integration (CI) Tests
	docker-compose -f docker-compose/ci-test.yaml --project-directory . up --build --abort-on-container-exit
	docker cp sports-ci-test:/sports/cover ./cover
	docker cp sports-ci-test:/sports/tests/test-report.html ./tests/test-report.html
	docker-compose -f docker-compose/ci-test.yaml --project-directory . down

ci-test-down: # stop and remove dreg CI test containers and volume
	docker-compose -f docker-compose/ci-test.yaml --project-directory . down -v

release: # Do a release of the current code.
	./bin/release.sh git-tag
	./bin/release.sh push-git-tag

build-local: # Build local development docker image
	docker-compose -f docker-compose/local.yaml --project-directory . build --force-rm

build-local-no-cache: # Build local development docker image --no-cache
	docker-compose -f docker-compose/local.yaml --project-directory . build --force-rm --no-cache

build: # Build the main docker image
	./bin/release.sh build-main-image

enter: # Enter main docker image
	./bin/release.sh enter-main-image

bump: # Bumps Version `make bump v=patch`
	bump2version --config-file bumpversion.cfg $(v) --allow-dirty
	# https://python-poetry.org/docs/cli/#version
	poetry version $(v)

up: # Spins up local containerized development environment
	docker-compose -f docker-compose/local.yaml --project-directory . up -d
	docker exec -it sports-local bash

down: # Spins down local containerized development environment
	docker-compose -f docker-compose/local.yaml --project-directory . down

test: # Update Dependencies in Environment to match and Runs Tests
	make install-deps
	python -m pytest -vv tests/

test-up: # Run test in docker container
	docker-compose --project-directory . run --rm sports-test

test-down: # stop and remove test container and volume
	docker-compose -f docker-compose/test.yaml --project-directory . down -v

docker-rmi-dangling: # Remove Dangling Docker images
	docker rmi `docker images --filter "dangling=true" -q --no-trunc`
