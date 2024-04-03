
.PHONY: all
all: pyvenv install-requirements

.PHONY: qai_pdf
qai_pdf:
	./pyvenv/bin/streamlit run ./src/qai_pdf.py

#
# $ . pyvenv/bin/activate
#
pyvenv:
	virtualenv $@
	$@/bin/pip $(PIP_OPTS) install pip --upgrade


.PHONY: install-requirements
install-requirements: pyvenv
	$</bin/pip $(PIP_OPTS) install -r ./requirements.txt
	touch $@


.PHONY: clean
clean:
	rm -rf pyvenv* __pycache__
	rm -f install-requirements
