
.PHONY: all
all: pyvenv install-requirements

.PHONY: qai_pdf
qai_pdf:
	./pyvenv/bin/streamlit run ./src/qai_pdf.py

.PHONY: qai qpic qairole qassist qask
qai:
	./pyvenv/bin/python3 ./src/qai.py

qpic:
	./pyvenv/bin/python3 ./src/qpic.py

qairole:
	./pyvenv/bin/python3 ./src/qairole.py

qassist:
	./pyvenv/bin/python3 ./src/qassist.py

qask:
	./pyvenv/bin/python3 ./src/qask.py

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
