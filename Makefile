PEP8_IGNORE := E221,E241,E261

default:
	@echo "What?"

pep8:
	find . -name \*.py -exec pep8 --ignore=$(PEP8_IGNORE) "{}" \;

strip-spaces:
	find . -name \*.py -exec perl -pe 's@ +$$@@' -i "{}" \;