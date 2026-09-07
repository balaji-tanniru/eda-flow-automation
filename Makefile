.PHONY: install test validate run clean

install:
	python3 -m pip install -r requirements-dev.txt

test:
	python3 -m pytest

validate:
	python3 -m edaflow validate configs/counter.yaml

run:
	python3 -m edaflow run configs/counter.yaml

clean:
	python3 -m edaflow clean configs/counter.yaml

