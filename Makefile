# Some simple testing tasks (sorry, UNIX only).

FLAGS=


checkrst:
	python3 setup.py check --restructuredtext

flake: checkrst
	flake8 aioodbc tests examples setup.py

test: flake
	docker compose build
	docker compose run aioodbc pytest --cov

doc:
	docker compose run aioodbc make -C docs html
	@echo "open file://`pwd`/docs/_build/html/index.html"

.PHONY: all flake test clean doc
