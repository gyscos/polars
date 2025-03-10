SHELL=/bin/bash
PYTHON=venv/bin/python
PYTHON_BIN=venv/bin

.PHONY: pre-commit test pip clean

venv:
	@python -m venv venv
	@venv/bin/pip install -U pip
	@venv/bin/pip install -r build.requirements.txt
	@unset CONDA_PREFIX && source venv/bin/activate && maturin develop

clean:
	@-rm -r venv
	@cargo clean

pre-commit: venv
	$(PYTHON_BIN)/isort .
	$(PYTHON_BIN)/black .
	$(PYTHON_BIN)/blackdoc .
	$(PYTHON_BIN)/mypy
	$(PYTHON_BIN)/flake8
	make -C .. fmt_toml
	cargo fmt --all

test: venv
	$(PYTHON_BIN)/maturin develop
	$(PYTHON) -m pytest tests

test-all: venv
	$(PYTHON_BIN)/maturin develop
	$(PYTHON) -m pytest tests
	$(PYTHON) -m pytest tests_parametric
	$(PYTHON) tests/run_doc_examples.py

test-with-cov: venv
	$(PYTHON) -m pytest \
		--cov=polars \
		--cov-report xml \
		--cov-fail-under=85 \
		--import-mode=importlib

doctest:
	cd tests && ../$(PYTHON) run_doc_examples.py

install-wheel:
	pip install --force-reinstall -U wheels/polars-*.whl

build-no-venv:
	maturin build -o wheels

build-no-venv-release:
	maturin build -o wheels --release

build-and-test-no-venv:
	maturin build -o wheels
	pip install --force-reinstall -U wheels/polars-*.whl
	pytest tests

install-no-venv: build-no-venv install-wheel
install-no-venv-release: build-no-venv-release install-wheel

