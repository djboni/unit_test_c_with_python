PYTHON = python3
PYTHONPATH = PYTHONPATH=

PYLINT = pylint
PYLINT_OPTS = --jobs=0
PYLINT_OPTS += --disable=missing-docstring
PYLINT_OPTS += --disable=invalid-name
PYLINT_OPTS += --disable=duplicate-code
PYLINT_OPTS += --disable=fixme

MYPY = mypy
MYPYPATH = MYPYPATH=

all: examples mypy pylint

examples:
	cd unittest && make all
	cd integrtest && make all

clean:
	@echo ">>> Cleaning..."
	find .. -name __pycache__ | xargs rm -fr
	find .. -name .mypy_cache | xargs rm -fr
	cd unittest && make clean
	cd integrtest && make clean

mypy:
	@echo ">>> Versions..."
	$(PYTHON) --version
	$(MYPY) --version

	@echo ">>> Type hints check..."
	$(MYPYPATH) $(MYPY) load.py --ignore-missing-imports

pylint:
	@echo ">>> Versions..."
	$(PYTHON) --version
	$(PYLINT) --version

	@echo ">>> Linting..."
	$(PYTHONPATH) $(PYLINT) $(PYLINT_OPTS) load.py
