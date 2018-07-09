BUILDDIR='~build'


.mkbuilddir:
	mkdir -p ${BUILDDIR}

develop:
	@pip install -U pip setuptools pip-tools
	@pip install -e .[dev]


requirements:
	pipenv lock -r > src/requirements/install.pip
	pipenv lock -r -d > src/requirements/testing.pip
	sed -i "" 's/\(.*\)==.*/\1/g' src/requirements/install.pip && sed -i "" '1d' src/requirements/install.pip
	sed -i "" 's/\(.*\)==.*/\1/g' src/requirements/testing.pip && sed -i "" '1d' src/requirements/testing.pip


test:
	py.test -v --create-db

qa:
	flake8 src/ tests/
	isort -rc src/ --check-only
	check-manifest


clean:
	rm -fr ${BUILDDIR} dist *.egg-info .coverage coverage.xml .eggs
	find src -name __pycache__ -o -name "*.py?" -o -name "*.orig" -prune | xargs rm -rf
	find tests -name __pycache__ -o -name "*.py?" -o -name "*.orig" -prune | xargs rm -rf
	find src/concurrency/locale -name django.mo | xargs rm -f

fullclean:
	rm -fr .tox .cache
	$(MAKE) clean


docs: .mkbuilddir
	mkdir -p ${BUILDDIR}/docs
	sphinx-build -aE docs/ ${BUILDDIR}/docs
ifdef BROWSE
	firefox ${BUILDDIR}/docs/index.html
endif
