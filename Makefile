PEP8_IGNORE := E221,E241,E261

default:
	@echo "What?"

doc:
	PYTHONPATH=$(shell pwd) make -C docs html

pep8:
	find . -name \*.py -exec pep8 --ignore=$(PEP8_IGNORE) "{}" \;

strip-spaces:
	find . -name \*.py -exec perl -pe 's@ +$$@@' -i "{}" \;
